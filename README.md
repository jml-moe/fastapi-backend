# Backend Sistem Rekomendasi Karier Developer

Backend FastAPI untuk skripsi: merekomendasikan bidang karier developer kepada mahasiswa dengan
Content-Based Filtering (IDF + centroid + cosine similarity) dari Stack Overflow Developer Survey 2025.
Rancangan lengkap ada di Bab III tracker skripsi.

## Menjalankan

```bash
uv sync
cp .env.example .env      # isi SECRET_KEY, ADMIN_PASSWORD
# letakkan dataset di data/survey_results_public_2025.xlsx (tidak disimpan di git)
make dev                  # migrasi database lalu server di :8000
```

Dokumentasi interaktif: <http://localhost:8000/scalar> (atau `/docs`).

## Mencoba di Scalar

1. `POST /auth/login` dengan `ADMIN_EMAIL` / `ADMIN_PASSWORD` dari `.env`; salin `token`, tempel di panel **Authentication** (Bearer).
2. `POST /admin/profile-versions` — unggah dataset `.xlsx`/`.csv` (respons 202 + header `Location`). Pemrosesan ±45 detik di latar belakang.
3. `GET /admin/profile-versions/{id}` sampai `status: ready`; lihat tabel penyaringan, parameter beserta alasannya, dan Hit@3.
4. `PATCH /admin/profile-versions/{id}` dengan `{"is_active": true}` untuk mengaktifkan.
5. `POST /auth/register` lalu `POST /auth/login` sebagai Mahasiswa (ganti token di panel Authentication).
6. `GET /technologies` untuk kode teknologi, lalu `POST /recommendations` dengan minimal 3, mis.
   `{"teknologi": ["lang:Python", "lang:SQL", "db:PostgreSQL"]}`.
7. `GET /recommendations` (riwayat) dan `GET /recommendations/{id}` (detail).

## Endpoint (RESTful)

| Sumber daya | Buat | Baca | Ubah | Hapus |
|---|---|---|---|---|
| Versi profil (Admin) | `POST /admin/profile-versions` (unggah dataset, 202) | `GET /admin/profile-versions`, `GET /admin/profile-versions/{id}` | `PATCH /admin/profile-versions/{id}` `{"is_active": true\|false}` | `DELETE /admin/profile-versions/{id}` (204) |
| Rekomendasi (milik sendiri) | `POST /recommendations` | `GET /recommendations`, `GET /recommendations/{id}` | tidak ada (hasil hitungan) | `DELETE /recommendations/{id}` (204) |

Aturan penghapusan: hapus bersifat permanen. Versi yang **aktif** atau **sedang diproses** tidak bisa dihapus (409).
Riwayat rekomendasi tetap utuh setelah versinya dihapus (`recommendation.version_id` menjadi NULL; hasilnya sudah
tersimpan di riwayat). Mengaktifkan satu versi otomatis menonaktifkan versi lain. Hapus rekomendasi milik orang lain
dijawab 404. Login dan registrasi (`/auth/*`) tetap berbentuk aksi, lazim untuk autentikasi.

## Frontend

Frontend ada di `frontend/` (Astro, build statis, tanpa framework UI tambahan). Hasil build
(`frontend/dist`) disajikan FastAPI dari satu origin, jadi tidak perlu CORS. Butuh Node >= 22.12.
Arah desain ada di `DESIGN.md`; semua token warna, huruf, dan jarak ada di `frontend/src/styles/global.css`.

```bash
make fe-install   # sekali saja
make fe-build     # bangun frontend, lalu buka http://localhost:8000 (make dev)
# pengembangan: dua terminal
make dev          # API di :8000
make fe-dev       # Astro di :4321, panggilan API diteruskan ke :8000
```

Halaman tamu: `/` beranda, `/masuk/`, `/daftar/`. Mahasiswa: `/dashboard/`, `/rekomendasi/` (pilih teknologi),
`/hasil/?id=`, `/rekomendasi/detail/?id=&peringkat=` (dasar perhitungan skor), `/riwayat/`. Admin: `/kelola/`
(Dashboard), `/kelola/unggah/`, `/kelola/versi/` dan `/kelola/versi/detail/?id=`, `/kelola/profil/` (Profil
Bidang Karier). Admin juga bisa memakai halaman Mahasiswa lewat menu Individual. Susunan halaman mengikuti
bagian 3.7 skripsi (Gambar 3.7 sampai 3.15); perbedaan yang disengaja ada di `DESIGN.md`. Semua panggilan API
lewat satu fungsi di `frontend/src/lib/api.ts`; bentuk respons yang dibaca ada di `frontend/src/lib/types.ts`.
Kerangka sidebar ada di `frontend/src/layouts/Aplikasi.astro` dan menu per peran di
`frontend/src/lib/shell.ts`.
Token disimpan di `localStorage` dan dikirim sebagai header Bearer; nama dan peran diambil dari
`GET /auth/me`. Bila `frontend/dist` belum ada, API tetap jalan tanpa frontend.

## Struktur

```
app/ml/           inti metode (numpy/pandas, tanpa FastAPI/DB): params, preprocess, profile, recommend, evaluate, pipeline
app/modules/      auth, admin (dataset & versi profil), profile (simpan/muat model), recommendation
app/models/       tabel: User(role), ProfileVersion, Recommendation
tests/            unit ML, paritas angka skripsi, API ujung ke ujung
```

Semua parameter metode (ambang 151 responden, awal karier 1–5 tahun, dst.) ada di `app/ml/params.py`
beserta alasan dan sumbernya. Jalankan `uv run python -m app.ml.pipeline` untuk mencetak ringkasannya.

## Perintah

`make dev` · `make test` · `make lint` · `make migrate` · `uv run alembic revision --autogenerate -m "pesan"`

Tes paritas dan tes alur lengkap membutuhkan dataset di `data/` (±45 detik); tanpa dataset keduanya dilewati.
