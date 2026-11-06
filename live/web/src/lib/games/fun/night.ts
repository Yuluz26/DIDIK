/*
 * Pasar Malam's night in base pixels: a starry sky over the dark shapes of the kampung, two other
 * stalls glowing further down the lane, the packed-earth ground, and the bamboo poles the string of
 * lights hangs between. The child's own stall stands in the middle (art.ts).
 */
import { memo } from '$lib/pixel/cache';
import { Pix, pack } from '$lib/pixel/pix';
import { M, NIGHT, bands, mix, moon, noise, ramp, rgba, stars } from './scenery';

export const MARKET = {
	w: 176,
	h: 104,
	/** Where the ground begins. */
	ground: 72,
	/** The stall's foot. */
	stall: 92,
	/** The tops of the two poles the lights hang between. */
	poles: [5, 170] as const,
	poleTop: 10
} as const;

const SHAPES = ramp(['#0c0b16', '#13111f', '#1a1729', '#221f35', '#2c2842']);

/** Sky, moon, the kampung's roofs and trees in silhouette, the far stalls, the ground. */
export function nightBack(): Pix {
	return memo('night:back', () => {
		const { w, h, ground } = MARKET;
		const p = new Pix(w, h);
		bands(p, 0, ground, NIGHT, 3);
		stars(p, 0, 40, 0.007, 5);
		moon(p, 138, 14, 5, NIGHT[0]);
		// roofs and trees of the kampung against the sky
		for (let x = 0; x < w; x++) {
			const tree = 50 - Math.round(4 * Math.abs(Math.sin(x * 0.17)) + 3 * noise(x >> 2, 0, 3));
			for (let y = tree; y < ground; y++) p.set(x, y, SHAPES.c[1]);
		}
		for (const [x0, roofW] of [[18, 24], [70, 30], [128, 22]] as [number, number][]) {
			const top = 40;
			p.poly([[x0, top + 10], [x0 + roofW / 2, top], [x0 + roofW, top + 10]], SHAPES.c[2]);
			p.rect(x0 + 3, top + 10, roofW - 6, ground - top - 10, SHAPES.c[2]);
			// a lit window or two
			p.rect(x0 + 6, top + 13, 3, 3, rgba('#ffcf5a'));
			if (roofW > 24) p.rect(x0 + roofW - 10, top + 13, 3, 3, rgba('#ffb84a'));
		}
		// two other stalls down the lane, small with distance, glowing
		farStall(p, 8, ground + 2, M.sky);
		farStall(p, 146, ground + 2, M.pink);
		// packed earth, a little lighter where people walk
		for (let y = ground; y < h; y++) {
			for (let x = 0; x < w; x++) {
				const n = noise(x, y, 8);
				const path = Math.abs(y - 96) < 5;
				const base = path ? rgba('#4a4058') : rgba('#3a3348');
				p.set(x, y, n < 0.08 ? rgba('#2c2638') : n > 0.95 ? rgba('#5a5068') : base);
			}
		}
		for (let x = 0; x < w; x++) p.set(x, ground, rgba('#2a2436'));
		return p;
	});
}

function farStall(p: Pix, x: number, foot: number, cloth: typeof M.sky): void {
	const glow = pack(255, 200, 90, 50);
	for (let y = foot - 18; y < foot + 2; y++) for (let i = -3; i < 27; i++) p.blend(x + i, y, glow);
	p.rect(x, foot - 14, 2, 14, SHAPES.c[3]);
	p.rect(x + 22, foot - 14, 2, 14, SHAPES.c[3]);
	p.rect(x - 1, foot - 16, 26, 3, mix(cloth.c[2], SHAPES.c[0], 0.35));
	p.rect(x + 1, foot - 6, 22, 6, SHAPES.c[4]);
	p.hline(x + 1, foot - 6, 22, rgba('#ffcf5a'));
	for (let i = 0; i < 3; i++) p.rect(x + 4 + i * 6, foot - 12, 2, 3, rgba('#ffe070'));
}

/** A bamboo pole the string of lights is tied to. */
export function bamboo(): Pix {
	return memo('night:bamboo', () => {
		const len = MARKET.ground + 6 - MARKET.poleTop;
		const p = new Pix(3, len);
		const r = ramp(['#4a5a2a', '#6a7a3a', '#8a9a4a', '#a8b860', '#c8d880']);
		p.cyl(0, 0, 3, len, r);
		for (let y = 6; y < len; y += 9) p.hline(0, y, 3, r.c[0]);
		p.outline();
		return p;
	});
}

/** A soft pool of warm light on the ground, `rx` by `ry`. */
export function lightPool(rx: number, ry: number): Pix {
	return memo(`night:pool:${rx}:${ry}`, () => {
		const p = new Pix(rx * 2 + 2, ry * 2 + 2);
		const cx = rx + 1;
		const cy = ry + 1;
		for (let y = 0; y < p.h; y++) {
			for (let x = 0; x < p.w; x++) {
				const d = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2;
				if (d > 1) continue;
				const a = d < 0.35 ? 70 : d < 0.7 ? 46 : 24;
				p.set(x, y, pack(255, 196, 96, a));
			}
		}
		return p;
	});
}

/** Musical notes rising from the speaker. */
export function note(kind: number): Pix {
	return memo(`night:note:${kind}`, () =>
		Pix.fromMap(kind ? ['.##', '.#.', '.#.', '##.', '##.'] : ['.###', '.#.#', '.#.#', '##.#', '##..'], { '#': rgba('#ffe070') })
	);
}

export const BULBS = ['#ffe070', '#ff7a6a', '#7ee08a', '#7ec8ff', '#ffb84a'].map((h) => rgba(h));
export { mix };
