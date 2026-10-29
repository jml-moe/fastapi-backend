type Anak = Node | string | null | undefined | false;

/** Pembuat elemen kecil; semua teks lewat textContent sehingga aman dari injeksi HTML. */
export function el<K extends keyof HTMLElementTagNameMap>(
  tag: K,
  atribut: Record<string, string | boolean | undefined> = {},
  ...anak: Anak[]
): HTMLElementTagNameMap[K] {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(atribut)) {
    if (v === undefined || v === false) continue;
    e.setAttribute(k, v === true ? '' : v);
  }
  for (const a of anak) if (a) e.append(a);
  return e;
}

export function $<T extends HTMLElement = HTMLElement>(selektor: string, akar: ParentNode = document): T {
  const e = akar.querySelector<T>(selektor);
  if (!e) throw new Error(`Elemen tidak ditemukan: ${selektor}`);
  return e;
}

/** Tampilkan satu keadaan (memuat, galat, kosong, siap); sisanya disembunyikan. */
export function tampilkan(akar: HTMLElement, keadaan: string) {
  akar.querySelectorAll<HTMLElement>('[data-keadaan]').forEach((e) => {
    e.hidden = e.dataset.keadaan !== keadaan;
  });
}

const fAngka = new Intl.NumberFormat('id-ID', { maximumFractionDigits: 3 });
const fPersen = new Intl.NumberFormat('id-ID', { style: 'percent', maximumFractionDigits: 1 });
const fTanggal = new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium', timeStyle: 'short' });

export const angka = (n: number) => fAngka.format(n);
const fDua = new Intl.NumberFormat('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
/** Dua desimal tetap, untuk kolom angka sejajar seperti bobot IDF. */
export const dua = (n: number) => fDua.format(n);
export const persen = (n: number) => fPersen.format(n);

export function tanggal(iso: string): string {
  // SQLite mengembalikan waktu UTC tanpa zona; tambahkan Z agar dibaca sebagai UTC.
  const utc = /[zZ]|[+-]\d\d:?\d\d$/.test(iso) ? iso : `${iso}Z`;
  const d = new Date(utc);
  return Number.isNaN(d.getTime()) ? iso : fTanggal.format(d);
}

/** Inisial dua huruf dari nama untuk avatar. */
export function inisial(nama: string): string {
  const bagian = nama.trim().split(/\s+/).filter(Boolean);
  if (bagian.length === 0) return '?';
  const huruf = bagian.length === 1 ? bagian[0].slice(0, 2) : bagian[0][0] + bagian[bagian.length - 1][0];
  return huruf.toUpperCase();
}

const LABEL_STATUS = { processing: 'Diproses', ready: 'Siap', failed: 'Gagal' } as const;
const KELAS_STATUS = { processing: 'pil--proses', ready: 'pil--ok', failed: 'pil--galat' } as const;

/** Pil status versi profil; selalu bertulisan, tidak hanya berwarna. */
export function pilStatus(status: keyof typeof LABEL_STATUS, aktif = false): HTMLSpanElement {
  return aktif
    ? el('span', { class: 'pil pil--ok' }, 'Aktif')
    : el('span', { class: `pil ${KELAS_STATUS[status]}` }, LABEL_STATUS[status]);
}

/** "lang:Python" menjadi "Python". */
export const namaTeknologi = (kode: string) => kode.split(':').slice(1).join(':') || kode;

export function parameterUrl(nama: string): string | null {
  return new URLSearchParams(location.search).get(nama);
}
