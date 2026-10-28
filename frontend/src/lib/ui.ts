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
export const persen = (n: number) => fPersen.format(n);

export function tanggal(iso: string): string {
  // SQLite mengembalikan waktu UTC tanpa zona; tambahkan Z agar dibaca sebagai UTC.
  const utc = /[zZ]|[+-]\d\d:?\d\d$/.test(iso) ? iso : `${iso}Z`;
  const d = new Date(utc);
  return Number.isNaN(d.getTime()) ? iso : fTanggal.format(d);
}

/** "lang:Python" menjadi "Python". */
export const namaTeknologi = (kode: string) => kode.split(':').slice(1).join(':') || kode;

export function parameterUrl(nama: string): string | null {
  return new URLSearchParams(location.search).get(nama);
}
