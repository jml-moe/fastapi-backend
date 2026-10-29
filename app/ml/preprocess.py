"""Praproses dataset survei (Bab III 3.2, langkah A1-A3). Port dari Notebook 1."""

from dataclasses import dataclass

import pandas as pd

from app.ml.params import Params

KOLOM_FILTER = ["MainBranch", "Employment", "DevType", "WorkExp"]
KOLOM_TEKNOLOGI = {
    "lang": "LanguageHaveWorkedWith",
    "db": "DatabaseHaveWorkedWith",
    "plat": "PlatformHaveWorkedWith",
    "web": "WebframeHaveWorkedWith",
}
KOLOM_WAJIB = ["ResponseId", *KOLOM_FILTER, *KOLOM_TEKNOLOGI.values()]
NAMA_KELOMPOK = {
    "lang": "Bahasa pemrograman",
    "db": "Basis data",
    "plat": "Platform dan tools",
    "web": "Framework web",
}


@dataclass
class DataFinal:
    X: pd.DataFrame  # matriks biner developer x teknologi (kolom "kelompok:nama")
    label: pd.Series  # bidang karier per developer
    awal: pd.Series  # True bila developer awal karier
    log: list[dict]  # tabel penyaringan (tahap, alasan, sisa, terbuang)
    per_bidang: pd.DataFrame  # jumlah developer semua dan awal karier per bidang
    id_responden: pd.Series  # ResponseId, sejajar dengan baris X (untuk pratinjau data)


class KolomTidakLengkap(ValueError):
    def __init__(self, hilang: list[str]):
        super().__init__(f"Kolom wajib tidak ditemukan: {hilang}")
        self.hilang = hilang


def muat_dataset(path: str) -> pd.DataFrame:
    """Baca .csv atau .xlsx, hanya kolom yang dipakai."""
    if path.lower().endswith(".csv"):
        return pd.read_csv(path, usecols=lambda c: c in KOLOM_WAJIB)
    return pd.read_excel(path, usecols=lambda c: c in KOLOM_WAJIB)


def periksa_kolom(df: pd.DataFrame) -> list[str]:
    return [c for c in KOLOM_WAJIB if c not in df.columns]


def saring(df: pd.DataFrame, params: Params) -> tuple[pd.DataFrame, list[dict]]:
    """Enam langkah penyaringan (Tabel 3.4); setiap langkah dicatat beserta alasannya."""
    hilang = periksa_kolom(df)
    if hilang:
        raise KolomTidakLengkap(hilang)

    data = df[KOLOM_WAJIB].copy()
    log = [{"tahap": "Data awal", "alasan": "-", "sisa": len(data)}]

    def catat(tahap: str, alasan: str):
        log.append({"tahap": tahap, "alasan": alasan, "sisa": len(data)})

    data = data[data["MainBranch"] == "I am a developer by profession"]
    catat("Developer profesional", "Profil harus berasal dari orang yang bekerja sebagai developer")
    data = data[data["Employment"] == "Employed"]
    catat("Berstatus bekerja", "Teknologi yang dipakai harus mencerminkan pekerjaan yang dijalani")
    data = data[data["DevType"].notna()]
    catat("DevType terisi", "Tanpa jenis pekerjaan, responden tidak bisa dikelompokkan ke bidang")
    data = data[~data["DevType"].isin(params.peran_dibuang)]
    catat("Bukan peran nonteknis, manajerial, atau senior", "K1; alasan per peran pada parameter")
    data = data[data["LanguageHaveWorkedWith"].notna()]
    catat("Bahasa pemrograman terisi", "Tanpa data teknologi, profil tidak bisa dibentuk")

    data = data.copy()
    if params.gabung_cloud_devops:  # K6
        data["DevType"] = data["DevType"].replace(
            {"Cloud infrastructure engineer": "DevOps engineer or professional"}
        )
    jumlah = data["DevType"].value_counts()
    data = data[data["DevType"].isin(jumlah[jumlah >= params.n_min].index)]
    catat(
        f"Bidang dengan >= {params.n_min} responden",
        "K2; Cochran (1977), presisi proporsi ±" + str(params.e),
    )

    sebelumnya = None
    for baris in log:
        baris["terbuang"] = 0 if sebelumnya is None else sebelumnya - baris["sisa"]
        sebelumnya = baris["sisa"]
    return data, log


def encode(data: pd.DataFrame) -> pd.DataFrame:
    """Vektor biner (Pers. 2.1); awalan kelompok memisahkan nama yang sama di kelompok berbeda."""
    bagian = [
        data[kolom].str.get_dummies(sep=";").add_prefix(f"{awalan}:")
        for awalan, kolom in KOLOM_TEKNOLOGI.items()
    ]
    return pd.concat(bagian, axis=1).astype("int8")


def bangun_data_final(df: pd.DataFrame, params: Params) -> DataFinal:
    data, log = saring(df, params)
    awal_min, awal_maks = params.awal_karier
    awal = (
        data["WorkExp"].between(awal_min, awal_maks).reset_index(drop=True)
    )  # WorkExp kosong -> False
    X = encode(data).reset_index(drop=True)
    label = data["DevType"].reset_index(drop=True).rename("bidang_karier")
    id_responden = data["ResponseId"].reset_index(drop=True)
    per_bidang = (
        pd.DataFrame({"bidang": label, "awal_karier": awal})
        .groupby("bidang")
        .agg(semua=("awal_karier", "size"), awal_karier=("awal_karier", "sum"))
        .sort_values("semua", ascending=False)
    )
    return DataFinal(
        X=X, label=label, awal=awal, log=log, per_bidang=per_bidang, id_responden=id_responden
    )


def daftar_teknologi(X: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "kode": X.columns,
            "kelompok": X.columns.str.split(":").str[0],
            "teknologi": X.columns.str.split(":", n=1).str[1],
            "jumlah_pemakai": X.sum().to_numpy(),
        }
    )
