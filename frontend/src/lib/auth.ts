import { api, ApiError } from './api';
import { ambilPeran, ambilToken, simpanSesi, type Peran } from './sesi';

interface HasilLogin {
  token: string;
}

// Backend belum punya /me dan token hanya berisi id. Peran diketahui dengan mencoba
// satu endpoint Admin: 200 berarti Admin, 403 berarti Mahasiswa.
async function tentukanPeran(): Promise<Peran> {
  try {
    await api('/admin/profile-versions');
    return 'admin';
  } catch (e) {
    if (e instanceof ApiError && e.status === 403) return 'mahasiswa';
    throw e;
  }
}

export async function masuk(email: string, password: string): Promise<Peran> {
  const { token } = await api<HasilLogin>('/auth/login', {
    json: { email, password },
    tanpaToken: true,
  });
  simpanSesi(token, 'mahasiswa'); // sementara, agar panggilan berikutnya membawa token
  const peran = await tentukanPeran();
  simpanSesi(token, peran);
  return peran;
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
    location.replace('/rekomendasi/');
    return false;
  }
  return true;
}
