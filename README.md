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
2. `POST /admin/datasets` — unggah dataset `.xlsx`/`.csv`. Pemrosesan ±45 detik di latar belakang.
3. `GET /admin/profile-versions/{id}` sampai `status: ready`; lihat tabel penyaringan, parameter beserta alasannya, dan Hit@3.
4. `POST /admin/profile-versions/{id}/activate`.
5. `POST /auth/register` lalu `POST /auth/login` sebagai Mahasiswa (ganti token di panel Authentication).
6. `GET /technologies` untuk kode teknologi, lalu `POST /recommendations` dengan minimal 3, mis.
   `{"teknologi": ["lang:Python", "lang:SQL", "db:PostgreSQL"]}`.
7. `GET /recommendations` (riwayat) dan `GET /recommendations/{id}` (detail).

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

Halaman tamu: `/` beranda, `/masuk/`, `/daftar/`. Mahasiswa: `/rekomendasi/` (pilih teknologi),
`/hasil/?id=`, `/riwayat/`. Admin: `/kelola/` (Overview), `/kelola/unggah/`, `/kelola/versi/` dan
`/kelola/versi/detail/?id=`. Semua panggilan API lewat satu fungsi di `frontend/src/lib/api.ts`; bentuk
respons yang dibaca ada di `frontend/src/lib/types.ts`. Kerangka sidebar ada di
`frontend/src/layouts/Aplikasi.astro` dan menu per peran di `frontend/src/lib/shell.ts`.
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
