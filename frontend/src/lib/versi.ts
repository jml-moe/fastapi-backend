import { api } from './api';
import type { VersiRingkas } from './types';

/** Macro-Hit@3 pada skenario 3 teknologi, atau null bila belum ada metrik. */
export function macroHit3(v: VersiRingkas): number | null {
  const nilai = v.metrik?.skenario.find((s) => s.teknologi === 3)?.['macro-Hit@3'];
  return typeof nilai === 'number' ? nilai : null;
}

export async function aktifkanVersi(id: number) {
  await api(`/admin/profile-versions/${id}/activate`, { method: 'POST' });
}
