import { muatProfil } from './auth';
import { ikon, type NamaIkon } from './ikon';
import { ambilNama, ambilPeran, ambilToken, hapusSesi, type Peran } from './sesi';
import { $, el, inisial } from './ui';

interface Butir {
  href: string;
  label: string;
  ikon: NamaIkon;
  cocok: (jalur: string) => boolean;
}
interface Bagian {
  judul: string;
  butir: Butir[];
}

const DASHBOARD_MHS: Butir = { href: '/dashboard/', label: 'Dashboard', ikon: 'grid', cocok: (p) => p.startsWith('/dashboard/') };
// Hasil dan detail rekomendasi adalah bagian dari alur Rekomendasi (struktur menu 3.6.2).
const REKOMENDASI: Butir = { href: '/rekomendasi/', label: 'Rekomendasi', ikon: 'daftar-centang', cocok: (p) => p.startsWith('/rekomendasi/') || p.startsWith('/hasil/') };
const RIWAYAT: Butir = { href: '/riwayat/', label: 'Riwayat', ikon: 'jam', cocok: (p) => p.startsWith('/riwayat/') };

const MENU: Record<Peran, Bagian[]> = {
  mahasiswa: [{ judul: 'Menu', butir: [DASHBOARD_MHS, REKOMENDASI, RIWAYAT] }],
  admin: [
    {
      judul: 'Dashboard',
      butir: [
        { href: '/kelola/', label: 'Dashboard', ikon: 'grid', cocok: (p) => p === '/kelola/' },
        { href: '/kelola/unggah/', label: 'Unggah Dataset', ikon: 'unggah', cocok: (p) => p.startsWith('/kelola/unggah/') },
        { href: '/kelola/versi/', label: 'Versi Profil', ikon: 'tumpukan', cocok: (p) => p.startsWith('/kelola/versi/') },
        { href: '/kelola/profil/', label: 'Profil Bidang Karier', ikon: 'grafik', cocok: (p) => p.startsWith('/kelola/profil/') },
      ],
    },
    { judul: 'Individual', butir: [REKOMENDASI, RIWAYAT] },
  ],
};

const LABEL_PERAN: Record<Peran, string> = { mahasiswa: 'Mahasiswa', admin: 'Admin' };

function gambarMenu(peran: Peran) {
  const jalur = location.pathname;
  const akar = $('#menu-samping');
  akar.replaceChildren(
    ...MENU[peran].map((bagian, i) => {
      const idJudul = `nav-judul-${i}`;
      const daftar = el('ul', { class: 'nav-daftar', 'aria-labelledby': idJudul });
      for (const b of bagian.butir) {
        daftar.append(
          el(
            'li',
            {},
            el('a', { class: 'nav-item', href: b.href, 'aria-current': b.cocok(jalur) ? 'page' : undefined }, ikon(b.ikon), b.label),
          ),
        );
      }
      return el('div', { class: 'nav-bagian' }, el('p', { class: 'nav-judul', id: idJudul }, bagian.judul), daftar);
    }),
  );
}

function gambarPengguna(peran: Peran, nama: string) {
  const tombol = el(
    'button',
    { type: 'button', class: 'pengguna', id: 'tombol-pengguna', 'aria-expanded': 'false', 'aria-controls': 'menu-pengguna', 'aria-haspopup': 'true' },
    el('span', { class: 'avatar', 'aria-hidden': 'true' }, inisial(nama)),
    el('span', { class: 'pengguna__teks' }, el('span', { class: 'pengguna__nama' }, nama), el('span', { class: 'pengguna__peran' }, LABEL_PERAN[peran])),
    ikon('panah'),
  );
  const keluar = el('button', { type: 'button' }, 'Keluar');
  const menu = el('div', { class: 'menu-pengguna', id: 'menu-pengguna', hidden: true }, keluar);

  const tutup = () => {
    menu.hidden = true;
    tombol.setAttribute('aria-expanded', 'false');
  };
  tombol.addEventListener('click', () => {
    menu.hidden = !menu.hidden;
    tombol.setAttribute('aria-expanded', String(!menu.hidden));
  });
  keluar.addEventListener('click', () => {
    hapusSesi();
    location.assign('/masuk/');
  });
  document.addEventListener('click', (e) => {
    if (!menu.hidden && !(e.target as Element).closest('.sidebar__bawah')) tutup();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !menu.hidden) {
      tutup();
      tombol.focus();
    }
  });
  $('#bawah-sidebar').replaceChildren(menu, tombol);
}

/** Laci sidebar untuk layar sempit: tombol di bilah atas, tirai, Escape, fokus masuk dan kembali. */
function pasangLaci() {
  const sidebar = $('#sidebar');
  const utama = $('#app-utama');
  const buka = $<HTMLButtonElement>('#buka-menu');
  const lebar = window.matchMedia('(min-width: 56.01rem)');

  const ubah = (terbuka: boolean) => {
    sidebar.toggleAttribute('data-buka', terbuka);
    buka.setAttribute('aria-expanded', String(terbuka));
    utama.toggleAttribute('inert', terbuka); // isi di belakang tirai tak bisa difokus
    if (terbuka) sidebar.querySelector<HTMLElement>('.nav-item')?.focus();
    else buka.focus();
  };

  buka.addEventListener('click', () => ubah(!sidebar.hasAttribute('data-buka')));
  $('#tirai').addEventListener('click', () => ubah(false));
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar.hasAttribute('data-buka')) ubah(false);
  });
  lebar.addEventListener('change', () => {
    if (lebar.matches && sidebar.hasAttribute('data-buka')) {
      sidebar.removeAttribute('data-buka');
      utama.removeAttribute('inert');
      buka.setAttribute('aria-expanded', 'false');
    }
  });
}

export async function pasangShell() {
  pasangLaci();
  if (!ambilToken()) return; // halaman memanggil wajibMasuk() dan mengalihkan ke /masuk/

  // Sesi dari versi lama belum punya nama; ambil sekali dari /auth/me.
  let peran = ambilPeran();
  let nama = ambilNama();
  if (!peran || !nama) {
    try {
      peran = await muatProfil();
      nama = ambilNama();
    } catch {
      return; // 401 sudah ditangani api(); galat lain tidak boleh merusak halaman
    }
  }
  gambarMenu(peran);
  gambarPengguna(peran, nama ?? LABEL_PERAN[peran]);
}
