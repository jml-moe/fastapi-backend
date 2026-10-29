// Token, peran, dan nama disimpan di localStorage. Akses dibungkus try/catch karena
// penyimpanan bisa diblokir (mode privat, kebijakan peramban).
export type Peran = 'admin' | 'mahasiswa';

const KUNCI_TOKEN = 'karier.token';
const KUNCI_PERAN = 'karier.peran';
const KUNCI_NAMA = 'karier.nama';

function baca(kunci: string): string | null {
  try {
    return localStorage.getItem(kunci);
  } catch {
    return null;
  }
}

function tulis(kunci: string, nilai: string) {
  try {
    localStorage.setItem(kunci, nilai);
  } catch {
    /* tanpa penyimpanan, pengguna harus masuk ulang setiap halaman */
  }
}

export const ambilToken = () => baca(KUNCI_TOKEN);
export const ambilNama = () => baca(KUNCI_NAMA);

export function ambilPeran(): Peran | null {
  const peran = baca(KUNCI_PERAN);
  return peran === 'admin' || peran === 'mahasiswa' ? peran : null;
}

export function simpanToken(token: string) {
  tulis(KUNCI_TOKEN, token);
}

export function simpanProfil(peran: Peran, nama: string) {
  tulis(KUNCI_PERAN, peran);
  tulis(KUNCI_NAMA, nama);
}

export function hapusSesi() {
  try {
    localStorage.removeItem(KUNCI_TOKEN);
    localStorage.removeItem(KUNCI_PERAN);
    localStorage.removeItem(KUNCI_NAMA);
  } catch {
    /* tidak ada yang perlu dihapus */
  }
}
