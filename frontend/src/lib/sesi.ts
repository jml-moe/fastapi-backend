// Token dan peran disimpan di localStorage. Akses dibungkus try/catch karena
// penyimpanan bisa diblokir (mode privat, kebijakan peramban).
export type Peran = 'admin' | 'mahasiswa';

const KUNCI_TOKEN = 'karier.token';
const KUNCI_PERAN = 'karier.peran';

function baca(kunci: string): string | null {
  try {
    return localStorage.getItem(kunci);
  } catch {
    return null;
  }
}

export const ambilToken = () => baca(KUNCI_TOKEN);

export function ambilPeran(): Peran | null {
  const peran = baca(KUNCI_PERAN);
  return peran === 'admin' || peran === 'mahasiswa' ? peran : null;
}

export function simpanSesi(token: string, peran: Peran) {
  try {
    localStorage.setItem(KUNCI_TOKEN, token);
    localStorage.setItem(KUNCI_PERAN, peran);
  } catch {
    /* tanpa penyimpanan, pengguna harus masuk ulang setiap halaman */
  }
}

export function hapusSesi() {
  try {
    localStorage.removeItem(KUNCI_TOKEN);
    localStorage.removeItem(KUNCI_PERAN);
  } catch {
    /* tidak ada yang perlu dihapus */
  }
}
