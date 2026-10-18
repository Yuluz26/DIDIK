/**
 * POST JSON to the app with the CSRF token. Resolves with the parsed body, or rejects with an
 * Error that carries `status` and the parsed `body` so callers can tell "offline" from "refused".
 */
export async function postJson(url, data = {}) {
    const token = document.querySelector('meta[name="csrf-token"]')?.content ?? '';

    let response;

    try {
        response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Accept: 'application/json',
                'X-CSRF-TOKEN': token,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify(data),
            credentials: 'same-origin',
        });
    } catch (cause) {
        const error = new Error('network');
        error.status = 0;
        error.cause = cause;
        throw error;
    }

    const body = await response.json().catch(() => ({}));

    if (!response.ok) {
        const error = new Error('http');
        error.status = response.status;
        error.body = body;
        throw error;
    }

    return body;
}
