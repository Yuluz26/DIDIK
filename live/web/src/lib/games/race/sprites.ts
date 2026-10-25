/*
 * Lumba Sampan in pixels: the boat in three layers (the far side of the hull, the child, the near
 * side), a paddle and a wake, a pennant in the child's colour, the river with its jetty and sandy
 * bank, and the ripples that drift over it.
 */
import { TILE, memo, sheetOf } from '$lib/pixel/cache';
import { landMap, paintGround } from '$lib/pixel/ground';
import { M, coat } from '$lib/pixel/palette';
import { Pix, pack, rgba } from '$lib/pixel/pix';

export const BOAT_W = 46;
export const BOAT_H = 36;
/** Where the child's picture starts inside the boat, and the line the near wall hides them from. */
export const RIDER = { x: 14, y: 0 };

const gunwale = (x: number) => 27 - Math.round(3.6 * Math.abs((x - 24) / 20) ** 2.2);
const keel = (x: number) => 34 - Math.round(4.5 * Math.abs((x - 24) / 20) ** 2.6);

/** The far wall and the inside of the hull, and the mast. */
export function sampanBack() {
	return memo('sampan:back', () => {
		const p = new Pix(BOAT_W, BOAT_H);
		p.vline(8, 9, 18, M.bark.c[2], M.bark.ink);
		p.vline(7, 9, 18, M.bark.c[3], M.bark.ink);
		p.set(7, 8, M.gold.c[3], M.gold.ink);
		p.set(8, 8, M.gold.c[2], M.gold.ink);
		for (let x = 4; x <= 44; x++) {
			const far = gunwale(x) - 6;
			const near = gunwale(x);
			p.set(x, far, M.plank.c[3], M.plank.ink);
			for (let y = far + 1; y < near; y++) p.set(x, y, y === far + 1 ? M.bark.c[1] : M.bark.c[0], M.bark.ink);
		}
		return sheetOf(p.outline());
	});
}

/** The near wall of the hull: planks, a gold stripe, a rim of light, a little foam at the keel. */
export function sampanFront() {
	return memo('sampan:front', () => {
		const p = new Pix(BOAT_W, BOAT_H);
		for (let x = 4; x <= 44; x++) {
			const top = gunwale(x);
			const bottom = keel(x);
			for (let y = top; y <= bottom; y++) {
				let c = M.roof.c[2];
				if (y === top) c = M.roof.c[4];
				else if (y === top + 1) c = M.roof.c[3];
				else if (y === top + 2 || y === top + 3) c = M.gold.c[3];
				else if (y === bottom) c = M.roof.c[0];
				else if (y >= bottom - 1) c = M.roof.c[1];
				else if ((x - 4) % 7 === 0) c = M.roof.c[1];
				p.set(x, y, c, M.roof.ink);
			}
			if (x % 2 === 0) p.blend(x, bottom + 1, pack(255, 255, 255, 190));
		}
		p.outline();
		// the pointed ends rise a pixel past the rim
		p.set(4, gunwale(4) - 1, M.roof.c[3], M.roof.ink);
		p.set(44, gunwale(44) - 1, M.roof.c[4], M.roof.ink);
		return sheetOf(p);
	});
}

/** Three poses of the paddle: blade back, straight down, blade forward. */
export function paddle() {
	return memo('sampan:paddle', () => {
		const W = 16;
		const p = new Pix(W * 3, 20);
		[-5, 0, 5].forEach((dx, f) => {
			const q = new Pix(W, 20);
			const ox = 8;
			q.line(ox, 1, ox + dx, 14, M.plank.c[2], M.plank.ink);
			q.line(ox + 1, 1, ox + dx + 1, 14, M.plank.c[3], M.plank.ink);
			q.rect(ox + dx - 1, 13, 4, 5, M.plank.c[3], M.plank.ink);
			q.vline(ox + dx - 1, 13, 5, M.plank.c[4], M.plank.ink);
			q.set(ox + dx + 2, 17, M.plank.c[1], M.plank.ink);
			if (f !== 1) {
				q.blend(ox + dx - 3, 18, pack(255, 255, 255, 200));
				q.blend(ox + dx + 4, 17, pack(255, 255, 255, 200));
			}
			p.stamp(q.outline(), f * W, 0);
		});
		return sheetOf(p, W, 20);
	});
}

/** Foam trailing the stern while the child paddles. */
export function wake() {
	return memo('sampan:wake', () => {
		const W = 14;
		const p = new Pix(W * 2, 7);
		const foam = pack(255, 255, 255, 215);
		const dim = pack(205, 240, 250, 190);
		for (const [f, pts] of [
			[0, [[10, 1], [8, 2], [6, 2], [4, 3], [2, 3], [11, 4], [9, 5], [6, 5], [3, 6]]],
			[1, [[11, 1], [9, 1], [7, 2], [5, 3], [3, 3], [10, 4], [7, 5], [4, 5], [1, 6]]]
		] as const) {
			pts.forEach(([x, y], i) => p.set(f * W + x, y, i % 3 === 0 ? foam : dim));
		}
		return sheetOf(p, W, 7);
	});
}

/** A pennant in the child's colour, fluttering. */
export function pennant(colour: string) {
	return memo(`sampan:flag:${colour}`, () => {
		const W = 10;
		const r = coat(colour);
		const p = new Pix(W * 2, 8);
		for (let f = 0; f < 2; f++) {
			const q = new Pix(W, 8);
			q.poly([[9, 1], [9, 6], [1, 3 + f], [1, 2 + f]], r.c[2], r.ink);
			q.hline(5, 3, 4, r.c[3]);
			p.stamp(q.outline(), f * W, 0);
		}
		return sheetOf(p, W, 8);
	});
}

/** The drifting ripples, to be laid over the water and slid sideways by one period. */
export const RIPPLE = { w: 64, h: 24 };
export function ripples() {
	return memo('river:ripples', () => {
		const p = new Pix(RIPPLE.w, RIPPLE.h);
		const light = pack(255, 255, 255, 150);
		const soft = pack(205, 242, 250, 130);
		for (const [x, y, w] of [[4, 5, 6], [26, 12, 5], [44, 6, 7], [16, 19, 5], [52, 20, 6]] as const) {
			for (let i = 0; i < w; i++) p.set(x + i, y + (i === 0 || i === w - 1 ? 1 : 0), light);
			for (let i = 1; i < w - 2; i++) p.set(x + i + 1, y + 1, soft);
		}
		return p;
	});
}

export interface RiverShape {
	W: number;
	TOP: number;
	LANE: number;
	lanes: number;
	finish: number;
}

/** The river: a far bank, water in lanes with a rope of buoys between them, a jetty, the finish line. */
export function riverGround({ W, TOP, LANE, lanes, finish }: RiverShape): Pix {
	return memo(`river:${W}:${TOP}:${LANE}:${lanes}:${finish}`, () => {
		const bottom = TOP + lanes * LANE + 0.35;
		const H = TOP + lanes * LANE + 1.9;
		const top = TOP * TILE;
		const edge = bottom * TILE;
		const map = landMap(Array.from({ length: Math.ceil(H) }, () => 'g'.repeat(W)), { g: 'grass' });
		const ground = paintGround(map, {
			seed: 9,
			meadow: 0.3,
			shapes: [
				{ land: 'moss', test: (_x, y) => y < 9 },
				{ land: 'water', test: (_x, y) => y >= top && y < edge },
				{ land: 'sand', test: (_x, y) => y >= edge && y < edge + 9 },
				{ land: 'plank', test: (x, y) => x < 30 && y >= top - 3 && y < edge + 3 }
			]
		});
		const p = ground.crop(0, 0, W * TILE, Math.round(H * TILE));
		// lane ropes: a string of small red and white floats between the lanes
		for (let i = 1; i < lanes; i++) {
			const y = Math.round(top + i * LANE * TILE);
			for (let x = 36; x < finish * TILE; x += 6) {
				const c = (x / 6) % 2 === 0 ? rgba('#e2483d') : rgba('#ffffff');
				p.rect(x, y, 3, 2, c, rgba('#2a1f4a'));
				p.hline(x - 2, y + 1, 1, pack(255, 255, 255, 120));
			}
		}
		// the finish: a chain of floats across the river
		const fx = Math.round((finish + 0.5) * TILE);
		for (let y = Math.round(top) + 1; y < edge - 2; y += 5) {
			const red = ((y - top) / 5) % 2 < 1;
			p.rect(fx, y, 3, 3, red ? rgba('#e2483d') : rgba('#ffffff'), rgba('#2a1f4a'));
			p.set(fx, y, red ? rgba('#ff8a7a') : rgba('#ffffff'));
		}
		return p;
	});
}
