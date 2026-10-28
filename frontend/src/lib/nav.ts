import { ambilPeran, ambilToken, hapusSesi } from './sesi';
import { el } from './ui';

interface Tautan {
  href: string;
  label: string;
}

const MAHASISWA: Tautan[] = [
  { href: '/rekomendasi/', label: 'Rekomendasi' },
  { href: '/riwayat/', label: 'Riwayat' },
];
const TAMU: Tautan[] = [
  { href: '/masuk/', label: 'Masuk' },
  { href: '/daftar/', label: 'Buat akun' },
];

export function pasangNavigasi() {
  const nav = document.getElementById('navigasi');
  if (!nav) return;

  const masuk = Boolean(ambilToken());
  const tautan = masuk
    ? [...MAHASISWA, ...(ambilPeran() === 'admin' ? [{ href: '/kelola/', label: 'Kelola dataset' }] : [])]
    : TAMU;

  const daftar = el('ul', { class: 'nav__daftar' });
  for (const t of tautan) {
    const aktif = location.pathname.startsWith(t.href);
    daftar.append(
      el('li', {}, el('a', { class: 'nav__tautan', href: t.href, 'aria-current': aktif ? 'page' : undefined }, t.label)),
    );
  }
  if (masuk) {
    const keluar = el('button', { type: 'button', class: 'nav__tautan nav__keluar' }, 'Keluar');
    keluar.addEventListener('click', () => {
      hapusSesi();
      location.assign('/masuk/');
    });
    daftar.append(el('li', {}, keluar));
  }
  nav.replaceChildren(daftar);
}
