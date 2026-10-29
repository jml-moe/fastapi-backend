import { api } from './api';
import { konfirmasi } from './konfirmasi';
import type { StatusVersi, VersiRingkas } from './types';

/** Macro-Hit@3 pada skenario 3 teknologi, atau null bila belum ada metrik. */
export function macroHit3(v: VersiRingkas): number | null {
  const nilai = v.metrik?.skenario.find((s) => s.teknologi === 3)?.['macro-Hit@3'];
  return typeof nilai === 'number' ? nilai : null;
}

interface Versi {
  id: number;
  filename: string;
  status: StatusVersi;
  is_active: boolean;
}

/** Sama dengan aturan backend: versi aktif dan yang sedang diproses tidak bisa dihapus. */
export const bisaDihapus = (v: Pick<Versi, 'status' | 'is_active'>) => !v.is_active && v.status !== 'processing';

export async function aktifkanVersi(id: number) {
  await api(`/admin/profile-versions/${id}`, { method: 'PATCH', json: { is_active: true } });
}

/** Minta konfirmasi lalu nonaktifkan; true bila jadi dilakukan. */
export async function nonaktifkanVersi(v: Pick<Versi, 'id'>): Promise<boolean> {
  const lanjut = await konfirmasi({
    judul: `Nonaktifkan versi ${v.id}?`,
    pesan: 'Selama tidak ada versi aktif, Mahasiswa belum bisa meminta rekomendasi. Anda bisa mengaktifkannya lagi kapan saja.',
    aksi: 'Nonaktifkan',
  });
  if (lanjut) await api(`/admin/profile-versions/${v.id}`, { method: 'PATCH', json: { is_active: false } });
  return lanjut;
}

/** Minta konfirmasi lalu hapus permanen; true bila jadi dilakukan. */
export async function hapusVersi(v: Pick<Versi, 'id' | 'filename'>): Promise<boolean> {
  const lanjut = await konfirmasi({
    judul: `Hapus versi ${v.id}?`,
    pesan: `Profil dari berkas "${v.filename}" dihapus permanen dan tidak bisa dikembalikan; dataset harus diunggah ulang bila dibutuhkan. Riwayat rekomendasi Mahasiswa yang memakai versi ini tetap tersimpan.`,
    aksi: 'Hapus',
    bahaya: true,
  });
  if (lanjut) await api(`/admin/profile-versions/${v.id}`, { method: 'DELETE' });
  return lanjut;
}
