/*
 * Pasukan Warna's board in pixels: pointed hexagon tiles with a little thickness (grass, or a
 * team's colour with a flag, or a base with a tent), the marching ring that marks a tile a child
 * may take, and the sandy beach where each team's children stand.
 */
import { memo, sheetOf } from '$lib/pixel/cache';
import { Pix, type Ramp, mix, noise, rampFrom, rgba } from '$lib/pixel/pix';
import { M } from '$lib/pixel/palette';

export const HEX = { w: 20, h: 23, row: 17, depth: 3 };
export const CELL = { w: HEX.w, h: HEX.h + HEX.depth };

const corners = (ox: number, oy: number): [number, number][] => [
	[ox + 10, oy],
	[ox + 20, oy + 5.8],
	[ox + 20, oy + 17.2],
	[ox + 10, oy + 23],
	[ox, oy + 17.2],
	[ox, oy + 5.8]
];

const rampCache = new Map<string, Ramp>();
function teamRamp(owner: string | null, hex: string): Ramp {
	if (!owner) return M.grass;
	let r = rampCache.get(hex);
	if (!r) rampCache.set(hex, (r = rampFrom(hex)));
	return r;
}

/** One tile. `colour` is the owner's colour (null for free grass). */
export function hexTile(owner: string | null, colour: string, base: boolean, flag: boolean) {
	return memo(`hex:${owner}:${base}:${flag}`, () => {
		const p = new Pix(CELL.w, CELL.h);
		const r = teamRamp(owner, colour);
		// the side of the tile, under the top
		p.poly(corners(0, HEX.depth), r.c[0], r.ink);
		// the top
		p.poly(
			corners(0, 0),
			(x, y) => {
				const n = noise(x, y, owner ? 5 : 3);
				if (!owner) {
					if (n < 0.07) return r.c[1];
					if (n > 0.93) return r.c[4];
					if ((x >> 2) % 3 === 1 && y % 5 === 2 && noise(x >> 2, y, 9) < 0.5) return r.c[3];
					return r.c[2];
				}
				if ((x + y) % 5 === 0 && n > 0.35) return r.c[3];
				if (n < 0.05) return r.c[1];
				return r.c[2];
			},
			r.ink
		);
		const c = corners(0, 0).map(([x, y]) => [Math.round(x), Math.round(y)]);
		// lit on the upper left, in shade on the lower right
		const edge = (a: number, b: number, tone: number) => p.line(c[a][0], c[a][1], c[b][0], c[b][1], r.c[tone], r.ink);
		edge(4, 5, 4);
		edge(5, 0, 4);
		edge(0, 1, 3);
		edge(1, 2, 1);
		edge(2, 3, 1);
		edge(3, 4, 2);
		const post = (x: number, top: number, bottom: number) => {
			p.vline(x, top, bottom - top, M.bark.c[2], M.bark.ink);
			p.vline(x - 1, top, bottom - top, M.bark.c[3], M.bark.ink);
		};
		if (base) {
			// a tent with a flag on top
			p.poly([[10, 6], [16, 16], [4, 16]], mix(r.c[3], rgba('#ffffff'), 0.35), r.ink);
			p.poly([[10, 6], [16, 16], [10, 16]], r.c[3], r.ink);
			p.poly([[10, 12], [12.5, 16], [7.5, 16]], M.bark.c[1], M.bark.ink);
			post(10, 0, 8);
			p.poly([[11, 1], [16, 2.5], [11, 4]], rgba('#ffffff'), r.ink);
		} else if (flag) {
			post(11, 4, 15);
			p.poly([[12, 4], [17, 6], [12, 8]], rgba('#ffffff'), r.ink);
		}
		return sheetOf(p.outline());
	});
}

/** The ring around a tile that may be taken: white dashes that march, in two frames. */
export function hexRing() {
	return memo('hex:ring', () => {
		const p = new Pix(CELL.w * 2, CELL.h);
		const white = rgba('#ffffff');
		for (let f = 0; f < 2; f++) {
			const pts = corners(f * CELL.w, 0);
			for (let i = 0; i < 6; i++) {
				const [x0, y0] = pts[i];
				const [x1, y1] = pts[(i + 1) % 6];
				const steps = Math.ceil(Math.hypot(x1 - x0, y1 - y0));
				for (let k = 0; k <= steps; k++) {
					if ((k + f * 2) % 4 < 2) p.set(x0 + ((x1 - x0) * k) / steps, y0 + ((y1 - y0) * k) / steps, white);
				}
			}
		}
		return sheetOf(p, CELL.w, CELL.h);
	});
}
