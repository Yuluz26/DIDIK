/*
 * Kubu Pasir's beach in base pixels: the sky and the sea behind, the wet sand where the waves wash
 * in, the dry sand in front with shells and a spade, and the castle, built in tiers that narrow as
 * they rise the way a real sandcastle does. Sea walls are long mounds between the sea and the castle,
 * so a wave meets them first.
 */
import { memo } from '$lib/pixel/cache';
import { Pix } from '$lib/pixel/pix';
import { DAY, M, bands, cloud, mix, noise, rgba, sun } from './scenery';

export const BEACH = {
	w: 176,
	/** Where the sea meets the sky. */
	horizon: 34,
	/** Where the waves usually reach up the sand. */
	surf: 58,
	/** The front sea wall's foot, and the gap between two walls. */
	wall: 70,
	wallGap: 6
} as const;

const SEA = [rgba('#5fb9d0'), rgba('#3fa2c0'), rgba('#2f8db1'), rgba('#2a7ea6')];
export const FOAM = rgba('#f4fbfb');

/** How tall the scene is for a castle of `floors`: the beach grows so the tallest castle fits. */
export function beachHeight(floors: number): number {
	return Math.max(118, 46 + floors * 8 + 28);
}

/** The sky, sea and sand, `h` tall. */
export function beachBack(h: number): Pix {
	return memo(`beach:back:${h}`, () => {
		const { w, horizon, surf } = BEACH;
		const p = new Pix(w, h);
		bands(p, 0, horizon, DAY, 3);
		sun(p, 26, 12, 6);
		p.stamp(cloud(1), 112, 8);
		p.stamp(cloud(2), 60, 18);
		// an island far out at sea
		p.ellipse(150, horizon + 1, 12, 3.4, (x, y) => (y < horizon - 1 ? M.pine.c[2] : M.pine.c[1]), M.pine.ink);
		for (let x = 0; x < w; x++) p.set(x, horizon, mix(SEA[0], rgba('#cdeaf7'), 0.5));
		bands(p, horizon + 1, surf + 4, SEA, 3);
		// long lines of far swell
		for (let y = horizon + 3; y < surf - 2; y += 4) {
			for (let x = 0; x < w; x++) if (noise(x >> 2, y, 7) < 0.35) p.set(x, y, mix(SEA[0], FOAM, 0.35));
		}
		// wet sand, then dry sand with grain, shells and a starfish
		for (let y = surf; y < h; y++) {
			for (let x = 0; x < w; x++) {
				const wet = y < surf + 7;
				const n = noise(x, y, 3);
				const c = wet ? (n < 0.12 ? M.sand.c[0] : M.sand.c[1]) : n < 0.06 ? M.sand.c[1] : n > 0.95 ? M.sand.c[4] : n > 0.6 ? M.sand.c[3] : M.sand.c[2];
				p.set(x, y, c);
			}
		}
		for (let x = 0; x < w; x++) p.set(x, surf + 7, M.sand.c[1]);
		const shells: [number, number][] = [[20, h - 14], [140, h - 26], [154, h - 9], [34, surf + 16], [118, surf + 13]];
		for (const [x, y] of shells) shell(p, x, y);
		starfish(p, 150, surf + 20);
		return p;
	});
}

function shell(p: Pix, x: number, y: number): void {
	const pink = M.pink;
	p.set(x, y, pink.c[4]).set(x + 1, y, pink.c[3]).set(x - 1, y + 1, pink.c[3]).set(x, y + 1, pink.c[4]).set(x + 1, y + 1, pink.c[3]).set(x + 2, y + 1, pink.c[2]);
}

function starfish(p: Pix, cx: number, cy: number): void {
	const o = M.autumn;
	for (const [dx, dy] of [[0, -2], [0, -1], [-2, 0], [-1, 0], [0, 0], [1, 0], [2, 0], [-1, 1], [1, 1], [-2, 2], [2, 2]]) p.set(cx + dx, cy + dy, o.c[3]);
	p.set(cx, cy, o.c[4]);
}

const SAND = M.sand;

/** A sea wall: a long mound of packed sand with shells pressed into it. */
export function wallMound(): Pix {
	return memo('beach:wall', () => {
		const p = new Pix(104, 10);
		p.shadow(52, 9, 53, 1.4, 90);
		// a lit, rounded top and a darker front face patted flat with a spade
		p.poly([[1, 9], [5, 2], [99, 2], [103, 9]], (x, y) => (y < 4 ? SAND.c[4] : y < 5 ? SAND.c[3] : y < 8 ? SAND.c[1] : SAND.c[0]), SAND.ink);
		p.hline(6, 2, 92, rgba('#fff8de'), SAND.ink);
		for (let x = 8; x < 98; x += 7) p.vline(x, 5, 3, SAND.c[0]);
		for (let x = 10; x < 96; x += 14) {
			p.set(x, 3, M.pink.c[3]).set(x + 1, 3, M.pink.c[4]);
			p.set(x + 6, 6, M.cream.c[4]);
		}
		p.outline();
		return p;
	});
}

export interface Built {
	pix: Pix;
	/** Where the top of the highest tier is, from the bottom of the picture. */
	top: number;
}

const FLAGS = [M.red, M.sun, M.sky];

/**
 * The castle, `floors` tiers high (the bottom one widest, with a door), battlements on the top tier
 * and up to three flags on poles above them. Its foot is the bottom of the picture.
 */
export function castle(floors: number, flags: number): Built {
	return memo(`beach:castle:${floors}:${flags}`, () => {
		const tierW = (i: number) => Math.max(18, 44 - i * 4);
		const TIER = 8;
		const h = floors * TIER + 5 + (flags ? 12 : 0) + 2;
		const w = 48;
		const p = new Pix(w, h);
		const cx = w / 2;
		const foot = h - 1;
		if (!floors) return { pix: p, top: 0 };
		p.shadow(cx + 2, foot - 0.5, tierW(0) / 2 + 3, 1.6, 80);
		for (let i = 0; i < floors; i++) {
			const tw = tierW(i);
			const x0 = Math.round(cx - tw / 2);
			const y0 = foot - (i + 1) * TIER + 1;
			p.box(x0, y0, tw, TIER, SAND, 2);
			// the smoothed lip each tier was patted into, and grain
			p.hline(x0, y0, tw, SAND.c[4], SAND.ink);
			for (let x = x0 + 2; x < x0 + tw - 2; x += 3) if (noise(x, y0, 5) < 0.5) p.set(x, y0 + 4 + ((x >> 1) % 2), SAND.c[1]);
			// arched windows, a door in the bottom tier
			const windows = i === 0 ? [cx - 12, cx + 9] : tw > 26 ? [cx - 7, cx + 4] : [cx - 1.5];
			for (const wx of windows) {
				p.rect(Math.round(wx), y0 + 3, 3, 3, SAND.c[0]);
				p.set(Math.round(wx) + 1, y0 + 2, SAND.c[0]);
			}
			if (i === 0) {
				p.rect(Math.round(cx) - 3, y0 + 2, 6, TIER - 2, SAND.c[0]);
				p.hline(Math.round(cx) - 2, y0 + 1, 4, SAND.c[0]);
				p.vline(Math.round(cx), y0 + 3, TIER - 3, rgba('#7a5a3a'));
			}
		}
		// battlements on the top tier
		const tw = tierW(floors - 1);
		const x0 = Math.round(cx - tw / 2);
		const yTop = foot - floors * TIER + 1;
		for (let x = x0; x < x0 + tw; x += 4) p.rect(x, yTop - 3, 2, 3, SAND.c[3], SAND.ink);
		// flags on poles, standing on the battlements
		const spots = [x0, x0 + tw - 2, Math.round(cx) - 1];
		for (let f = 0; f < Math.min(flags, 3); f++) {
			const fx = spots[f];
			const pole = yTop - 3;
			p.vline(fx, pole - 10, 10, M.bark.c[1], M.bark.ink);
			const r = FLAGS[f];
			p.poly([[fx + 1, pole - 10], [fx + 7, pole - 8], [fx + 1, pole - 6]], r.c[2], r.ink);
			p.set(fx + 2, pole - 9, r.c[4]);
		}
		p.outline();
		return { pix: p, top: h - yTop + 3 };
	});
}

/** A spade and a little bucket stuck in the sand beside the castle. */
export function spade(): Pix {
	return memo('beach:spade', () => {
		const p = new Pix(14, 14);
		p.vline(3, 1, 8, M.bark.c[2], M.bark.ink);
		p.rect(2, 0, 3, 1, M.bark.c[3], M.bark.ink);
		p.poly([[0.5, 8], [6, 8], [5, 13], [1.5, 13]], M.sky.c[2], M.sky.ink);
		p.poly([[7, 6], [13, 6], [12, 13], [8, 13]], (x) => (x < 9 ? M.red.c[3] : M.red.c[2]), M.red.ink);
		p.hline(7, 6, 7, M.red.c[4], M.red.ink);
		p.outline();
		return p;
	});
}
