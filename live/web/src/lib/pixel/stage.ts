/*
 * A small oval of lawn with a dirt underside, a few flowers and tufts: the patch of ground a child's
 * character stands on while choosing it (joining) and while waiting in the lobby.
 */
import { memo, sheetOf } from './cache';
import { M } from './palette';
import { Pix, rgba } from './pix';

export const PATCH = { w: 46, h: 16 };

const PETALS = ['#ffffff', '#ffd34d', '#ff8fb1', '#c9a0ff'].map((h) => rgba(h));

export function lawnPatch() {
	return memo('stage:patch', () => {
		const { w, h } = PATCH;
		const p = new Pix(w, h);
		const cx = w / 2;
		const rx = w / 2 - 2;
		const inside = (x: number, y: number) => ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - 6.4) / 5.6) ** 2 <= 1;

		// the cut edge of the turf, then the top of the lawn with its light on the upper left
		p.blob(cx, 8.6, rx, 5.6, M.dirt, { rim: true, dither: 0.3 });
		p.blob(cx, 6.4, rx, 5.6, M.grass, { rim: true, dither: 0.45, bias: 0.2 });
		p.speckle(M.grass.c[1], 0.1, 3, inside);
		p.speckle(M.grass.c[3], 0.1, 8, inside);

		// tufts and flowers, placed by hand so the character's feet stay clear in the middle
		for (const [x, y] of [[8, 5], [37, 8], [14, 10], [30, 3], [41, 5]]) {
			p.set(x, y, M.grass.c[1]);
			p.set(x - 1, y + 1, M.grass.c[1]);
			p.set(x + 1, y + 1, M.grass.c[1]);
			p.set(x, y + 1, M.grass.c[0]);
		}
		for (const [x, y, i] of [[5, 7, 0], [39, 6, 1], [10, 4, 2], [34, 10, 3], [42, 8, 0], [6, 9, 1]] as const) {
			p.set(x, y, PETALS[i]);
			p.set(x, y + 1, M.grass.c[0]);
		}
		return sheetOf(p.outline());
	});
}
