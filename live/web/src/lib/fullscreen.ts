/** Browser fullscreen must be requested synchronously from a user gesture. */
type FullDocument = Document & {
	webkitFullscreenEnabled?: boolean;
	webkitFullscreenElement?: Element | null;
};

type FullElement = HTMLElement & {
	webkitRequestFullscreen?: () => Promise<void> | void;
};

export function fullscreenAvailable(): boolean {
	if (typeof document === 'undefined') return false;
	const doc = document as FullDocument;
	return !!(doc.fullscreenEnabled || doc.webkitFullscreenEnabled);
}

export function fullscreenActive(): boolean {
	if (typeof document === 'undefined') return false;
	const doc = document as FullDocument;
	return !!(doc.fullscreenElement || doc.webkitFullscreenElement);
}

export function enterFullscreen(): Promise<boolean> {
	if (!fullscreenAvailable()) return Promise.resolve(false);
	if (fullscreenActive()) return Promise.resolve(true);
	const root = document.documentElement as FullElement;
	try {
		if (root.requestFullscreen) {
			return Promise.resolve(root.requestFullscreen({ navigationUI: 'hide' }))
				.then(() => fullscreenActive())
				.catch(() => false);
		}
		if (root.webkitRequestFullscreen) {
			return Promise.resolve(root.webkitRequestFullscreen())
				.then(() => fullscreenActive())
				.catch(() => false);
		}
	} catch {
		/* The browser can refuse even during a gesture; the page still fills the viewport. */
	}
	return Promise.resolve(false);
}
