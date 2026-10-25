/*
 * Lompat!'s pond in pixels: a tile of water that repeats without a seam, the islands (a sandy rim,
 * a bank, a grassy top, a palm or a flowering bush), a strip of sand for the shore, a splash, and
 * the tail that turns a child who is out of hearts into a fish.
 */
import { memo, sheetOf } from '$lib/pixel/cache';
import { M, coat } from '$lib/pixel/palette';
import { Pix, mix, noise, pack, rgba } from '$lib/pixel/pix';

export const ISLAND = { w: 72, h: 40 };
/** Room above the island for the heads of the characters standing on it, in pixels. */
export const HEADROOM = 8;
/** The line the characters stand on, in island pixels, and the width they may spread over. */
export const STAND = { y: 25, left: 8, width: 56 };

/** Value noise that wraps every `period` pixels, so a tile of it repeats seamlessly. */
function wrapped(x: number, y: number, period: number, cells: number, seed: number): number {
	const f = period / cells;
	const gx = x / f;
	const gy = y / f;
	const x0 = Math.floor(gx);
	const y0 = Math.floor(gy);
	const fx = gx - x0;
	const fy = gy - y0;
	const sx = fx * fx * (3 - 2 * fx);
	const sy = fy * fy * (3 - 2 * fy);
	const at = (i: number, j: number) => noise(((i % cells) + cells) % cells, ((j % cells) + cells) % cells, seed);
	const a = at(x0, y0);
	const b = at(x0 + 1, y0);
	const c = at(x0, y0 + 1);
	const d = at(x0 + 1, y0 + 1);
	return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
}

/** Deep pond water, 48 pixels square, for repeating. */
export function pondWater() {
	return memo('pond:water', () => {
		const N = 48;
		const p = new Pix(N, N);
		const w = M.deep.c;
		for (let y = 0; y < N; y++) {
			for (let x = 0; x < N; x++) {
				const t = wrapped(x, y, N, 3, 3);
				let c = w[2];
				if (t > 0.6) c = mix(w[2], w[3], 0.38);
				else if (t < 0.32) c = mix(w[2], w[1], 0.38);
				p.set(x, y, c);
			}
		}
		// ripples: short pale dashes
		for (const [x, y, len] of [[5, 6, 6], [28, 14, 5], [14, 25, 7], [36, 33, 6], [4, 41, 5], [24, 44, 4]] as const) {
			for (let i = 0; i < len; i++) p.set(x + i, y, w[4]);
			for (let i = 1; i < len - 1; i++) p.set(x + i + 1, y + 1, w[3]);
		}
		return p;
	});
}

/** Sand for the near shore, 32 pixels square, with a lit lip along the top when drawn as a strip. */
export function shoreSand() {
	return memo('pond:sand', () => {
		const N = 32;
		const p = new Pix(N, N);
		const s = M.sand.c;
		for (let y = 0; y < N; y++) {
			for (let x = 0; x < N; x++) {
				const t = wrapped(x, y, N, 4, 5);
				let c = s[2];
				if (t > 0.62) c = mix(s[2], s[3], 0.6);
				else if (t < 0.32) c = mix(s[2], s[1], 0.5);
				const n = noise(x, y, 8);
				if (n < 0.04) c = s[1];
				else if (n > 0.96) c = s[4];
				p.set(x, y, c);
			}
		}
		return p;
	});
}

/** One island, with a palm (even) or a flowering bush (odd). */
export function island(variant: number) {
	return memo(`pond:island:${variant % 2}`, () => {
		const p = new Pix(ISLAND.w, ISLAND.h);
		const cx = ISLAND.w / 2;
		// shallow water around the foot
		const foam = pack(220, 245, 250, 150);
		for (let y = 0; y < ISLAND.h; y++) {
			for (let x = 0; x < ISLAND.w; x++) {
				if (((x + 0.5 - cx) / 35) ** 2 + ((y + 0.5 - 30) / 8.4) ** 2 <= 1) p.blend(x, y, foam);
			}
		}
		// the bank, the sandy rim, the grass
		p.ellipse(cx, 27, 32.5, 8.5, (x, y) => (y > 29 ? M.dirt.c[0] : M.dirt.c[1]), M.dirt.ink);
		p.ellipse(cx, 22.5, 32.5, 8.5, (x, y) => (y < 17 ? M.sand.c[3] : y > 26 ? M.sand.c[1] : M.sand.c[2]), M.sand.ink);
		p.ellipse(cx, 21, 28.5, 7, (x, y) => {
			const n = noise(x, y, 14);
			if (n < 0.06) return M.grass.c[1];
			if (n > 0.93) return M.grass.c[4];
			return y < 18 ? M.grass.c[3] : M.grass.c[2];
		}, M.grass.ink);
		p.set(cx - 18, 20, M.grass.c[4]);
		p.set(cx - 17, 20, M.grass.c[4]);
		if (variant % 2 === 0) {
			// a palm at the back left
			for (let i = 0; i < 17; i++) {
				const x = 14 + Math.round(Math.sin(i / 8) * 1.4);
				p.rect(x, 20 - i, 2, 1, i % 4 === 0 ? M.bark.c[1] : M.bark.c[2], M.bark.ink);
			}
			for (const [dx, dy] of [[-8, 3], [-6, -1], [-2, -3], [3, -2], [7, 2], [8, 6]]) {
				for (let i = 0; i <= 5; i++) {
					const t = i / 5;
					p.blob(15 + dx * t, 3 + dy * t + t * t * 3, 2.2 - t * 0.9, 1.6 - t * 0.5, M.leaf, { rim: true, bias: 0.3 - t * 0.6 });
				}
			}
		} else {
			p.blob(54, 18.5, 5.2, 3.8, M.leaf, { rim: true, bias: -0.2 });
			p.blob(59, 19.5, 4, 3, M.leaf, { rim: true, bias: -0.4 });
			p.blob(52, 16.8, 2.6, 1.8, M.leaf, { bias: 0.9 });
			for (const [x, y, c] of [[53, 17, '#ff7aa2'], [58, 18, '#ffd34d'], [56, 20, '#ff7aa2']] as const) {
				p.set(x, y, rgba(c), M.leaf.ink);
				p.set(x + 1, y, rgba(c), M.leaf.ink);
			}
		}
		return sheetOf(p.outline());
	});
}

/** A ring that spreads where a wrong island sank: three frames. */
export function splash() {
	return memo('pond:splash', () => {
		const W = 56;
		const H = 20;
		const p = new Pix(W * 3, H);
		const white = pack(255, 255, 255, 235);
		const soft = pack(205, 242, 250, 190);
		[10, 17, 24].forEach((rx, f) => {
			const ry = rx * 0.34;
			for (let a = 0; a < 90; a++) {
				const t = (a / 90) * Math.PI * 2;
				p.set(f * W + W / 2 + Math.cos(t) * rx, H / 2 + Math.sin(t) * ry, a % 3 ? white : soft);
			}
		});
		return sheetOf(p, W, H);
	});
}

/** The tail of a child who has become a fish, in their colour. */
export function fishTail(colour: string) {
	return memo(`pond:tail:${colour}`, () => {
		const r = coat(colour);
		const p = new Pix(10, 10);
		p.poly([[1, 5], [9, 1], [7, 5], [9, 9]], r.c[2], r.ink);
		p.hline(3, 5, 4, r.c[3]);
		return sheetOf(p.outline());
	});
}
