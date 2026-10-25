/*
 * The pixel painter: a small canvas of whole pixels that sprites are drawn into, one pixel at a time,
 * so every picture in the game is real pixel art in one palette (see palette.ts) and no shape is ever
 * smoothed. Sprites are painted once at 1x, then scaled by a whole number when they are shown
 * (cache.ts), so a pixel stays a block however large the screen is.
 *
 * Every painted pixel also remembers an `ink`: the dark tone of the material it belongs to. A sprite
 * finishes with `outline()`, which wraps its silhouette in that ink, so a leaf gets a dark green edge
 * and a plank a dark brown one, the way the reference art does, instead of one black line around all.
 */

/** 0xAABBGGRR: the byte order of canvas ImageData on every device that runs a browser. */
export type Colour = number;

export interface Ramp {
	/** Dark to light. */
	readonly c: readonly Colour[];
	/** The tone an outline takes around this material. */
	readonly ink: Colour;
}

export function pack(r: number, g: number, b: number, a = 255): Colour {
	return (((a & 255) << 24) | ((b & 255) << 16) | ((g & 255) << 8) | (r & 255)) >>> 0;
}

export function rgba(hex: string, a = 255): Colour {
	let h = hex.startsWith('#') ? hex.slice(1) : hex;
	if (h.length === 3) h = h[0] + h[0] + h[1] + h[1] + h[2] + h[2];
	const n = parseInt(h, 16);
	return pack((n >> 16) & 255, (n >> 8) & 255, n & 255, a);
}

export function unpack(c: Colour): [number, number, number, number] {
	return [c & 255, (c >>> 8) & 255, (c >>> 16) & 255, c >>> 24];
}

export function toHex(c: Colour): string {
	const [r, g, b] = unpack(c);
	return `#${((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1)}`;
}

export function mix(a: Colour, b: Colour, t: number): Colour {
	const [ar, ag, ab, aa] = unpack(a);
	const [br, bg, bb, ba] = unpack(b);
	return pack(
		Math.round(ar + (br - ar) * t),
		Math.round(ag + (bg - ag) * t),
		Math.round(ab + (bb - ab) * t),
		Math.round(aa + (ba - aa) * t)
	);
}

const COOL = rgba('#2a1f4a');
const WARM = rgba('#fff1bb');

/** A ramp of exactly the tones given, darkest first. The outline is the darkest tone, deepened. */
export function ramp(hexes: readonly string[], ink?: string): Ramp {
	const c = hexes.map((h) => rgba(h));
	return { c, ink: ink ? rgba(ink) : mix(c[0], COOL, 0.45) };
}

/** Five tones from one colour: shadows lean towards blue-violet, highlights towards warm light. */
export function rampFrom(hex: string): Ramp {
	const base = rgba(hex);
	return {
		c: [mix(base, COOL, 0.6), mix(base, COOL, 0.3), base, mix(base, WARM, 0.3), mix(base, WARM, 0.6)],
		ink: mix(base, COOL, 0.78)
	};
}

/** The same ramp with its tones in a different order or a different count: `pick([0, 2, 4])`. */
export function pick(r: Ramp, indexes: readonly number[]): Ramp {
	return { c: indexes.map((i) => r.c[i]), ink: r.ink };
}

const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];

/** Light comes from high up on the left, like everything else in the reference art. */
export const LIGHT: readonly [number, number, number] = [-0.45, -0.62, 0.64];

export function rng(seed: number): () => number {
	let a = seed >>> 0;
	return () => {
		a = (a + 0x6d2b79f5) >>> 0;
		let t = a;
		t = Math.imul(t ^ (t >>> 15), t | 1);
		t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}

/** A repeatable number in [0, 1) for a place, so textures do not change between draws. */
export function noise(x: number, y: number, seed = 0): number {
	let h = Math.imul(x | 0, 374761393) + Math.imul(y | 0, 668265263) + Math.imul(seed | 0, 2147483647);
	h = Math.imul(h ^ (h >>> 13), 1274126177);
	return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

export interface BlobOptions {
	light?: readonly [number, number, number];
	/** Moves the shading lighter (+) or darker (-), in tones. */
	bias?: number;
	/** 0..1: how much the edge between two tones is dithered. */
	dither?: number;
	/** A one-pixel rim in the darkest tone, so overlapping blobs read as separate leaves. */
	rim?: boolean;
	/** Nudges the tone at a pixel, in tones: leaves, speckle. */
	grain?: (x: number, y: number) => number;
	/** Turns the ellipse, in radians, about its centre. */
	angle?: number;
}

type Fill = Colour | ((x: number, y: number) => Colour);

export class Pix {
	readonly c: Uint32Array;
	readonly ink: Uint32Array;

	constructor(
		readonly w: number,
		readonly h: number
	) {
		this.c = new Uint32Array(w * h);
		this.ink = new Uint32Array(w * h);
	}

	/** A picture drawn as rows of characters: `legend` says which colour each one is; others are clear. */
	static fromMap(rows: readonly string[], legend: Readonly<Record<string, Colour>>): Pix {
		const p = new Pix(Math.max(...rows.map((r) => r.length)), rows.length);
		rows.forEach((row, y) => [...row].forEach((ch, x) => legend[ch] && p.set(x, y, legend[ch])));
		return p;
	}

	get(x: number, y: number): Colour {
		return x < 0 || y < 0 || x >= this.w || y >= this.h ? 0 : this.c[y * this.w + x];
	}

	/** Solid enough to be outlined (a soft shadow is not). */
	solid(x: number, y: number): boolean {
		return this.get(x, y) >>> 24 >= 200;
	}

	set(x: number, y: number, colour: Colour, ink = 0): this {
		x = Math.floor(x);
		y = Math.floor(y);
		if (x < 0 || y < 0 || x >= this.w || y >= this.h) return this;
		const i = y * this.w + x;
		this.c[i] = colour;
		this.ink[i] = ink;
		return this;
	}

	/** Lays a translucent colour over what is there (shadows, glints). */
	blend(x: number, y: number, colour: Colour): this {
		x = Math.floor(x);
		y = Math.floor(y);
		if (x < 0 || y < 0 || x >= this.w || y >= this.h) return this;
		const i = y * this.w + x;
		const under = this.c[i];
		const a = colour >>> 24;
		if (under === 0 || a === 255) this.c[i] = colour;
		else {
			const [r, g, b, ua] = unpack(under);
			const [cr, cg, cb] = unpack(colour);
			const t = a / 255;
			this.c[i] = pack(r + (cr - r) * t, g + (cg - g) * t, b + (cb - b) * t, Math.max(ua, a));
		}
		return this;
	}

	rect(x: number, y: number, w: number, h: number, fill: Fill, ink = 0): this {
		for (let j = 0; j < h; j++) {
			for (let i = 0; i < w; i++) this.set(x + i, y + j, typeof fill === 'function' ? fill(x + i, y + j) : fill, ink);
		}
		return this;
	}

	hline(x: number, y: number, w: number, colour: Colour, ink = 0): this {
		return this.rect(x, y, w, 1, colour, ink);
	}

	vline(x: number, y: number, h: number, colour: Colour, ink = 0): this {
		return this.rect(x, y, 1, h, colour, ink);
	}

	line(x0: number, y0: number, x1: number, y1: number, colour: Colour, ink = 0): this {
		x0 = Math.round(x0);
		y0 = Math.round(y0);
		x1 = Math.round(x1);
		y1 = Math.round(y1);
		const dx = Math.abs(x1 - x0);
		const dy = -Math.abs(y1 - y0);
		const sx = x0 < x1 ? 1 : -1;
		const sy = y0 < y1 ? 1 : -1;
		let err = dx + dy;
		for (;;) {
			this.set(x0, y0, colour, ink);
			if (x0 === x1 && y0 === y1) break;
			const e2 = 2 * err;
			if (e2 >= dy) {
				err += dy;
				x0 += sx;
			}
			if (e2 <= dx) {
				err += dx;
				y0 += sy;
			}
		}
		return this;
	}

	/** A flat ellipse (or a gradient, if `fill` is a function). */
	ellipse(cx: number, cy: number, rx: number, ry: number, fill: Fill, ink = 0): this {
		for (let y = Math.floor(cy - ry); y <= Math.ceil(cy + ry); y++) {
			for (let x = Math.floor(cx - rx); x <= Math.ceil(cx + rx); x++) {
				const nx = (x + 0.5 - cx) / rx;
				const ny = (y + 0.5 - cy) / ry;
				if (nx * nx + ny * ny <= 1) this.set(x, y, typeof fill === 'function' ? fill(x, y) : fill, ink);
			}
		}
		return this;
	}

	/** A filled polygon, tested at pixel centres. */
	poly(points: readonly (readonly [number, number])[], fill: Fill, ink = 0): this {
		let x0 = Infinity;
		let y0 = Infinity;
		let x1 = -Infinity;
		let y1 = -Infinity;
		for (const [x, y] of points) {
			x0 = Math.min(x0, x);
			y0 = Math.min(y0, y);
			x1 = Math.max(x1, x);
			y1 = Math.max(y1, y);
		}
		for (let y = Math.floor(y0); y <= Math.ceil(y1); y++) {
			for (let x = Math.floor(x0); x <= Math.ceil(x1); x++) {
				const px = x + 0.5;
				const py = y + 0.5;
				let inside = false;
				for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
					const [xi, yi] = points[i];
					const [xj, yj] = points[j];
					if (yi > py !== yj > py && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi) inside = !inside;
				}
				if (inside) this.set(x, y, typeof fill === 'function' ? fill(x, y) : fill, ink);
			}
		}
		return this;
	}

	/** A lit ball: foliage, bushes, rocks, hair. The tone follows the light, so it has a front. */
	blob(cx: number, cy: number, rx: number, ry: number, r: Ramp, o: BlobOptions = {}): this {
		const [lx, ly, lz] = o.light ?? LIGHT;
		const n = r.c.length;
		const cos = Math.cos(o.angle ?? 0);
		const sin = Math.sin(o.angle ?? 0);
		const local = (x: number, y: number): [number, number] => {
			const dx = x + 0.5 - cx;
			const dy = y + 0.5 - cy;
			return [(dx * cos + dy * sin) / rx, (-dx * sin + dy * cos) / ry];
		};
		const edge = (x: number, y: number) => {
			const [nx, ny] = local(x, y);
			return nx * nx + ny * ny > 1;
		};
		const reach = Math.max(rx, ry) + 1;
		for (let y = Math.floor(cy - reach); y <= Math.ceil(cy + reach); y++) {
			for (let x = Math.floor(cx - reach); x <= Math.ceil(cx + reach); x++) {
				const [nx, ny] = local(x, y);
				const d = nx * nx + ny * ny;
				if (d > 1) continue;
				// the light is fixed to the picture, so a turned ellipse keeps its highlight up and left
				const wx = nx * cos - ny * sin;
				const wy = nx * sin + ny * cos;
				const lit = Math.max(0, wx * lx + wy * ly + Math.sqrt(1 - d) * lz);
				let t = lit * n * 0.98 + (o.bias ?? 0) + (o.grain ? o.grain(x, y) : 0);
				if (o.dither) t += (BAYER[(y & 3) * 4 + (x & 3)] / 16 - 0.5) * o.dither * 1.6;
				let i = Math.floor(t);
				if (o.rim && (edge(x - 1, y) || edge(x + 1, y) || edge(x, y - 1) || edge(x, y + 1))) i = 0;
				this.set(x, y, r.c[Math.min(n - 1, Math.max(0, i))], r.ink);
			}
		}
		return this;
	}

	/** A round post or trunk: light on the left, dark on the right. */
	cyl(x: number, y: number, w: number, h: number, r: Ramp): this {
		const n = r.c.length;
		for (let i = 0; i < w; i++) {
			const t = w === 1 ? 0.3 : i / (w - 1);
			const tone = Math.min(n - 1, Math.max(0, Math.round(n - 2 - t * (n - 2.4))));
			this.rect(x + i, y, 1, h, r.c[tone], r.ink);
		}
		return this;
	}

	/** A block seen from the front and a little above: a lit top, a front, a darker right edge. */
	box(x: number, y: number, w: number, h: number, r: Ramp, top = 0): this {
		const n = r.c.length;
		this.rect(x, y, w, h, r.c[Math.min(n - 1, 2)], r.ink);
		if (top > 0) this.rect(x, y, w, top, r.c[n - 2], r.ink);
		this.vline(x, y + top, h - top, r.c[Math.min(n - 1, 3)], r.ink);
		this.vline(x + w - 1, y + top, h - top, r.c[1], r.ink);
		this.hline(x, y + h - 1, w, r.c[1], r.ink);
		return this;
	}

	/** Scatters single pixels of a colour over what is already painted (speckle, grain, stars). */
	speckle(colour: Colour, density: number, seed: number, where?: (x: number, y: number) => boolean): this {
		for (let y = 0; y < this.h; y++) {
			for (let x = 0; x < this.w; x++) {
				if (!this.solid(x, y) || (where && !where(x, y))) continue;
				if (noise(x, y, seed) < density) this.c[y * this.w + x] = colour;
			}
		}
		return this;
	}

	/** A soft ground shadow: translucent, so it never gets an outline. */
	shadow(cx: number, cy: number, rx: number, ry: number, alpha = 70): this {
		const dark = pack(20, 12, 40, alpha);
		for (let y = Math.floor(cy - ry); y <= Math.ceil(cy + ry); y++) {
			for (let x = Math.floor(cx - rx); x <= Math.ceil(cx + rx); x++) {
				const nx = (x + 0.5 - cx) / rx;
				const ny = (y + 0.5 - cy) / ry;
				if (nx * nx + ny * ny <= 1 && !this.solid(x, y)) this.blend(x, y, dark);
			}
		}
		return this;
	}

	/** Wraps the silhouette in the ink of the material next to it. */
	outline(fallback: Colour = rgba('#2a1f2d'), diagonal = false): this {
		const edits: [number, Colour][] = [];
		for (let y = 0; y < this.h; y++) {
			for (let x = 0; x < this.w; x++) {
				if (this.solid(x, y)) continue;
				let found = 0;
				const around: [number, number][] = [
					[0, 1],
					[1, 0],
					[-1, 0],
					[0, -1]
				];
				if (diagonal) around.push([1, 1], [-1, 1], [1, -1], [-1, -1]);
				for (const [dx, dy] of around) {
					if (this.solid(x + dx, y + dy)) {
						found = this.ink[(y + dy) * this.w + x + dx] || fallback;
						break;
					}
				}
				if (found) edits.push([y * this.w + x, found]);
			}
		}
		for (const [i, colour] of edits) {
			this.c[i] = colour;
			this.ink[i] = colour;
		}
		return this;
	}

	/** Copies another picture on top; `flip` mirrors it. Soft pixels blend. */
	stamp(src: Pix, dx: number, dy: number, flip = false): this {
		for (let y = 0; y < src.h; y++) {
			for (let x = 0; x < src.w; x++) {
				const col = src.c[y * src.w + (flip ? src.w - 1 - x : x)];
				if (!col) continue;
				const ink = src.ink[y * src.w + (flip ? src.w - 1 - x : x)];
				if (col >>> 24 === 255) this.set(dx + x, dy + y, col, ink);
				else this.blend(dx + x, dy + y, col);
			}
		}
		return this;
	}

	flipX(): Pix {
		const out = new Pix(this.w, this.h);
		out.stamp(this, 0, 0, true);
		return out;
	}

	crop(x: number, y: number, w: number, h: number): Pix {
		const out = new Pix(w, h);
		for (let j = 0; j < h; j++) {
			for (let i = 0; i < w; i++) {
				const s = (y + j) * this.w + x + i;
				if (x + i >= 0 && x + i < this.w && y + j >= 0 && y + j < this.h) {
					out.c[j * w + i] = this.c[s];
					out.ink[j * w + i] = this.ink[s];
				}
			}
		}
		return out;
	}

	/** Replaces one colour by another everywhere (a state change: a lamp lit, a chest opened). */
	swap(from: Colour, to: Colour): this {
		for (let i = 0; i < this.c.length; i++) if (this.c[i] === from) this.c[i] = to;
		return this;
	}

	toImageData(k = 1): ImageData {
		const W = this.w * k;
		const H = this.h * k;
		const img = new ImageData(W, H);
		const out = new Uint32Array(img.data.buffer);
		if (k === 1) out.set(this.c);
		else {
			for (let y = 0; y < this.h; y++) {
				for (let x = 0; x < this.w; x++) {
					const col = this.c[y * this.w + x];
					if (!col) continue;
					for (let dy = 0; dy < k; dy++) {
						const at = (y * k + dy) * W + x * k;
						out.fill(col, at, at + k);
					}
				}
			}
		}
		return img;
	}

	toCanvas(k = 1, into?: HTMLCanvasElement): HTMLCanvasElement {
		const canvas = into ?? document.createElement('canvas');
		canvas.width = this.w * k;
		canvas.height = this.h * k;
		canvas.getContext('2d')!.putImageData(this.toImageData(k), 0, 0);
		return canvas;
	}

	toURL(k = 1): string {
		return this.toCanvas(k).toDataURL('image/png');
	}
}
