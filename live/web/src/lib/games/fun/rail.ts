/*
 * Kereta Api Kampung's countryside in base pixels, in layers that slide past at different speeds
 * while the train runs: far hills, a line of trees and kampung houses, and near the track grass,
 * bushes and telegraph poles. The track is ballast, wooden sleepers and a steel rail; the wheels of
 * the engine and the carriages sit on the rail. Every layer repeats seamlessly every `RAIL.w` pixels.
 */
import { memo } from '$lib/pixel/cache';
import { Pix, type Ramp } from '$lib/pixel/pix';
import { DAY, M, bands, cloud, mix, noise, ramp, rgba, sun, treeline } from './scenery';

export const RAIL = {
	w: 176,
	h: 96,
	/** The top of the rail: wheels stand on it. */
	top: 74,
	/** Where the near ground begins. */
	ground: 62
} as const;

/** The sky, which never moves. */
export function railSky(): Pix {
	return memo('rail:sky', () => {
		const p = new Pix(RAIL.w, 50);
		bands(p, 0, 50, DAY, 3);
		sun(p, 150, 12, 6);
		p.stamp(cloud(2), 30, 10);
		return p;
	});
}

const TAU = Math.PI * 2;

/** Far blue-green hills, repeating every RAIL.w. */
export function railHills(): Pix {
	return memo('rail:hills', () => {
		const { w } = RAIL;
		const p = new Pix(w, 62);
		const r = ramp(['#5f9a8a', '#72ad95', '#88bf9f', '#a3d0ad', '#c0e0c0']);
		for (let x = 0; x < w; x++) {
			const top = Math.round(38 - 8 * (0.5 + 0.35 * Math.sin((x / w) * TAU * 2 + 1) + 0.15 * Math.sin((x / w) * TAU * 5)));
			for (let y = top; y < 62; y++) p.set(x, y, y === top ? r.c[3] : y - top < 3 ? r.c[2] : r.c[1], r.ink);
		}
		return p;
	});
}

/** Trees, coconut palms and a kampung house on stilts, repeating every RAIL.w. */
export function railTrees(): Pix {
	return memo('rail:trees', () => {
		const { w, ground } = RAIL;
		// painted a little wider, then what spills past the right edge wraps round to the left
		const wide = new Pix(w + 24, ground + 2);
		treeline(wide, 0, w + 10, ground - 1, M.leaf, 11);
		house(wide, 40, ground - 1, M.roof);
		house(wide, 128, ground - 1, ramp(['#5a3a6e', '#74508a', '#9068a6', '#ab86c0', '#c8a8d8']));
		const p = wide.crop(0, 0, w, ground + 2);
		for (let y = 0; y < p.h; y++) {
			for (let x = w; x < wide.w; x++) {
				const c = wide.get(x, y);
				if (c) p.set(x - w, y, c, wide.ink[y * wide.w + x]);
			}
		}
		return p;
	});
}

function house(p: Pix, x: number, foot: number, roof: Ramp): void {
	// stilts, a plank wall with a window, a steep roof
	for (const sx of [x + 1, x + 6, x + 11]) p.vline(sx, foot - 4, 4, M.bark.c[0], M.bark.ink);
	p.box(x, foot - 11, 13, 7, M.plank, 0);
	p.rect(x + 4, foot - 9, 3, 3, M.night.c[3]);
	p.set(x + 4, foot - 9, M.sun.c[4]);
	p.poly([[x - 2, foot - 10], [x + 6.5, foot - 17], [x + 15, foot - 10]], (_x, y) => (y < foot - 14 ? roof.c[3] : roof.c[2]), roof.ink);
	p.hline(x - 2, foot - 10, 17, roof.c[1], roof.ink);
}

/** The near ground: grass, the track's ballast and sleepers, the rail, bushes and a telegraph pole. */
export function railNear(): Pix {
	return memo('rail:near', () => {
		const { w, h, ground, top } = RAIL;
		const p = new Pix(w, h);
		for (let y = ground; y < h; y++) {
			for (let x = 0; x < w; x++) {
				const n = noise(x, y, 21);
				p.set(x, y, y === ground ? M.grass.c[3] : n < 0.07 ? M.grass.c[1] : n > 0.94 ? M.grass.c[3] : M.grass.c[2], M.grass.ink);
			}
		}
		// ballast: a bank of grey stones under the sleepers
		const gravel = [rgba('#7d7a7a'), rgba('#99948c'), rgba('#b3ada2'), rgba('#6a6668')];
		for (let y = top + 1; y < top + 9; y++) {
			for (let x = 0; x < w; x++) p.set(x, y, gravel[Math.floor(noise(x, y, 23) * 4)]);
		}
		for (let x = 0; x < w; x++) p.set(x, top + 9, mix(gravel[3], M.grass.c[1], 0.5));
		// sleepers, seen end on as the track runs across the picture
		for (let x = 2; x < w; x += 8) {
			p.rect(x, top + 2, 5, 2, M.bark.c[1], M.bark.ink);
			p.hline(x, top + 2, 5, M.bark.c[2]);
		}
		// the rail: a lit top, a dark web
		for (let x = 0; x < w; x++) {
			p.set(x, top, rgba('#d6d8e0'));
			p.set(x, top + 1, rgba('#5c5e6c'));
		}
		// bushes and flowers along the line, in front of the track
		for (const [bx, r] of [[18, 3.4], [96, 4], [150, 3]] as [number, number][]) {
			p.blob(bx, h - 6, r + 1.5, r, M.leaf, { rim: true, grain: (a, b) => (noise(a, b, 4) - 0.5) * 1.2 });
		}
		for (const fx of [60, 66, 120]) p.set(fx, h - 9, M.pink.c[4]).set(fx + 1, h - 9, M.sun.c[4]);
		return p;
	});
}

/** A telegraph pole: drawn with its foot at (x, foot). */
export function pole(): Pix {
	return memo('rail:pole', () => {
		const p = new Pix(9, 34);
		p.cyl(3, 2, 2, 32, M.bark);
		p.hline(0, 4, 9, M.bark.c[1], M.bark.ink);
		for (const x of [0, 4, 8]) p.set(x, 3, rgba('#e8eef4'));
		p.outline();
		return p;
	});
}

/** The station: a platform along the track, a little wooden station house and the name board. */
export function station(): Pix {
	return memo('rail:station', () => {
		const p = new Pix(STATION.w, STATION.h);
		const foot = STATION.h - 1;
		const w = STATION.w;
		// platform: concrete with a yellow line along its edge
		p.rect(0, foot - 6, w, 6, M.stone.c[2], M.stone.ink);
		p.hline(0, foot - 6, w, M.stone.c[4], M.stone.ink);
		p.hline(0, foot - 4, w, M.sun.c[3]);
		p.hline(0, foot, w, M.stone.c[0], M.stone.ink);
		// the station house, its roof overhanging the platform on posts
		p.box(68, foot - 22, 34, 16, M.cream, 0);
		p.rect(72, foot - 17, 6, 6, M.sky.c[1], M.sky.ink);
		p.rect(82, foot - 16, 6, 10, M.plank.c[1], M.plank.ink);
		p.rect(92, foot - 17, 6, 6, M.sky.c[1], M.sky.ink);
		p.poly([[62, foot - 22], [72, foot - 32], [100, foot - 32], [108, foot - 22]], (_x, y) => (y < foot - 28 ? M.roof.c[3] : M.roof.c[2]), M.roof.ink);
		p.hline(62, foot - 22, 47, M.roof.c[1], M.roof.ink);
		for (const x of [64, 106]) p.vline(x, foot - 21, 15, M.bark.c[2], M.bark.ink);
		// the name board, high on two posts so it shows over the carriages
		for (const x of [8, 55]) p.cyl(x, foot - 38, 2, 32, M.bark);
		p.rect(1, foot - 47, 62, 11, rgba('#fff6e6'), M.plank.ink);
		p.hline(1, foot - 47, 62, M.plank.c[2], M.plank.ink);
		p.hline(1, foot - 37, 62, M.plank.c[1], M.plank.ink);
		p.outline();
		return p;
	});
}
export const STATION = { w: 112, h: 50 } as const;
/** Where the name board's face is, in the station picture's pixels (for the name set over it). */
export const BOARD = { x: 2, y: 3, w: 60, h: 9 } as const;

/** The steam engine, facing right, with its two driving wheels in one of two turns. */
export function locomotive(frame: number): Pix {
	return memo(`rail:engine:${frame}`, () => {
		const p = new Pix(42, 26);
		const red = M.red;
		const dark = M.metal;
		const foot = 25;
		// running board and the frame under the boiler
		p.rect(2, foot - 9, 36, 2, dark.c[1], dark.ink);
		// boiler with brass bands, smokebox at the front
		p.rect(4, foot - 17, 26, 8, red.c[2], red.ink);
		p.hline(4, foot - 17, 26, red.c[4], red.ink);
		p.hline(4, foot - 16, 26, red.c[3], red.ink);
		p.hline(4, foot - 10, 26, red.c[1], red.ink);
		for (const x of [12, 20]) p.vline(x, foot - 17, 8, M.gold.c[3]);
		p.rect(28, foot - 18, 8, 9, dark.c[2], dark.ink);
		p.hline(28, foot - 18, 8, dark.c[3], dark.ink);
		p.set(35, foot - 14, M.sun.c[4]).set(35, foot - 15, M.sun.c[4]);
		// chimney (flared), dome, whistle
		p.rect(30, foot - 23, 4, 5, dark.c[1], dark.ink);
		p.rect(29, foot - 24, 6, 2, dark.c[2], dark.ink);
		p.rect(19, foot - 20, 5, 3, M.gold.c[3], M.gold.ink);
		p.hline(20, foot - 21, 3, M.gold.c[4], M.gold.ink);
		// the cab at the back, with a window and a roof
		p.rect(0, foot - 22, 11, 13, M.sky.c[2], M.sky.ink);
		p.rect(2, foot - 20, 6, 5, M.water.c[4], M.sky.ink);
		p.rect(-1, foot - 24, 13, 2, dark.c[1], dark.ink);
		// cowcatcher
		p.poly([[36, foot - 8], [41, foot - 1], [36, foot - 1]], dark.c[2], dark.ink);
		// wheels: two big drivers and a small one at the front, joined by a rod
		const spoke = frame % 2;
		for (const [cx, r] of [[10, 4.4], [21, 4.4], [32, 2.6]] as [number, number][]) {
			p.ellipse(cx, foot - r, r, r, dark.c[1], dark.ink);
			p.ellipse(cx, foot - r, r - 1.4, r - 1.4, red.c[1], dark.ink);
			p.set(cx, foot - r, M.gold.c[3]);
			if (r > 3) {
				const [dx, dy] = spoke ? [2, 0] : [0, 2];
				p.set(cx + dx, foot - r + dy, dark.c[0]).set(cx - dx, foot - r - dy, dark.c[0]);
			}
		}
		const rodY = foot - 4.4 + (spoke ? 1 : -1);
		p.hline(10, Math.round(rodY), 12, M.stone.c[3], dark.ink);
		p.outline();
		return p;
	});
}

const CAR_TONES = ['#2bb0a6', '#f5c518', '#8a5cd1', '#ec6ca5', '#6cb33f', '#e0742a', '#2f7fcf'];
const FACES = ['#f2d0b0', '#e7b98a', '#c98e5f', '#8f5b3a'];

/** A passenger carriage: panelled sides, windows with faces in them, a roof and two bogies. */
export function coach(index: number, frame: number): Pix {
	const tone = CAR_TONES[index % CAR_TONES.length];
	return memo(`rail:coach:${tone}:${frame}:${index % 4}`, () => {
		const r = ramp([mix(rgbaOf(tone), rgba('#2a1f4a'), 0.55), mix(rgbaOf(tone), rgba('#2a1f4a'), 0.28), rgbaOf(tone), mix(rgbaOf(tone), rgba('#fff1bb'), 0.3), mix(rgbaOf(tone), rgba('#fff1bb'), 0.6)].map(hexOf));
		const p = new Pix(30, 22);
		const foot = 21;
		p.rect(1, foot - 18, 28, 12, r.c[2], r.ink);
		p.hline(1, foot - 15, 28, r.c[3], r.ink);
		p.hline(1, foot - 7, 28, r.c[1], r.ink);
		p.rect(0, foot - 20, 30, 2, M.cream.c[1], M.cream.ink);
		p.hline(2, foot - 21, 26, M.cream.c[3], M.cream.ink);
		for (let i = 0; i < 3; i++) {
			const x = 3 + i * 9;
			p.rect(x, foot - 14, 6, 5, M.water.c[4], r.ink);
			const face = rgbaOf(FACES[(index + i) % FACES.length]);
			p.ellipse(x + 3, foot - 11, 1.8, 1.8, face);
			p.set(x + 2, foot - 12, rgba('#241b2c')).set(x + 4, foot - 12, rgba('#241b2c'));
			p.hline(x + 1, foot - 14, 4, mix(rgbaOf(FACES[(index + i + 1) % 4]), rgba('#241b2c'), 0.7));
		}
		// bogies: two wheels at each end, turning
		p.rect(2, foot - 6, 26, 2, M.metal.c[1], M.metal.ink);
		for (const cx of [5, 10, 20, 25]) {
			p.ellipse(cx, foot - 2.4, 2.4, 2.4, M.metal.c[1], M.metal.ink);
			p.set(cx + (frame % 2 ? 1 : 0), foot - 2 - (frame % 2 ? 0 : 1), M.metal.c[3]);
		}
		// coupler
		p.hline(29, foot - 5, 2, M.metal.c[2], M.metal.ink);
		p.outline();
		return p;
	});
}

const rgbaOf = (h: string) => rgba(h);
const hexOf = (c: number) => {
	const r = c & 255;
	const g = (c >>> 8) & 255;
	const b = (c >>> 16) & 255;
	return `#${((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1)}`;
};

/** A puff of steam, `size` 0..2. */
export function puff(size: number): Pix {
	return memo(`rail:puff:${size}`, () => {
		const r = [2.2, 3.4, 4.6][size];
		const p = new Pix(12, 10);
		p.blob(6, 5, r, r * 0.8, M.cloth, { bias: 0.8 });
		return p;
	});
}
