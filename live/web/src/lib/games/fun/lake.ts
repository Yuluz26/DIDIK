/*
 * Pancing Ikan's lake, in base pixels: the sky and the far bank with its trees mirrored in the water
 * (behind the fish), and the wooden jetty standing on its posts in the water, with the reeds in front
 * (in front of the fish). The child stands at the end of the jetty with the rod; these are the fixed
 * places the scene is laid out by.
 */
import { memo } from '$lib/pixel/cache';
import { Pix, pack } from '$lib/pixel/pix';
import { DAY, M, bands, cloud, hills, mix, noise, ramp, reflect, rgba, sun, treeline } from './scenery';

export const LAKE = {
	w: 176,
	h: 110,
	/** The far bank meets the water here. */
	shore: 42,
	/** The top of the jetty's planks; the child stands on it. */
	deck: 75,
	/** The jetty reaches this far out from the left edge. */
	end: 67,
	/** Where the child stands (the left of their cell). */
	angler: 47
} as const;

const WATER = [rgba('#7fcfd4'), rgba('#5dbcc6'), rgba('#3fa6b8'), rgba('#2f90ab'), rgba('#247a98')];
export const WATER_DEEP = rgba('#1f6d8c');

/** Everything behind the fish: sky, sun, clouds, far hills and trees, the lake and its lilies. */
export function lakeBack(): Pix {
	return memo('lake:back', () => {
		const { w, h, shore } = LAKE;
		const p = new Pix(w, h);
		bands(p, 0, shore, DAY, 3);
		sun(p, 150, 11, 6);
		p.stamp(cloud(0), 14, 6);
		p.stamp(cloud(2), 98, 15);
		hills(p, 30, 7, shore, ramp(['#4f8a86', '#63a08f', '#79b59a', '#98c9a8', '#b8dcc0']), 1.7, 0.8);
		treeline(p, -4, w + 4, shore - 1, M.pine, 5);
		// the far bank: a strip of sand at the water's edge
		for (let x = 0; x < w; x++) {
			p.set(x, shore - 1, noise(x, 0, 9) < 0.5 ? M.sand.c[2] : M.sand.c[1]);
			p.set(x, shore, M.sand.c[0]);
		}
		// water: pale near the far bank, deep near the jetty
		bands(p, shore + 1, h, WATER, 4);
		reflect(p, shore, 9, WATER[1], 3);
		// lily pads, one in flower, on the right where the line does not fall
		lily(p, 158, 61, false);
		lily(p, 150, 66, true);
		lily(p, 166, 72, false);
		lily(p, 124, 52, false);
		return p;
	});
}

function lily(p: Pix, cx: number, cy: number, flower: boolean): void {
	const r = M.leaf;
	p.ellipse(cx, cy, 4.2, 1.7, (x, y) => (y < cy ? r.c[3] : r.c[2]), r.ink);
	// the notch
	p.set(Math.round(cx) + 1, Math.round(cy) - 1, 0).set(Math.round(cx) + 2, Math.round(cy) - 1, 0);
	p.hline(Math.round(cx) - 4, Math.round(cy) + 1, 8, mix(r.c[0], WATER[2], 0.5));
	if (flower) {
		const pink = M.pink;
		p.set(cx - 1, cy - 2, pink.c[3]).set(cx, cy - 3, pink.c[4]).set(cx + 1, cy - 2, pink.c[3]).set(cx, cy - 2, M.sun.c[3]);
	}
}

/** Everything in front of the fish: the jetty, its posts in the water and its shadow, the reeds. */
export function lakeFront(): Pix {
	return memo('lake:front', () => {
		const { w, h, deck, end } = LAKE;
		const p = new Pix(w, h);
		const water = WATER[3];
		// the jetty's shadow on the water
		for (let y = deck + 4; y < deck + 11; y++) for (let x = 0; x < end + 2 - (y - deck - 4); x++) p.set(x, y, pack(16, 40, 70, 60));
		// posts: dry above the water, then a light ring where they go in, then seen through the water
		const waterline = deck + 12;
		for (const x of [3, 21, 39, 57]) {
			p.cyl(x, deck + 3, 3, waterline - deck - 3, M.bark);
			p.hline(x - 1, waterline, 5, WATER[0]);
			for (let y = waterline + 1; y < waterline + 12; y++) {
				// below the surface the post wavers a pixel either way and fades into the water
				const wob = (y >> 1) % 2;
				for (let i = 0; i < 3; i++) {
					const c = mix(M.bark.c[i === 0 ? 2 : 1], water, 0.45 + (y - waterline) * 0.04);
					p.set(x + i + wob, y, ((c & 0xffffff) | (190 << 24)) >>> 0);
				}
			}
		}
		// the deck: lit plank tops with dark gaps, then the edge of the frame beneath them
		for (let x = 0; x < end; x++) {
			const gap = x % 8 === 7;
			p.set(x, deck - 1, gap ? M.plank.c[1] : M.plank.c[4], M.plank.ink);
			p.set(x, deck, gap ? M.plank.c[1] : M.plank.c[3], M.plank.ink);
			p.set(x, deck + 1, gap ? M.plank.c[0] : noise(x, 1, 4) < 0.2 ? M.plank.c[1] : M.plank.c[2], M.plank.ink);
			p.set(x, deck + 2, M.plank.c[1], M.plank.ink);
			p.set(x, deck + 3, M.plank.c[0], M.plank.ink);
			if (noise(x, 2, 4) < 0.08 && !gap) p.set(x, deck, M.plank.c[2]);
		}
		p.vline(end, deck - 1, 5, M.plank.c[0], M.plank.ink);
		// a mooring post at the end of the jetty and a coil of rope by the bank
		p.cyl(end - 3, deck - 4, 3, 4, M.bark);
		p.hline(end - 3, deck - 4, 3, M.bark.c[3], M.bark.ink);
		p.ellipse(9, deck - 2, 3.4, 1.6, M.thatch.c[2], M.thatch.ink);
		p.ellipse(9, deck - 2.3, 1.6, 0.7, M.thatch.c[0]);
		// reeds in the corners, in front of everything in the water
		reeds(p, 2, h, 9, 31);
		reeds(p, w - 13, h, 12, 37);
		reeds(p, w - 4, h - 22, 6, 13);
		p.outline(rgba('#2a1f2d'));
		return p;
	});
}

function reeds(p: Pix, x0: number, base: number, count: number, seed: number): void {
	for (let i = 0; i < count; i++) {
		const x = x0 + Math.round(noise(i, 0, seed) * 12) - 2;
		const tall = 10 + Math.round(noise(i, 1, seed) * 12);
		const lean = noise(i, 2, seed) < 0.5 ? -1 : 1;
		for (let k = 0; k < tall; k++) p.set(x + (k > tall * 0.6 ? lean : 0), base - 1 - k, k < 3 ? M.leaf.c[1] : M.leaf.c[2 + (i % 2)], M.leaf.ink);
		if (i % 3 === 0) p.rect(x + lean, base - tall - 3, 2, 4, M.bark.c[2], M.bark.ink);
	}
}

/** The float: red over white, with a stub of a stick on top. */
export function bobber(gold: boolean): Pix {
	return memo(`lake:bobber:${gold}`, () => {
		const top = gold ? M.gold : M.red;
		return Pix.fromMap(['.t.', 'rrr', 'rhr', 'www', 'www'], { t: M.bark.c[0], r: top.c[2], h: top.c[4], w: rgba('#f6f4ee') });
	});
}

/** The bucket on the jetty; once something is caught, a tail sticks out of it. */
export function bucket(full: boolean): Pix {
	return memo(`lake:bucket:${full}`, () => {
		const r = M.metal;
		const p = new Pix(11, 12);
		// handle, then the pail, wider at the top
		for (const [x, y] of [[2, 3], [2, 2], [3, 1], [4, 0], [5, 0], [6, 0], [7, 1], [8, 2], [8, 3]]) p.set(x, y, r.c[1], r.ink);
		p.poly([[1, 4], [10, 4], [9, 12], [2, 12]], (x) => (x < 4 ? r.c[4] : x > 7 ? r.c[2] : r.c[3]), r.ink);
		p.hline(1, 4, 9, r.c[4], r.ink);
		p.hline(2, 8, 7, r.c[2], r.ink);
		if (full) {
			const fin = M.sky;
			p.set(5, 3, fin.c[2], fin.ink).set(6, 2, fin.c[3], fin.ink).set(4, 2, fin.c[3], fin.ink).set(5, 4, fin.c[1]);
		}
		p.outline();
		return p;
	});
}

/** A speech bubble with "!" in it: something is on the line. */
export function alert(): Pix {
	return memo('lake:alert', () =>
		Pix.fromMap(['.#####.', '#wwwww#', '#wwrww#', '#wwrww#', '#wwrww#', '#wwwww#', '#wwrww#', '.##w##.', '...#...'], {
			'#': rgba('#2a1f2d'),
			w: rgba('#ffffff'),
			r: rgba('#e2483d')
		})
	);
}
