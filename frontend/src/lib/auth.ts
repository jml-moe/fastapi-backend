import { api } from './api';
import { ambilPeran, ambilToken, simpanProfil, simpanToken, type Peran } from './sesi';

interface HasilLogin {
  token: string;
}
interface Profil {
  name: string;
  role: string;
}

/** Ambil nama dan peran dari backend lalu simpan; dipakai saat login dan untuk sesi lama. */
export async function muatProfil(): Promise<Peran> {
  const saya = await api<Profil>('/auth/me');
  const peran: Peran = saya.role === 'admin' ? 'admin' : 'mahasiswa';
  simpanProfil(peran, saya.name);
  return peran;
}

export async function masuk(email: string, password: string): Promise<Peran> {
  const { token } = await api<HasilLogin>('/auth/login', {
    json: { email, password },
    tanpaToken: true,
  });
  simpanToken(token); // agar /auth/me membawa token
  return muatProfil();
}

export async function daftar(name: string, email: string, password: string) {
  await api('/auth/register', { json: { name, email, password }, tanpaToken: true });
}

/**
 * Pastikan pengguna sudah masuk (dan berperan sesuai). Bila tidak, halaman dialihkan dan
 * fungsi mengembalikan false; halaman tidak boleh melanjutkan memuat data.
 */
export function wajibMasuk(peranDiminta?: Peran): boolean {
  if (!ambilToken()) {
    const lanjut = encodeURIComponent(location.pathname + location.search);
    location.replace(`/masuk/?lanjut=${lanjut}`);
    return false;
  }
  if (peranDiminta && ambilPeran() !== peranDiminta) {
    location.replace('/dashboard/');
    return false;
  }
  return true;
}
