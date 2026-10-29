// The worlds' living videos, each fetched whole (about 2 MB) before it plays and played from memory: no
// buffering halfway through a loop on a busy school Wi-Fi, no fetching again when the loop starts over.
// The next world's video is fetched ahead, while the child is still fighting the current boss.

const sources = new Map<string, Promise<string>>();

/** A source for `url` that plays from memory; the address itself if it cannot be fetched whole. */
export function sceneSource(url: string): Promise<string> {
	let job = sources.get(url);
	if (!job) {
		job = fetch(url, { priority: 'low' } as RequestInit)
			.then((response) => (response.ok ? response.blob() : Promise.reject(new Error(String(response.status)))))
			.then((blob) => URL.createObjectURL(blob))
			.catch(() => {
				// next time, try the network again
				sources.delete(url);
				return url;
			});
		sources.set(url, job);
	}
	return job;
}

/** Starts fetching these videos now, so they are ready when they are needed. */
export function warmScenes(urls: string[]): void {
	for (const url of urls) void sceneSource(url);
}
