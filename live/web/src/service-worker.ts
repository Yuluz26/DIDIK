/// <reference no-default-lib="true"/>
/// <reference lib="esnext" />
/// <reference lib="webworker" />
/// <reference types="@sveltejs/kit" />

// The service worker: a cache on each phone and computer, so a page, a game and its art open at once the
// second time, even on a slow school Wi-Fi.
//
// - The app's scripts and styles of this build are stored when it installs (APP, one cache per build).
// - The story art (asked for with a hash of its content, see storyArt) and the uploaded pictures (each a
//   random name of its own) never change under their address: they are kept the first time they are
//   seen (ART, shared by every build) and served from there, video ranges included.
// - The page itself comes from the network, and from the last copy when the network is slow or gone.
// - The API, the game sockets and anything from another site are never touched.

import { build, files, version } from '$service-worker';

const sw = self as unknown as ServiceWorkerGlobalScope;

const APP = `didik-app-${version}`;
const ART = 'didik-art-v1';
const SHELL = '/__didik-page';
// How long a page waits for the network before the last copy is shown.
const PAGE_WAIT_MS = 3500;
// The art cache keeps at most this many files (the whole story is about 120).
const ART_FILES = 400;

const IMMUTABLE = new Set(build);
// Everything of this build except the story art, which is stored as it is first used (about 24 MB).
const PRECACHE = [...build, ...files.filter((file) => !file.startsWith('/story/'))];

sw.addEventListener('install', (event) => {
	event.waitUntil(
		(async () => {
			const cache = await caches.open(APP);
			await cache.addAll(PRECACHE);
			await sw.skipWaiting();
		})()
	);
});

sw.addEventListener('activate', (event) => {
	event.waitUntil(
		(async () => {
			for (const name of await caches.keys()) {
				if (name.startsWith('didik-app-') && name !== APP) await caches.delete(name);
			}
			await pruneArt();
			await sw.clients.claim();
		})()
	);
});

/** Only the newest copy of each file is kept (an older hash of the same picture is dropped), and no more than ART_FILES. */
async function pruneArt(): Promise<void> {
	const cache = await caches.open(ART);
	const keys = await cache.keys();
	const newest = new Map<string, Request>();
	for (const request of keys) newest.set(new URL(request.url).pathname, request);
	const keep = new Set([...newest.values()].slice(-ART_FILES));
	await Promise.all(keys.filter((request) => !keep.has(request)).map((request) => cache.delete(request)));
}

sw.addEventListener('fetch', (event) => {
	const request = event.request;
	if (request.method !== 'GET') return;
	const url = new URL(request.url);
	if (url.origin !== sw.location.origin) return;
	if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/ws/')) return;

	if (request.mode === 'navigate') {
		event.respondWith(page(request));
	} else if (IMMUTABLE.has(url.pathname)) {
		event.respondWith(fromApp(request));
	} else if ((url.pathname.startsWith('/story/') && url.searchParams.has('v')) || url.pathname.startsWith('/uploads/')) {
		event.respondWith(art(request));
	}
	// anything else (the app's version check, an unversioned file) goes to the network as usual
});

/** The page: the network's answer, and the last copy when the network is slow or gone. */
async function page(request: Request): Promise<Response> {
	const cache = await caches.open(APP);
	const network = fetch(request).then(async (response) => {
		// A page the server marks no-store (the owner's private control room) is never kept: its copy would
		// come back in place of the site's own page on a slow connection.
		const kept = !(response.headers.get('cache-control') ?? '').includes('no-store');
		if (kept && response.ok && (response.headers.get('content-type') ?? '').includes('text/html')) {
			await cache.put(SHELL, response.clone());
		}
		return response;
	});
	const waited = new Promise<Response | undefined>((done) =>
		setTimeout(async () => done(await cache.match(SHELL)), PAGE_WAIT_MS)
	);
	try {
		const first = await Promise.race([network, waited]);
		if (first) return first;
		return await network;
	} catch {
		const copy = await cache.match(SHELL);
		if (copy) return copy;
		return new Response(
			'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>DIDIK</title>' +
				'<body style="font:18px/1.6 system-ui;text-align:center;padding:3rem 1rem">' +
				'<h1>Tiada sambungan internet</h1><p>Semak Wi-Fi, kemudian muat semula halaman ini.</p>',
			{ status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
		);
	}
}

/** A script or style of this build: stored at install, so it never waits on the network. */
async function fromApp(request: Request): Promise<Response> {
	const cache = await caches.open(APP);
	const hit = await cache.match(request);
	if (hit) return hit;
	const response = await fetch(request);
	if (response.ok) await cache.put(request, response.clone());
	return response;
}

/** Story art and uploaded pictures: from the cache, fetched whole the first time; a video's ranges are cut from the stored copy. */
async function art(request: Request): Promise<Response> {
	const cache = await caches.open(ART);
	// stored without its Range header, whole
	const key = new Request(request.url);
	let stored = await cache.match(key);
	if (!stored) {
		const response = await fetch(key);
		if (response.status !== 200) return response;
		await cache.put(key, response.clone());
		stored = response;
	}
	const range = request.headers.get('range');
	return range ? ranged(stored, range) : stored;
}

/** A 206 answer to `bytes=start-end` out of a whole stored file, as a video asks for (Safari always does). */
async function ranged(whole: Response, range: string): Promise<Response> {
	const blob = await whole.blob();
	const match = /^bytes=(\d*)-(\d*)$/.exec(range.trim());
	if (!match) return new Response(blob, { status: 200, headers: whole.headers });
	const size = blob.size;
	let start = match[1] === '' ? size - Number(match[2]) : Number(match[1]);
	let end = match[1] === '' || match[2] === '' ? size - 1 : Number(match[2]);
	start = Math.max(0, start);
	end = Math.min(end, size - 1);
	if (start > end) return new Response(null, { status: 416, headers: { 'Content-Range': `bytes */${size}` } });
	return new Response(blob.slice(start, end + 1), {
		status: 206,
		headers: {
			'Content-Type': whole.headers.get('content-type') ?? 'application/octet-stream',
			'Content-Range': `bytes ${start}-${end}/${size}`,
			'Content-Length': String(end - start + 1),
			'Accept-Ranges': 'bytes'
		}
	});
}
