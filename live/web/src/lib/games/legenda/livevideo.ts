// Keeps a world's living video playing (an attachment: `{@attach (v) => keepPlaying(v, wanted)}` on a
// muted, looping <video>). A browser may hold back a video that started in a hidden tab or a background
// pane, or one whose loading stalled, and then never start it by itself: this starts it once it can play,
// again whenever the page is shown, and reloads it if it has not started after a few seconds. While
// `wanted()` is false (the scene is covered) it stays paused, so only one video is decoded at a time.

const STALL_MS = 5000;

export function keepPlaying(video: HTMLVideoElement, wanted: () => boolean = () => true): () => void {
	// muted before anything else, so the browser allows it to start without a tap
	video.muted = true;
	video.defaultMuted = true;
	video.playsInline = true;

	const start = () => {
		if (document.hidden || !video.paused || !wanted()) return;
		void video.play().catch(() => undefined);
	};
	let stall: ReturnType<typeof setTimeout> | undefined;
	const watch = () => {
		clearTimeout(stall);
		stall = setTimeout(() => {
			if (wanted() && video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA && !document.hidden) {
				video.load();
				start();
			}
			watch();
		}, STALL_MS);
	};
	const shown = () => {
		start();
		watch();
	};

	video.addEventListener('canplay', start);
	document.addEventListener('visibilitychange', shown);
	start();
	watch();
	return () => {
		clearTimeout(stall);
		video.removeEventListener('canplay', start);
		document.removeEventListener('visibilitychange', shown);
	};
}
