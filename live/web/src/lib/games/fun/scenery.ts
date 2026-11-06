/*
 * The painters the scenes of the newer games share: skies in dithered bands, clouds, rolling hills,
 * a far line of trees, water with the far bank mirrored in it, a starry night. Each paints into a Pix
 * at base pixels, in the one palette, so a lake, a beach, a railway and a night market all sit in the
 * same light as the rest of the game.
 */
import { memo } from '$lib/pixel/cache';
import { M } from '$lib/pixel/palette';
import { type Colour, Pix, type Ramp, mix, noise, pack, ramp, rgba } from '$lib/pixel/pix';

const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
export const bayer = (x: number, y: number) => (BAYER[(y & 3) * 4 + (x & 3)] + 0.5) / 16;

/** Rows y0..y1 in bands of the colours given, top first, each dithered into the next over `soft` rows. */
export function bands(p: Pix, y0: number, y1: number, colours: readonly Colour[], soft = 3, x0 = 0, x1 = p.w): void {
	const n = colours.length;
	const band = (y1 - y0) / n;
	for (let y = y0; y < y1; y++) {
		const f = (y - y0) / band;
		const k = Math.min(n - 1, Math.floor(f));
		const into = (f - k) * band;
		for (let x = x0; x < x1; x++) {
			let c = colours[k];
			if (k < n - 1 && into > band - soft && (into - (band - soft)) / (soft + 1) > bayer(x, y)) c = colours[k + 1];
			p.set(x, y, c);
		}
	}
}

export const DAY = ['#6fbde6', '#8fcdee', '#addcf3', '#cdeaf7'].map((h) => rgba(h));
export const DUSK = ['#2a2850', '#3a3768', '#4b4680', '#5e5590'].map((h) => rgba(h));
export const NIGHT = ['#100e1c', '#17152a', '#1f1c37', '#282544'].map((h) => rgba(h));

/** A fluffy cloud, about `w` wide, lit from above. */
export function cloud(variant: number): Pix {
	return memo(`scenery:cloud:${variant}`, () => {
		const w = [26, 34, 20][variant % 3];
		const p = new Pix(w + 4, 12);
		const cx = (w + 4) / 2;
		const r = M.cloth;
		p.blob(cx, 7, w / 2.3, 3.6, r, { bias: 0.6 });
		p.blob(cx - w / 4.2, 6.5, w / 5, 3.4, r, { bias: 0.7 });
		p.blob(cx + w / 6, 5, w / 4.4, 4, r, { bias: 0.8 });
		// a flat, slightly shaded underside
		for (let x = 0; x < p.w; x++) {
			for (let y = 9; y < 12; y++) if (p.solid(x, y)) p.set(x, y, y === 9 ? r.c[1] : 0);
		}
		return p;
	});
}

/** A round sun with a pale ring, `r` pixels across the middle. */
export function sun(p: Pix, cx: number, cy: number, r: number): void {
	p.ellipse(cx, cy, r + 2, r + 2, mix(rgba('#fff3b0'), rgba('#cdeaf7'), 0.55));
	p.ellipse(cx, cy, r, r, (x, y) => ((x - cx + 1) ** 2 + (y - cy + 1) ** 2 < (r * 0.55) ** 2 ? rgba('#fffbe0') : rgba('#ffe58a')));
}

/** A ridge of hills along the scene: its top rises and falls by `amp` around `y`, filled down to `bottom`. */
export function hills(p: Pix, y: number, amp: number, bottom: number, r: Ramp, seed: number, freq = 1): void {
	for (let x = 0; x < p.w; x++) {
		const top = Math.round(y - amp * (0.55 + 0.3 * Math.sin((x * 0.045 + seed) * freq) + 0.15 * Math.sin((x * 0.13 + seed * 2.3) * freq)));
		for (let yy = top; yy < bottom; yy++) {
			const depth = yy - top;
			const c = depth === 0 ? r.c[3] : depth < 3 ? r.c[2] : noise(x >> 1, yy >> 1, seed) < 0.12 ? r.c[2] : r.c[1];
			p.set(x, yy, c, r.ink);
		}
	}
}

/** A far line of round treetops (and the odd coconut palm) standing on `baseY`, from x0 to x1. */
export function treeline(p: Pix, x0: number, x1: number, baseY: number, r: Ramp, seed: number, palms = true): void {
	let x = x0;
	let i = 0;
	while (x < x1) {
		const n = noise(i, 0, seed);
		if (palms && n > 0.86) {
			// a palm: a leaning trunk and a star of fronds
			const h = 9 + Math.round(noise(i, 1, seed) * 4);
			const lean = noise(i, 2, seed) > 0.5 ? 1 : -1;
			for (let k = 0; k < h; k++) p.set(x + Math.round((k * lean) / 4), baseY - k, M.bark.c[1]);
			const tx = x + Math.round((h * lean) / 4);
			const ty = baseY - h;
			for (const [dx, dy] of [[-3, 1], [-2, 0], [-1, 0], [1, 0], [2, 0], [3, 1], [-4, 2], [4, 2], [0, -1], [-1, -1], [1, -1]]) p.set(tx + dx, ty + dy, r.c[2], r.ink);
			x += 5;
		} else {
			const rad = 2.6 + n * 3.2;
			p.blob(x + rad, baseY - rad + 1, rad + 0.6, rad, r, { rim: false, bias: -0.2, grain: (a, b) => (noise(a, b, seed + i) - 0.5) * 1.2 });
			x += Math.max(3, Math.round(rad * 1.3));
		}
		i++;
	}
}

/**
 * Mirrors the rows above `surface` into the water below it, darkened towards the water's colour and
 * broken into short dashes, as a still lake reflects its far bank.
 */
export function reflect(p: Pix, surface: number, depth: number, water: Colour, seed: number): void {
	for (let d = 1; d <= depth; d++) {
		const y = surface + d;
		const src = surface - d;
		const wobble = d % 2 ? 1 : 0;
		const fade = 0.45 + (d / depth) * 0.45;
		for (let x = 0; x < p.w; x++) {
			const c = p.get(x + wobble, src);
			if (!c || noise(x >> 1, y, seed) < 0.18 + d / depth / 3) continue;
			p.set(x, y, mix(c, water, fade));
		}
	}
}

/** Single twinkling-white pixels and the odd plus-shaped bright star over a night sky. */
export function stars(p: Pix, y0: number, y1: number, density: number, seed: number): void {
	const bright = rgba('#fff6d8');
	const dim = rgba('#a8a4d0');
	for (let y = y0; y < y1; y++) {
		for (let x = 0; x < p.w; x++) {
			const n = noise(x, y, seed);
			if (n < density * 0.12) {
				p.set(x - 1, y, dim).set(x + 1, y, dim).set(x, y - 1, dim).set(x, y + 1, dim).set(x, y, bright);
			} else if (n < density) p.set(x, y, n < density * 0.5 ? bright : dim);
		}
	}
}

/** A crescent moon, `r` across. */
export function moon(p: Pix, cx: number, cy: number, r: number, sky: Colour): void {
	p.ellipse(cx, cy, r + 1.5, r + 1.5, mix(rgba('#fff3c4'), sky, 0.8));
	p.ellipse(cx, cy, r, r, rgba('#fff3c4'));
	p.ellipse(cx + r * 0.45, cy - r * 0.3, r * 0.85, r * 0.85, sky);
}

/** Grass with a ragged lighter top edge and darker speckle, from y down to `bottom`. */
export function grassland(p: Pix, y: number, bottom: number, seed: number, r: Ramp = M.grass, x0 = 0, x1 = p.w): void {
	for (let x = x0; x < x1; x++) {
		const lip = noise(x >> 1, 0, seed) < 0.3 ? 1 : 0;
		for (let yy = y - lip; yy < bottom; yy++) {
			const n = noise(x, yy, seed + 3);
			const c = yy <= y ? r.c[3] : n < 0.08 ? r.c[1] : n > 0.93 ? r.c[3] : r.c[2];
			p.set(x, yy, c, r.ink);
		}
	}
}

/** A little bird in two frames of flapping. */
export function bird(frame: number): Pix {
	return memo(`scenery:bird:${frame}`, () => {
		const c = rgba('#3a3346');
		return frame ? Pix.fromMap(['#...#', '.#.#.', '..#..'], { '#': c }) : Pix.fromMap(['.....', '##.##', '..#..'], { '#': c });
	});
}

/** A soft ground shadow colour. */
export const SHADE = pack(20, 12, 40, 70);

export { M, mix, noise, ramp, rgba };
