// Bentuk respons yang dibaca halaman. Sumber kebenarannya ada di
// app/modules/*/router.py dan app/ml/recommend.py.

export interface Teknologi {
  kode: string;
  nama: string;
}
export type DaftarTeknologi = Record<string, Teknologi[]>;

export interface Sumbangan {
  kode: string;
  sumbangan: number;
}
export interface TeknologiUmum {
  kode: string;
  proporsi: number;
  dipilih: boolean;
}
export interface Peringkat {
  peringkat: number;
  bidang_karier: string;
  skor: number;
  sumbangan?: Sumbangan[];
  teknologi_umum?: TeknologiUmum[];
}
export interface Rekomendasi {
  id: number;
  created_at: string;
  teknologi_dipilih: string[];
  peringkat: Peringkat[];
}
export interface RingkasRiwayat {
  id: number;
  created_at: string;
  teknologi_dipilih: string[];
  top: { bidang_karier: string; skor: number }[];
}

export type StatusVersi = 'processing' | 'ready' | 'failed';

export interface SkenarioMetrik {
  teknologi: number | 'semua';
  n_uji: number;
  [kunci: string]: number | string;
}
export interface Metrik {
  n_uji: number;
  skenario: SkenarioMetrik[];
  baseline_popularitas: Record<string, number>;
}
export interface VersiRingkas {
  id: number;
  filename: string;
  status: StatusVersi;
  is_active: boolean;
  created_at: string;
  n_developer: number | null;
  metrik: Metrik | null;
}
export interface Ringkasan {
  penyaringan: { tahap: string; alasan: string; sisa: number; terbuang: number }[];
  per_bidang: { bidang: string; semua: number; awal_karier: number }[];
  n_developer: number;
  n_teknologi: number;
  metrik: Metrik;
  params: {
    top_k: number;
    penjelasan: { parameter: string; nilai: unknown; sumber: string; alasan: string }[];
  };
}
export interface VersiDetail {
  id: number;
  filename: string;
  status: StatusVersi;
  is_active: boolean;
  error: string | null;
  ringkasan: Ringkasan | null;
}
