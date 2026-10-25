/*
 * The ground of a world, painted from a map of tiles. Each pixel takes the texture of the land it
 * is on (grass, a dirt path, water, planks, cobbles), outer corners are rounded where two sides meet
 * different land, and the borders between lands get the small touches that make a tile map look
 * drawn: a dark rim on the higher land, a lit lip on the side facing the light, a shadow on the low
 * land at its foot, foam where water laps a bank.
 */
import { TILE } from './cache';
import { M } from './palette';
import { type Colour, Pix, type Ramp, mix, noise, rgba } from './pix';

export type Land = 'grass' | 'dirt' | 'sand' | 'water' | 'deep' | 'plank' | 'stone' | 'moss' | 'soil';

/** The map: land for each tile, row by row; `land('x')` characters are mapped by the caller. */
export type LandMap = readonly (readonly Land[])[];

const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
const bayer = (x: number, y: number) => BAYER[(y & 3) * 4 + (x & 3)] / 16;

/** Smooth value noise in [0, 1): broad patches of tone. */
function vnoise(x: number, y: number, seed: number): number {
	const x0 = Math.floor(x);
	const y0 = Math.floor(y);
	const fx = x - x0;
	const fy = y - y0;
	const sx = fx * fx * (3 - 2 * fx);
	const sy = fy * fy * (3 - 2 * fy);
	const a = noise(x0, y0, seed);
	const b = noise(x0 + 1, y0, seed);
	const c = noise(x0, y0 + 1, seed);
	const d = noise(x0 + 1, y0 + 1, seed);
	return a + (b - a) * sx + (c - a) * sy + (a - b - c + d) * sx * sy;
}

interface Def {
	layer: number;
	ramp: Ramp;
	round: boolean;
	tex: (x: number, y: number, seed: number) => Colour;
}

/** Soft patches of a lighter and darker tone, dithered at their edges. */
function patched(r: Ramp, x: number, y: number, seed: number, scale = 9, soft = 0.5): Colour {
	const t = vnoise(x / scale, y / scale, seed) + (bayer(x, y) - 0.5) * 0.2;
	return t > 0.64 ? mix(r.c[2], r.c[3], soft) : t < 0.34 ? mix(r.c[2], r.c[1], soft) : r.c[2];
}

const DEFS: Record<Land, Def> = {
	grass: {
		layer: 3,
		ramp: M.grass,
		round: true,
		tex(x, y, seed) {
			const g = M.grass.c;
			let c = patched(M.grass, x, y, seed + 1);
			const n = noise(x, y, seed);
			if (n < 0.03) c = g[1];
			else if (n > 0.975) c = g[4];
			// small tufts: a V of two darker pixels with a lit tip
			const tx = x >> 2;
			const ty = y >> 2;
			if (noise(tx, ty, seed + 7) < 0.11) {
				const lx = x & 3;
				const ly = y & 3;
				if ((lx === 0 || lx === 2) && ly === 1) c = g[1];
				else if (lx === 1 && ly === 2) c = g[0];
				else if (lx === 1 && ly === 1) c = g[3];
			}
			return c;
		}
	},
	moss: {
		layer: 3,
		ramp: M.leaf,
		round: true,
		tex(x, y, seed) {
			const g = M.leaf.c;
			const n = noise(x, y, seed);
			let c = patched(M.leaf, x, y, seed + 3, 7);
			if (n < 0.05) c = g[0];
			else if (n > 0.96) c = g[3];
			return c;
		}
	},
	dirt: {
		layer: 4,
		ramp: M.dirt,
		round: true,
		tex(x, y, seed) {
			const d = M.dirt.c;
			let c = patched(M.dirt, x, y, seed + 2, 7);
			const n = noise(x, y, seed + 5);
			if (n < 0.04) c = d[1];
			else if (n > 0.97) c = d[4];
			else if (n > 0.945 && noise(x >> 1, y >> 1, seed + 9) > 0.5) c = M.stone.c[3];
			return c;
		}
	},
	soil: {
		layer: 4,
		ramp: M.bark,
		round: true,
		tex(x, y, seed) {
			const d = M.bark.c;
			const n = noise(x, y, seed + 11);
			const furrow = (y + (x >> 3)) % 5 === 0;
			let c = furrow ? d[1] : d[2];
			if (n < 0.06) c = d[1];
			else if (n > 0.95) c = d[3];
			return c;
		}
	},
	sand: {
		layer: 2,
		ramp: M.sand,
		round: true,
		tex(x, y, seed) {
			const s = M.sand.c;
			let c = patched(M.sand, x, y, seed + 4, 8);
			const n = noise(x, y, seed + 6);
			if (n < 0.04) c = s[1];
			else if (n > 0.965) c = s[4];
			return c;
		}
	},
	water: {
		layer: 1,
		ramp: M.water,
		round: true,
		tex(x, y, seed) {
			const w = M.water.c;
			let c = w[2];
			const t = vnoise(x / 11, y / 8, seed + 8);
			if (t > 0.64) c = mix(w[2], w[3], 0.5);
			else if (t < 0.3) c = mix(w[2], w[1], 0.5);
			// ripples: short light dashes on every few rows
			const row = (y + (x >> 4) * 3) % 7;
			if (row === 0 && (x + (y >> 3) * 5) % 13 < 3) c = w[4];
			else if (row === 1 && (x + (y >> 3) * 5 + 1) % 13 < 2) c = w[3];
			return c;
		}
	},
	deep: {
		layer: 0,
		ramp: M.deep,
		round: true,
		tex(x, y, seed) {
			const w = M.deep.c;
			let c = w[2];
			const t = vnoise(x / 12, y / 9, seed + 12);
			if (t > 0.66) c = mix(w[2], w[3], 0.5);
			else if (t < 0.32) c = mix(w[2], w[1], 0.5);
			const row = (y + (x >> 4) * 3) % 8;
			if (row === 0 && (x + (y >> 3) * 5) % 14 < 3) c = w[4];
			return c;
		}
	},
	plank: {
		layer: 6,
		ramp: M.plank,
		round: false,
		tex(x, y, seed) {
			const p = M.plank.c;
			const row = y & 3;
			const board = y >> 2;
			let c = row === 0 ? p[3] : row === 3 ? p[1] : p[2];
			if ((x + board * 5) % 13 === 0) c = p[1];
			else if (noise(x, y, seed + 13) < 0.07) c = p[1];
			else if (row === 1 && noise(x >> 1, board, seed + 14) < 0.3 && x % 3 === 0) c = p[3];
			return c;
		}
	},
	stone: {
		layer: 5,
		ramp: M.stone,
		round: false,
		tex(x, y, seed) {
			const s = M.stone.c;
			const row = Math.floor(y / 5);
			const off = (row % 2) * 4;
			const col = Math.floor((x + off) / 8);
			if (y % 5 === 4 || (x + off) % 8 === 7) return s[1];
			const tone = noise(col, row, seed + 15);
			let c = tone > 0.66 ? s[3] : tone < 0.25 ? s[2] : s[2];
			if (y % 5 === 0) c = s[4];
			else if (noise(x, y, seed + 16) < 0.05) c = s[1];
			return c;
		}
	}
};

export interface GroundShape {
	land: Land;
	/** True for the pixels (x, y) of the shape, in pixels from the top left of the map. */
	test: (x: number, y: number) => boolean;
}

export interface GroundOptions {
	seed?: number;
	/** Smooth shapes laid over the tiles (a paved ellipse, a winding path), in order. */
	shapes?: readonly GroundShape[];
	/** Radius of rounded outer corners, in pixels. */
	corner?: number;
	/** Flowers, pebbles and little plants scattered over the grass, 0..1. */
	meadow?: number;
}

const PETALS = [rgba('#ffffff'), rgba('#ffd34d'), rgba('#ff8fb1'), rgba('#c9a0ff')];

/** Paints the whole ground of a world, one tile being TILE pixels square. */
export function paintGround(map: LandMap, o: GroundOptions = {}): Pix {
	const rows = map.length;
	const cols = map[0].length;
	const seed = o.seed ?? 1;
	const R = o.corner ?? 5;
	const p = new Pix(cols * TILE, rows * TILE);
	const ids = new Array<Land>(p.w * p.h);
	const at = (tx: number, ty: number, fallback: Land): Land => (tx < 0 || ty < 0 || tx >= cols || ty >= rows ? fallback : map[ty][tx]);

	// 1. which land is each pixel on, with the outer corners rounded
	for (let y = 0; y < p.h; y++) {
		for (let x = 0; x < p.w; x++) {
			const tx = Math.floor(x / TILE);
			const ty = Math.floor(y / TILE);
			const me = map[ty][tx];
			let land = me;
			if (DEFS[me].round) {
				const lx = x - tx * TILE;
				const ly = y - ty * TILE;
				const qx = lx < TILE / 2 ? -1 : 1;
				const qy = ly < TILE / 2 ? -1 : 1;
				const a = at(tx + qx, ty, me);
				const b = at(tx, ty + qy, me);
				if (a !== me && b !== me) {
					const cornerX = qx < 0 ? 0 : TILE;
					const cornerY = qy < 0 ? 0 : TILE;
					if (Math.abs(lx + 0.5 - cornerX) < R && Math.abs(ly + 0.5 - cornerY) < R) {
						const cx = cornerX - qx * R;
						const cy = cornerY - qy * R;
						if (Math.hypot(lx + 0.5 - cx, ly + 0.5 - cy) > R) land = DEFS[a].layer >= DEFS[b].layer ? a : b;
					}
				}
			}
			ids[y * p.w + x] = land;
		}
	}

	for (const shape of o.shapes ?? []) {
		for (let y = 0; y < p.h; y++) {
			for (let x = 0; x < p.w; x++) if (shape.test(x, y)) ids[y * p.w + x] = shape.land;
		}
	}

	// 2. texture
	for (let y = 0; y < p.h; y++) {
		for (let x = 0; x < p.w; x++) {
			const land = ids[y * p.w + x];
			p.set(x, y, DEFS[land].tex(x, y, seed), DEFS[land].ramp.ink);
		}
	}

	// 3. the borders between lands
	const land = (x: number, y: number): Land | null => (x < 0 || y < 0 || x >= p.w || y >= p.h ? null : ids[y * p.w + x]);
	const paint: [number, number, Colour][] = [];
	const around: [number, number][] = [
		[-1, 0],
		[0, -1],
		[1, 0],
		[0, 1]
	];
	for (let y = 0; y < p.h; y++) {
		for (let x = 0; x < p.w; x++) {
			const me = ids[y * p.w + x];
			const mine = DEFS[me];
			for (const [dx, dy] of around) {
				const n = land(x + dx, y + dy);
				if (!n || n === me) continue;
				const other = DEFS[n];
				if (mine.layer > other.layer) {
					// the higher land: a dark rim at its edge, then a lit lip on the sides facing the light
					paint.push([x, y, mine.ramp.c[0]]);
					break;
				}
				if (mine.layer < other.layer) {
					// the lower land at the foot of the higher: shaded where the light is blocked
					const shaded = dx < 0 || dy < 0;
					if (shaded) paint.push([x, y, mine.ramp.c[1]]);
					else if (me === 'water' || me === 'deep') paint.push([x, y, mine.ramp.c[4]]);
					break;
				}
			}
		}
	}
	for (const [x, y, c] of paint) p.set(x, y, c, p.ink[y * p.w + x]);
	// the lit lip: one pixel inside the rim, on edges that face up or left
	const lips: [number, number, Colour][] = [];
	for (let y = 1; y < p.h - 1; y++) {
		for (let x = 1; x < p.w - 1; x++) {
			const me = ids[y * p.w + x];
			const mine = DEFS[me];
			const top = ids[(y - 1) * p.w + x];
			const left = ids[y * p.w + x - 1];
			if ((top !== me && mine.layer > DEFS[top].layer) || (left !== me && mine.layer > DEFS[left].layer)) continue;
			const up2 = y > 1 ? ids[(y - 2) * p.w + x] : me;
			const left2 = x > 1 ? ids[y * p.w + x - 2] : me;
			if ((up2 !== me && top === me && mine.layer > DEFS[up2].layer) || (left2 !== me && left === me && mine.layer > DEFS[left2].layer)) {
				lips.push([x, y, mine.ramp.c[3]]);
			}
		}
	}
	for (const [x, y, c] of lips) p.set(x, y, c, p.ink[y * p.w + x]);

	// 4. a meadow: flowers and little stones on open grass, kept off the edges
	const meadow = o.meadow ?? 0.5;
	if (meadow > 0) {
		for (let ty = 0; ty < rows; ty++) {
			for (let tx = 0; tx < cols; tx++) {
				if (map[ty][tx] !== 'grass') continue;
				const n = noise(tx, ty, seed + 21);
				if (n > meadow * 0.16) continue;
				const x = tx * TILE + 3 + Math.floor(noise(tx, ty, seed + 22) * 10);
				const y = ty * TILE + 3 + Math.floor(noise(tx, ty, seed + 23) * 10);
				if (ids[y * p.w + x] !== 'grass' || ids[(y + 2) * p.w + x] !== 'grass' || ids[y * p.w + x + 2] !== 'grass') continue;
				const petal = PETALS[Math.floor(noise(tx, ty, seed + 24) * PETALS.length)];
				const kind = noise(tx, ty, seed + 25);
				if (kind < 0.7) {
					p.set(x, y, petal);
					p.set(x - 1, y, petal);
					p.set(x + 1, y, petal);
					p.set(x, y - 1, petal);
					p.set(x, y + 1, petal);
					p.set(x, y, rgba('#ffe27a'));
					p.set(x, y + 2, M.grass.c[1]);
				} else {
					p.set(x, y, M.stone.c[3]);
					p.set(x + 1, y, M.stone.c[3]);
					p.set(x, y + 1, M.stone.c[2]);
					p.set(x + 1, y + 1, M.stone.c[1]);
				}
			}
		}
	}
	return p;
}

/** A map made from rows of characters: `{ g: 'grass', '~': 'water' }`. */
export function landMap(rows: readonly string[], legend: Record<string, Land>): Land[][] {
	return rows.map((row) => [...row].map((ch) => legend[ch] ?? 'grass'));
}

export { mix };
