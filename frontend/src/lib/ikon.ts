// Ikon garis buatan sendiri (viewBox 24). Setiap ikon dipilih karena relevan dengan menunya:
// daftar-centang = Pilih Teknologi, jam = Riwayat, grid = Overview, unggah = Unggah Dataset,
// tumpukan = Versi Profil, grafik = Profil Bidang Karier (proporsi pemakaian), pengguna = kartu pengguna.
export const IKON = {
  'daftar-centang': ['M10 6h10', 'M10 12h10', 'M10 18h10', 'M3.5 6l1.5 1.5L7.5 4.5', 'M3.5 12l1.5 1.5 2.5-3', 'M3.5 18l1.5 1.5 2.5-3'],
  jam: ['M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z', 'M12 7v5l3 2'],
  grid: ['M4 4h6.5v6.5H4z', 'M13.5 4H20v6.5h-6.5z', 'M4 13.5h6.5V20H4z', 'M13.5 13.5H20V20h-6.5z'],
  unggah: ['M12 16V4', 'M7 9l5-5 5 5', 'M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3'],
  tumpukan: ['M12 3l9 5-9 5-9-5 9-5z', 'M3 12.5l9 5 9-5', 'M3 17l9 5 9-5'],
  pengguna: ['M12 4a4 4 0 1 0 0 8 4 4 0 0 0 0-8z', 'M4 20c0-3.6 3.6-6 8-6s8 2.4 8 6'],
  grafik: ['M4 20h16', 'M7 20v-7', 'M12 20V5', 'M17 20v-10'],
  panah: ['M6 9l6 6 6-6'],
  menu: ['M4 7h16', 'M4 12h16', 'M4 17h16'],
} as const;

export type NamaIkon = keyof typeof IKON;

const NS = 'http://www.w3.org/2000/svg';

/** Elemen SVG untuk dipakai dari skrip (menu, akordeon). */
export function ikon(nama: NamaIkon, kelas = 'ikon'): SVGSVGElement {
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '1.75');
  svg.setAttribute('stroke-linecap', 'round');
  svg.setAttribute('stroke-linejoin', 'round');
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('class', kelas);
  for (const d of IKON[nama]) {
    const path = document.createElementNS(NS, 'path');
    path.setAttribute('d', d);
    svg.append(path);
  }
  return svg;
}
