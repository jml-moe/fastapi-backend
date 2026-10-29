import { el } from './ui';

interface Opsi {
  judul: string;
  pesan: string;
  aksi: string;
  /** Aksi yang tak bisa dibatalkan (hapus); tombolnya berwarna galat. */
  bahaya?: boolean;
}

/**
 * Dialog konfirmasi berbasis <dialog> native: Escape, klik di luar, atau Batal menutup tanpa aksi;
 * fokus awal di Batal (pilihan aman) dan kembali ke pemicu setelah tertutup. Hasilnya true bila aksi dipilih.
 */
export function konfirmasi(opsi: Opsi): Promise<boolean> {
  return new Promise((selesai) => {
    const pemicu = document.activeElement as HTMLElement | null;
    const batal = el('button', { type: 'submit', class: 'tombol tombol--sekunder', value: 'batal' }, 'Batal');
    const ya = el('button', { type: 'submit', class: opsi.bahaya ? 'tombol tombol--bahaya' : 'tombol', value: 'ya' }, opsi.aksi);
    const dialog = el(
      'dialog',
      { class: 'dialog', 'aria-labelledby': 'dialog-judul', 'aria-describedby': 'dialog-pesan' },
      el('div', { class: 'dialog__isi' }, el('h2', { id: 'dialog-judul' }, opsi.judul), el('p', { id: 'dialog-pesan' }, opsi.pesan)),
      el('form', { method: 'dialog', class: 'dialog__aksi' }, batal, ya),
    );
    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) dialog.close('batal');
    });
    dialog.addEventListener('close', () => {
      dialog.remove();
      pemicu?.focus();
      selesai(dialog.returnValue === 'ya');
    });
    document.body.append(dialog);
    dialog.showModal();
    batal.focus();
  });
}
