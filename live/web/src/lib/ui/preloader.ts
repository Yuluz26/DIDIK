// The page's own preloader (app.html): Didi hopping on its island while the app's files arrive. The root
// layout hides it once the app is up and its fonts are in (at once from the cache on a later visit), but never
// sooner than half a second after it appeared, so it does not just flash past.

const SHOWN_FOR = 500;
const FONTS_WAIT = 1200;

declare global {
	interface Window {
		__didikPreloader?: { shownAt: number; hide: () => void };
	}
}

/** A game's own screens: the child's and the host's. They never show a preloader. */
export const isGamePath = (path: string) => /^\/(m|hos)(\/|$)/.test(path);

export async function hidePreloader(): Promise<void> {
	const preloader = window.__didikPreloader;
	if (!preloader) return;
	await Promise.race([document.fonts?.ready, new Promise((done) => setTimeout(done, FONTS_WAIT))]);
	const left = SHOWN_FOR - (performance.now() - preloader.shownAt);
	setTimeout(preloader.hide, Math.max(0, left));
}
