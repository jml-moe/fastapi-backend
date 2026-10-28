"""Registry parameter metode.

Setiap parameter yang memengaruhi hasil didefinisikan di sini beserta alasan dan sumbernya
(kode K merujuk register keputusan di tab "Audit dan Eksperimen" pada tracker). Tidak ada angka
ajaib di modul lain: semua modul menerima ``Params`` lewat argumen.
"""

import math
from dataclasses import dataclass, field

# K1 - peran yang dibuang pada langkah 4 penyaringan, masing-masing dengan alasannya
PERAN_DIBUANG = {
    "Architect, software or solutions": "Peran senior: median 18 tahun, 6% awal karier",
    "Engineering manager": "Manajerial",
    "Senior executive (C-suite, VP, etc.)": "Manajerial",
    "Founder, technology or otherwise": "Manajerial",
    "Project manager": "Manajerial",
    "Product manager": "Manajerial",
    "Academic researcher": "Bukan pekerjaan developer",
    "Financial analyst or engineer": "Bukan pekerjaan developer",
    "Student": "Bukan jenis pekerjaan",
    "Retired": "Bukan jenis pekerjaan",
    "Other (please specify):": "Tidak dapat dikelompokkan",
}

# K12 - package manager dan build tool: bukan keterampilan yang dipelajari tersendiri
PACKAGE_MANAGER = (
    "APT", "Bun", "Cargo", "Chocolatey", "Composer", "Gradle", "Homebrew",
    "MSBuild", "Make", "Maven (build tool)", "Ninja", "NuGet", "Pacman",
    "Pip", "Poetry", "Vite", "Webpack", "Yarn", "npm", "pnpm",
)  # fmt: skip


def ukuran_sampel(z: float, p: float, e: float) -> int:
    """Ukuran sampel minimum untuk menaksir proporsi (Cochran, 1977): n = z^2 p (1-p) / e^2."""
    return math.ceil(z**2 * p * (1 - p) / e**2)


@dataclass(frozen=True)
class Params:
    # K2 - ambang responden per bidang (Cochran, 1977)
    z: float = 1.96  # tingkat kepercayaan 95%
    p: float = 0.5  # proporsi tak diketahui -> 0,5 memberi varians terbesar (paling konservatif)
    e: float = 0.08  # galat yang ditoleransi (pilihan peneliti)
    # K3 - developer awal karier: pengalaman kerja 1-5 tahun (pengelompokan Stack Overflow 2025)
    awal_karier: tuple[int, int] = (1, 5)
    # K7 - minimal teknologi yang dipilih Mahasiswa (usul 5 menunggu dosen)
    min_teknologi: int = 3
    top_k: int = 3
    # Evaluasi (Bab III 3.2): stratified k-fold, simulasi jumlah teknologi yang dipilih
    k_fold: int = 5
    seed: int = 0
    skenario_teknologi: tuple[int | None, ...] = (3, 5, 8, None)  # None = semua teknologi
    # K6 - gabung Cloud infrastructure engineer ke DevOps (menunggu dosen)
    gabung_cloud_devops: bool = False
    # K16 (IDF terhaluskan) dan K17 (tanpa normalisasi vektor developer) bersifat tetap pada
    # implementasi; dicatat di snapshot agar terlihat oleh Admin.
    peran_dibuang: dict[str, str] = field(default_factory=lambda: dict(PERAN_DIBUANG))
    teknologi_dikecualikan_umum: tuple[str, ...] = tuple("plat:" + t for t in PACKAGE_MANAGER)

    @property
    def n_min(self) -> int:
        return ukuran_sampel(self.z, self.p, self.e)

    def penjelasan(self) -> list[dict]:
        """Daftar parameter beserta nilai, alasan, dan sumbernya untuk ditampilkan ke Admin."""
        return [
            {
                "parameter": "n_min",
                "nilai": self.n_min,
                "sumber": "K2; Cochran (1977)",
                "alasan": f"ceil(z^2 p(1-p) / e^2) dengan z={self.z}, p={self.p}, e={self.e}; "
                "bidang di bawah ambang dibuang agar proporsi pemakaian stabil",
            },
            {
                "parameter": "awal_karier",
                "nilai": list(self.awal_karier),
                "sumber": "K3; Stack Overflow (2025)",
                "alasan": "Pengalaman kerja 1-5 tahun = awal karier; dipakai sebagai data uji",
            },
            {
                "parameter": "min_teknologi",
                "nilai": self.min_teknologi,
                "sumber": "K7",
                "alasan": "Hit@3 naik bertahap tanpa titik lonjakan (3: 0,613; 5: 0,655; 8: 0,702)",
            },
            {
                "parameter": "top_k",
                "nilai": self.top_k,
                "sumber": "Rumusan masalah",
                "alasan": "Hit@3",
            },
            {
                "parameter": "k_fold",
                "nilai": self.k_fold,
                "sumber": "Bab III 3.2; Kohavi (1995)",
                "alasan": "Stratified k-fold pada developer awal karier",
            },
            {
                "parameter": "seed",
                "nilai": self.seed,
                "sumber": "Reproduksibilitas",
                "alasan": "Pembagian fold dan simulasi teknologi dapat diulang",
            },
            {
                "parameter": "skenario_teknologi",
                "nilai": list(self.skenario_teknologi),
                "sumber": "K7",
                "alasan": "Mahasiswa diperkirakan menguasai lebih sedikit teknologi daripada developer",
            },
            {
                "parameter": "gabung_cloud_devops",
                "nilai": self.gabung_cloud_devops,
                "sumber": "K6",
                "alasan": "Menunggu keputusan dosen; cosine profil keduanya 0,977",
            },
            {
                "parameter": "peran_dibuang",
                "nilai": self.peran_dibuang,
                "sumber": "K1",
                "alasan": "Setiap peran dibuang dengan alasan tercatat",
            },
            {
                "parameter": "idf",
                "nilai": "ln((1+N)/(1+df)) + 1",
                "sumber": "K16; scikit-learn smooth_idf=True",
                "alasan": "Peringkat identik dengan varian lain pada 4 skenario",
            },
            {
                "parameter": "normalisasi_vektor",
                "nilai": False,
                "sumber": "K17",
                "alasan": "Selisih Hit@3 dengan normalisasi maksimum 0,006",
            },
        ]

    def snapshot(self) -> dict:
        return {
            "n_min": self.n_min,
            "z": self.z,
            "p": self.p,
            "e": self.e,
            "awal_karier": list(self.awal_karier),
            "min_teknologi": self.min_teknologi,
            "top_k": self.top_k,
            "k_fold": self.k_fold,
            "seed": self.seed,
            "skenario_teknologi": list(self.skenario_teknologi),
            "gabung_cloud_devops": self.gabung_cloud_devops,
            "peran_dibuang": self.peran_dibuang,
            "penjelasan": self.penjelasan(),
        }
