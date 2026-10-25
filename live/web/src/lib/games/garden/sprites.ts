/*
 * Kebun Ajaib's ground in pixels: grass with paths between the beds and over to the hut.
 */
import { TILE, memo } from '$lib/pixel/cache';
import { landMap, paintGround } from '$lib/pixel/ground';

export function gardenGround(W: number, H: number) {
	return memo(`garden:${W}:${H}`, () => {
		const map = landMap(Array.from({ length: H }, () => 'g'.repeat(W)), { g: 'grass' });
		const px = (tiles: number) => tiles * TILE;
		const bar = (x0: number, y0: number, x1: number, y1: number) => (x: number, y: number) => x >= px(x0) && x < px(x1) && y >= px(y0) && y < px(y1);
		return paintGround(map, {
			seed: 51,
			meadow: 0.35,
			shapes: [
				...[3.8, 7.4].map((x) => ({ land: 'dirt' as const, test: bar(x - 0.32, 2.0, x + 0.32, 10.6) })),
				...[4.75, 7.45].map((y) => ({ land: 'dirt' as const, test: bar(0.4, y - 0.3, 11, y + 0.3) })),
				{ land: 'dirt' as const, test: bar(10.7, 2.0, 11.4, 10.6) },
				{ land: 'dirt' as const, test: bar(10.7, 6.4, 13.3, 7.1) }
			]
		});
	});
}
