# DESIGN.md

Arah desain untuk frontend (`frontend/`). Bagian "Dari pemilik" ditranskrip dari permintaan pemilik proyek;
bagian "Turunan" disusun agen dari situ dan boleh diubah. Semua token ada di
`frontend/src/styles/global.css`, jadi mengganti arah cukup mengubah satu berkas itu.

## Dari pemilik
- Referensi: dua screenshot dashboard milik pemilik (halaman "Isi Profil Akademik" mahasiswa dan
  "Overview" admin). Tiru gaya tata letaknya: rapi, bersih, enak dipandang. Meniru ini diminta eksplisit.
- Warna utama: monokrom hitam mengikuti referensi (menggantikan pilihan awal biru tua).
- Ikon menu: dipakai, selama relevan.
- Tema: terang saja.
- Struktur: sidebar kiri, kartu di kanan; admin dipisah menjadi Overview, Unggah Dataset, dan Versi Profil.

## Turunan
- Dial: ENERGY 1 / RHYTHM 2 / MOTION 1.
- Kerangka: sidebar putih 15rem dengan garis kanan tipis, konten berlatar abu sangat terang. Di layar
  sempit (< 56rem) sidebar menjadi laci yang dibuka dari bilah atas.
- Kartu: putih, garis 1px, sudut 14px, tanpa bayangan; kepala kartu (judul, subjudul) lalu garis lalu isi.
- Kontrol: sudut 8px, tombol utama hitam pekat, sekunder putih bergaris. Batas input dibuat sedikit lebih
  tegas dari referensi (3,47:1) agar kolom tetap terlihat.
- Huruf: Plus Jakarta Sans variabel, self-host lewat `@fontsource-variable/plus-jakarta-sans`. Kode dan ID
  memakai monospace sistem.
- Warna: kertas `#fafafa`, permukaan `#fff`, tinta `#111318`, redup `#5b6270`, garis `#e7e7ea`. Selain itu
  hanya warna status: hijau (siap, aktif) dan merah (gagal). Kontras teks diperiksa dengan
  `antislop-human/contrast-check.py`; terendah 5,43:1.
- Motif: kode mono gelap kecil pada baris akordeon (LANG, DB, PLAT, WEB), dipakai berulang; ID versi pada
  tabel memakai monospace polos.
- Gerak: transisi warna 0,15 detik pada kontrol, laci sidebar 0,2 detik; mati bila `prefers-reduced-motion`.
- Nama dan logo: tanpa logo. "Rekomendasi Karier" ditulis sebagai teks.
- Konten: hanya yang ada di sistem. Angka pada kartu Overview berasal dari API (versi aktif); tanpa delta,
  tren, atau testimoni.

## Alasan satu baris (R-31)
- Sidebar dan kartu: diminta pemilik, dan aplikasi ini punya dua peran dengan beberapa tugas yang perlu
  mudah ditemukan.
- Hitam pekat: referensi monokrom, sehingga satu-satunya warna lain hanya menandai status.
- Plus Jakarta Sans: karakter huruf pada referensi, bukan pilihan bawaan AI (R-06).
- Label kapital kecil (R-06): hanya untuk label kolom, bidang, dan judul bagian menu, jarak huruf 0,04em;
  memisahkan label dari nilai pada formulir padat.
- Monospace (R-06): hanya untuk kode dan ID; lebar karakter tetap memudahkan membandingkan.
- Ikon (R-04), ditulis sebagai garis sederhana di `frontend/src/lib/ikon.ts`: daftar centang untuk Pilih
  Teknologi (memilih beberapa item), jam untuk Riwayat (waktu lampau), grid untuk Overview (ringkasan
  berpetak), panah ke atas untuk Unggah Dataset (memasukkan berkas), tumpukan untuk Versi Profil (versi
  berlapis), panah bawah untuk membuka akordeon dan menu pengguna.
- Pil status (R-09): fungsional (Diproses, Siap, Aktif, Gagal) dan selalu bertulisan, tidak hanya berwarna.
- Tanpa bayangan (R-12): hierarki dari garis dan jarak, seperti referensi.
- Variasi ritme (R-14): kartu bidang peringkat 1 lebih besar dan berbingkai hitam; kartu Versi Aktif pada
  Overview lebih lebar dari tiga kartu angka lainnya.
- Akordeon: ratusan teknologi dalam empat kelompok terlalu panjang bila dibuka semua; akordeon menjaga
  halaman tetap ringkas dan hitungan "dipilih/total" tetap terlihat.
