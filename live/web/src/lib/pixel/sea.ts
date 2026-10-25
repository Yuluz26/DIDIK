/*
 * The front page's backdrops as repeating pixel pictures: the sea with its little waves (two frames
 * that take turns), the foam line where the sea meets the beach, grains of sand, the dusk sky in
 * dithered bands with a few stars, and the blades of grass along the top of the parents' field.
 * Each is a small picture the page repeats and magnifies by a whole number.
 */
import { memo } from './cache';
import { Pix, noise, rgba } from './pix';

const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
const bayer = (x: number, y: number) => (BAYER[(y & 3) * 4 + (x & 3)] + 0.5) / 16;

export const SEA = { w: 64, h: 64 };

/** Soft patches that repeat seamlessly: a value noise on a 4 × 4 lattice of 16-pixel cells, wrapped. */
function patches(x: number, y: number, seed: number): number {
	const cx = x / 16;
	const cy = y / 16;
	const x0 = Math.floor(cx);
	const y0 = Math.floor(cy);
	const fx = cx - x0;
	const fy = cy - y0;
	const sx = fx * fx * (3 - 2 * fx);
	const sy = fy * fy * (3 - 2 * fy);
	const at = (i: number, j: number) => noise(((i % 4) + 4) % 4, ((j % 4) + 4) % 4, seed);
	const a = at(x0, y0);
	const b = at(x0 + 1, y0);
	const c = at(x0, y0 + 1);
	const d = at(x0 + 1, y0 + 1);
	return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
}

/** The open sea: flat colour with patches a shade lighter and short wave marks, shifted a little in frame 1. */
export function seaTile(frame: 0 | 1): Pix {
	return memo(`sea:${frame}`, () => {
		const p = new Pix(SEA.w, SEA.h);
		const base = rgba('#1f78ab');
		const lift = rgba('#2481b4');
		const wave = rgba('#3589bd');
		const glint = rgba('#74bde2');
		for (let y = 0; y < SEA.h; y++) {
			for (let x = 0; x < SEA.w; x++) p.set(x, y, patches(x, y, 5) + (bayer(x, y) - 0.5) * 0.22 > 0.6 ? lift : base);
		}
		// a wave mark in about half the 8 × 8 cells
		for (let cy = 0; cy < SEA.h / 8; cy++) {
			for (let cx = 0; cx < SEA.w / 8; cx++) {
				if (noise(cx, cy, 31) > 0.5) continue;
				const long = noise(cx, cy, 32) > 0.45;
				const x = cx * 8 + Math.floor(noise(cx, cy, 33) * 2) + (frame ? 2 : 0);
				const y = cy * 8 + 1 + Math.floor(noise(cx, cy, 34) * 5);
				const width = long ? 5 : 3;
				p.rect(x, y, width, 1, wave);
				p.set(x - 1, y + 1, wave);
				p.set(x + width, y + 1, wave);
				if (long) p.set(x + 2, y - 1, glint);
			}
		}
		return p;
	});
}

export const SHORE = { w: 48, h: 16 };

/** Where the sea meets the sand: scalloped foam over the shallows, then wet and dry sand. */
export function shoreStrip(): Pix {
	return memo('sea:shore', () => {
		const p = new Pix(SHORE.w, SHORE.h);
		const foam = rgba('#ffffff');
		const surf = rgba('#d8f0f8');
		const shallow = rgba('#7cc2e4');
		const wet = rgba('#f0d9a2');
		const sand = rgba('#f8e7bf');
		for (let x = 0; x < SHORE.w; x++) {
			// two arcs along the strip: the line rides up and down in steps
			const y = 4 + Math.round(1.7 * Math.sin((x / SHORE.w) * Math.PI * 4));
			p.set(x, y, foam);
			p.set(x, y + 1, surf);
			p.set(x, y + 2, (x + y) % 2 ? shallow : surf);
			p.set(x, y + 3, shallow);
			p.set(x, y + 4, (x + y) % 2 ? wet : shallow);
			for (let k = y + 5; k < SHORE.h; k++) p.set(x, k, k === y + 5 ? wet : sand);
		}
		return p;
	});
}

export const BEACH = { w: 64, h: 64 };

/** Sand with a few grains, a pebble or two and a shell. */
export function beachTile(): Pix {
	return memo('sea:beach', () => {
		const p = new Pix(BEACH.w, BEACH.h);
		const sand = rgba('#f8e7bf');
		p.rect(0, 0, BEACH.w, BEACH.h, sand);
		const dark = rgba('#efd9a3');
		const light = rgba('#fff3d2');
		for (let y = 0; y < BEACH.h; y++) {
			for (let x = 0; x < BEACH.w; x++) {
				const n = noise(x, y, 77);
				if (n < 0.035) p.set(x, y, dark);
				else if (n > 0.985) p.set(x, y, light);
			}
		}
		// a shell and a pebble pair
		const shell = rgba('#fff6e6');
		const rim = rgba('#e3c892');
		for (const [x, y] of [[41, 18], [9, 47]]) {
			p.set(x, y, shell);
			p.set(x + 1, y, shell);
			p.set(x - 1, y + 1, rim);
			p.set(x, y + 1, shell);
			p.set(x + 1, y + 1, shell);
			p.set(x + 2, y + 1, rim);
			p.set(x, y + 2, rim);
			p.set(x + 1, y + 2, rim);
		}
		for (const [x, y] of [[26, 52], [55, 33]]) {
			p.set(x, y, rgba('#cdb88c'));
			p.set(x + 1, y, rgba('#cdb88c'));
			p.set(x + 1, y + 1, rgba('#b39a6c'));
		}
		return p;
	});
}

export const DUSK = { w: 96, h: 88 };
const SKY = ['#f8e7bf', '#f6cd9a', '#f2b077', '#d38a6f', '#8c6176', '#5a4f6b', '#2f3d5c', '#1b2d3f'].map((h) => rgba(h));

/** The sand turning to sunset and then night, in bands whose edges are dithered, with stars. */
export function duskSky(): Pix {
	return memo('sea:dusk', () => {
		const p = new Pix(DUSK.w, DUSK.h);
		const band = DUSK.h / SKY.length;
		for (let y = 0; y < DUSK.h; y++) {
			const k = Math.floor(y / band);
			const into = y - k * band;
			for (let x = 0; x < DUSK.w; x++) {
				let c = SKY[k];
				// the last rows of a band dither into the next, the first rows of the next dither back
				if (k < SKY.length - 1 && into >= band - 3) c = (into - (band - 3) + 1) / 7 + 0.14 > bayer(x, y) ? SKY[k + 1] : SKY[k];
				else if (k > 0 && into < 3) c = 1 - (into + 1) / 7 - 0.14 > bayer(x, y) ? SKY[k - 1] : SKY[k];
				p.set(x, y, c);
			}
		}
		const star = rgba('#f3efe6');
		for (let i = 0; i < 16; i++) {
			const x = Math.floor(noise(i, 1, 90) * DUSK.w);
			const y = 38 + Math.floor(noise(i, 2, 90) * 24);
			p.set(x, y, star);
			if (i % 4 === 0) {
				p.set(x - 1, y, star);
				p.set(x + 1, y, star);
				p.set(x, y - 1, star);
				p.set(x, y + 1, star);
			}
		}
		return p;
	});
}

export const FRINGE = { w: 32, h: 14 };

/** Grass along the top of the parents' field, rising into the night above it. */
export function grassFringe(): Pix {
	return memo('sea:fringe', () => {
		const p = new Pix(FRINGE.w, FRINGE.h);
		const night = rgba('#0f1f24');
		const field = rgba('#1c6b4a');
		const lit = rgba('#2f8a5c');
		const tip = rgba('#58b27a');
		p.rect(0, 0, FRINGE.w, FRINGE.h, night);
		for (let x = 0; x < FRINGE.w; x++) {
			// blades of different heights, always a pixel wider at the foot
			const height = 3 + Math.floor(noise(x >> 1, 0, 61) * 8) + (x % 4 === 1 ? 1 : 0);
			for (let k = 0; k < height + 3; k++) p.set(x, FRINGE.h - 1 - k, k === height + 2 ? tip : x % 3 === 0 ? lit : field);
		}
		// the last rows are solid, to meet the field
		p.rect(0, FRINGE.h - 3, FRINGE.w, 3, field);
		return p;
	});
}
