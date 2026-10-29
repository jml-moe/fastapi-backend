import { api } from './api';
import type { VersiRingkas } from './types';

/** Hit@3 pada skenario 3 teknologi, atau null bila belum ada metrik. */
export function hit3(v: VersiRingkas): number | null {
  const nilai = v.metrik?.skenario.find((s) => s.teknologi === 3)?.['Hit@3'];
  return typeof nilai === 'number' ? nilai : null;
}

export async function aktifkanVersi(id: number) {
  await api(`/admin/profile-versions/${id}/activate`, { method: 'POST' });
}
