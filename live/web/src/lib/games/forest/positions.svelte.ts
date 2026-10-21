// Live positions for Hutan Misteri as reactive state, refreshed at most once per animation frame,
// with who is moving right now (so their legs swing).

import type { RoomClient } from '$lib/room.svelte';

export function livePositions(client: RoomClient) {
	const state = $state<{ all: Record<string, { x: number; y: number; f: number }>; moving: Record<string, boolean> }>({
		all: {},
		moving: {}
	});

	$effect(() => {
		let frame = 0;
		const lastMoved = new Map<string, number>();
		let previous: Record<string, { x: number; y: number }> = {};
		const sync = () => {
			frame = 0;
			const now = performance.now();
			const all = Object.fromEntries(client.positions);
			const moving: Record<string, boolean> = {};
			for (const [id, pos] of Object.entries(all)) {
				const before = previous[id];
				if (before && (Math.abs(before.x - pos.x) > 0.01 || Math.abs(before.y - pos.y) > 0.01)) lastMoved.set(id, now);
				moving[id] = now - (lastMoved.get(id) ?? 0) < 260;
			}
			previous = all;
			state.all = all;
			state.moving = moving;
		};
		sync();
		const stop = client.onPositions(() => {
			if (!frame) frame = requestAnimationFrame(sync);
		});
		// Legs stop swinging shortly after the last movement even when no new positions arrive.
		const settle = setInterval(() => {
			if (Object.values(state.moving).some(Boolean)) sync();
		}, 300);
		return () => {
			stop();
			clearInterval(settle);
			if (frame) cancelAnimationFrame(frame);
		};
	});

	return state;
}
