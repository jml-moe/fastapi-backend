# DESIGN.md

Arah desain untuk frontend (`frontend/`). Bagian "Dari pemilik" ditranskrip dari jawaban pemilik proyek;
bagian "Turunan" disusun agen dari jawaban itu dan boleh diubah. Semua token ada di
`frontend/src/styles/global.css`, jadi mengganti arah cukup mengubah satu berkas itu.

## Dari pemilik
- Kesan: tenang dan akademik. Terang, banyak ruang kosong, huruf serif untuk judul, satu warna aksen kalem.
- Warna aksen: biru tua.
- Tema: terang saja.

## Turunan
- Dial: ENERGY 1 / RHYTHM 2 / MOTION 1
- Tipografi: judul memakai serif sistem (Iowan Old Style, Palatino, Georgia); isi memakai sans-serif sistem.
  Tanpa font eksternal agar tidak ada permintaan jaringan tambahan.
- Warna: latar putih gading, teks arang kebiruan, aksen biru tua `#1e3a8a`; merah dan hijau hanya untuk
  status galat dan sukses. Kontras teks diperiksa dengan `antislop-human/contrast-check.py`.
- Motif: garis aksen tipis di sisi kiri judul bagian, seperti catatan tepi pada makalah.
- Gerak: hanya transisi warna pendek pada tautan dan tombol; mati bila `prefers-reduced-motion`.
- Nama dan logo: tidak ada logo. Nama produk ditulis sebagai teks, mengikuti judul API:
  "Rekomendasi Karier Developer".
- Konten: hanya yang benar-benar ada di sistem. Tidak ada testimoni, statistik, atau klaim performa.
