/*
 * Kampung Kita's ground in pixels: grass, a kampung road, the lane down to the padang, and the
 * padang itself, mown in stripes; and the arrow that marks the building going up.
 */
import { TILE, memo, sheetOf } from '$lib/pixel/cache';
import { landMap, paintGround } from '$lib/pixel/ground';
import { M } from '$lib/pixel/palette';
import { Pix } from '$lib/pixel/pix';

export function villageGround(W: number, H: number) {
	return memo(`village:${W}:${H}`, () => {
		const map = landMap(Array.from({ length: H }, () => 'g'.repeat(W)), { g: 'grass' });
		const px = (tiles: number) => tiles * TILE;
		return paintGround(map, {
			seed: 31,
			meadow: 0.4,
			shapes: [
				{ land: 'lawn', test: (x, y) => x >= px(0.3) && x < px(W - 0.3) && y >= px(9.35) && y < px(12.35) },
				{ land: 'dirt', test: (_x, y) => y >= px(4.7) && y < px(5.9) },
				{ land: 'dirt', test: (x, y) => x >= px(10.1) && x < px(10.9) && y >= px(5.8) && y < px(9.45) }
			]
		});
	});
}

/** A little arrow that bobs over the building being built. */
export function arrowDown() {
	return memo('village:arrow', () => {
		const p = new Pix(11, 9);
		p.poly([[0.5, 0.5], [10.5, 0.5], [5.5, 8.5]], M.sun.c[3], M.sun.ink);
		p.hline(2, 1, 7, M.sun.c[4]);
		p.set(2, 2, M.sun.c[4]);
		return sheetOf(p.outline());
	});
}
