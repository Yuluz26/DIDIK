// A thin JSON client for the Python API. Errors come back in Malay from the server.

export interface FieldError {
	loc: (string | number)[];
	message: string;
}

export class ApiError extends Error {
	constructor(
		public status: number,
		message: string,
		public errors: FieldError[] = []
	) {
		super(message);
	}

	/** The message for one field, by its path, e.g. ("questions", 2, "choices"). */
	at(...path: (string | number)[]): string | undefined {
		const key = path.join('.');
		return this.errors.find((e) => e.loc.join('.') === key)?.message;
	}
}

async function request<T>(method: string, url: string, body?: unknown, raw?: Blob): Promise<T> {
	const headers: Record<string, string> = { Accept: 'application/json' };
	let payload: BodyInit | undefined;
	if (raw) {
		payload = raw;
		headers['Content-Type'] = raw.type || 'application/octet-stream';
	} else if (body !== undefined) {
		payload = JSON.stringify(body);
		headers['Content-Type'] = 'application/json';
	}

	let response: Response;
	try {
		response = await fetch(url, { method, headers, body: payload, credentials: 'same-origin' });
	} catch {
		throw new ApiError(0, 'Tiada sambungan ke pelayan. Semak internet dan cuba lagi.');
	}
	if (response.status === 204) return undefined as T;

	// A body that cannot be read (cut off when the page is left mid-request) is an error, never an
	// empty answer: callers would otherwise store `undefined` where they expect a list.
	const data = await response.json().catch(() => undefined);
	if (!response.ok) {
		const message = typeof data?.message === 'string' ? data.message : 'Sesuatu tidak kena. Cuba lagi.';
		throw new ApiError(response.status, message, Array.isArray(data?.errors) ? data.errors : []);
	}
	if (data === undefined) throw new ApiError(response.status, 'Jawapan pelayan tidak dapat dibaca. Cuba lagi.');
	return data as T;
}

export const api = {
	get: <T>(url: string) => request<T>('GET', url),
	post: <T>(url: string, body?: unknown) => request<T>('POST', url, body ?? {}),
	put: <T>(url: string, body: unknown) => request<T>('PUT', url, body),
	del: <T>(url: string) => request<T>('DELETE', url),
	upload: <T>(url: string, file: Blob) => request<T>('POST', url, undefined, file)
};
