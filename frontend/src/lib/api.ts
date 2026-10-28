import { ambilToken, hapusSesi } from './sesi';

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

interface Opsi {
  method?: string;
  json?: unknown;
  form?: FormData;
  /** Untuk login/registrasi: jangan kirim token dan jangan alihkan saat 401. */
  tanpaToken?: boolean;
}

// FastAPI mengirim `detail` berupa teks, daftar teks (validasi rekomendasi),
// atau daftar objek `{msg}` (validasi Pydantic).
function pesanGalat(data: unknown): string | null {
  const detail = (data as { detail?: unknown } | null)?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === 'string' ? d : ((d as { msg?: string }).msg ?? '')))
      .filter(Boolean)
      .join(' ');
  }
  return null;
}

/** Satu-satunya pintu panggilan ke backend. */
export async function api<T>(path: string, opsi: Opsi = {}): Promise<T> {
  const headers = new Headers();
  const token = opsi.tanpaToken ? null : ambilToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);

  let body: BodyInit | undefined;
  if (opsi.json !== undefined) {
    headers.set('Content-Type', 'application/json');
    body = JSON.stringify(opsi.json);
  } else if (opsi.form) {
    body = opsi.form;
  }

  let res: Response;
  try {
    res = await fetch(path, { method: opsi.method ?? (body ? 'POST' : 'GET'), headers, body });
  } catch {
    throw new ApiError(0, 'Server tidak dapat dihubungi. Periksa koneksi, lalu coba lagi.');
  }

  if (res.status === 401 && token) {
    hapusSesi();
    const lanjut = encodeURIComponent(location.pathname + location.search);
    location.assign(`/masuk/?lanjut=${lanjut}`);
    throw new ApiError(401, 'Sesi berakhir. Silakan masuk lagi.');
  }

  const data: unknown = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(res.status, pesanGalat(data) ?? `Permintaan gagal (${res.status}).`);
  return data as T;
}
