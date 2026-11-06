/*
 * Pixel scenes: a whole picture painted on a small canvas of base pixels every frame (Scene.svelte),
 * so a fishing line, a wave or a kite's string lands on the same grid of pixels as every sprite and
 * nothing in the picture is ever smoothed. These helpers put Pix pictures, cells of a sheet, single
 * pixels, straight lines and sagging curves onto such a canvas, always on whole pixels.
 */
import type { Sheet } from './cache';
import { type Colour, Pix, mix, rgba, unpack } from './pix';

export type G = CanvasRenderingContext2D;

const canvases = new WeakMap<Pix, HTMLCanvasElement>();

/** A picture as a canvas at 1x, made once. */
export function canvasOf(pix: Pix): HTMLCanvasElement {
	let c = canvases.get(pix);
	if (!c) canvases.set(pix, (c = pix.toCanvas(1)));
	return c;
}

/** Draws a picture with its top-left corner at (x, y); `flip` mirrors it in place. */
export function put(g: G, pix: Pix, x: number, y: number, flip = false): void {
	const c = canvasOf(pix);
	x = Math.round(x);
	y = Math.round(y);
	if (!flip) g.drawImage(c, x, y);
	else {
		g.save();
		g.translate(x + pix.w, y);
		g.scale(-1, 1);
		g.drawImage(c, 0, 0);
		g.restore();
	}
}

/** Draws one cell of a sheet with its top-left corner at (x, y). */
export function cell(g: G, sheet: Sheet, col: number, row: number, x: number, y: number, flip = false): void {
	const c = canvasOf(sheet.pix);
	x = Math.round(x);
	y = Math.round(y);
	const [sx, sy, w, h] = [col * sheet.cw, row * sheet.ch, sheet.cw, sheet.ch];
	if (!flip) g.drawImage(c, sx, sy, w, h, x, y, w, h);
	else {
		g.save();
		g.translate(x + w, y);
		g.scale(-1, 1);
		g.drawImage(c, sx, sy, w, h, 0, 0, w, h);
		g.restore();
	}
}

const styles = new Map<Colour, string>();

/** A palette colour as a canvas fill style. */
export function css(c: Colour): string {
	let s = styles.get(c);
	if (!s) {
		const [r, gg, b, a] = unpack(c);
		styles.set(c, (s = `rgba(${r},${gg},${b},${(a / 255).toFixed(3)})`));
	}
	return s;
}

/** A hex colour (with an optional alpha 0..255) as a palette colour. */
export const hex = (h: string, a = 255): Colour => rgba(h, a);

export function dot(g: G, x: number, y: number, c: Colour): void {
	g.fillStyle = css(c);
	g.fillRect(Math.round(x), Math.round(y), 1, 1);
}

export function block(g: G, x: number, y: number, w: number, h: number, c: Colour): void {
	g.fillStyle = css(c);
	g.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h));
}

/** A one-pixel line, the way an old console draws one: every step a whole pixel. */
export function line(g: G, x0: number, y0: number, x1: number, y1: number, c: Colour): void {
	g.fillStyle = css(c);
	x0 = Math.round(x0);
	y0 = Math.round(y0);
	x1 = Math.round(x1);
	y1 = Math.round(y1);
	const dx = Math.abs(x1 - x0);
	const dy = -Math.abs(y1 - y0);
	const sx = x0 < x1 ? 1 : -1;
	const sy = y0 < y1 ? 1 : -1;
	let err = dx + dy;
	for (let guard = 0; guard < 4096; guard++) {
		g.fillRect(x0, y0, 1, 1);
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
}

/** A string or fishing line from a to b that hangs `sag` pixels below the straight way at its middle. */
export function sagLine(g: G, a: readonly [number, number], b: readonly [number, number], sag: number, c: Colour): void {
	const mx = (a[0] + b[0]) / 2;
	const my = (a[1] + b[1]) / 2 + sag * 2;
	const steps = Math.max(2, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / 3));
	let px = a[0];
	let py = a[1];
	for (let i = 1; i <= steps; i++) {
		const t = i / steps;
		const x = (1 - t) * (1 - t) * a[0] + 2 * (1 - t) * t * mx + t * t * b[0];
		const y = (1 - t) * (1 - t) * a[1] + 2 * (1 - t) * t * my + t * t * b[1];
		line(g, px, py, x, y, c);
		px = x;
		py = y;
	}
}

/** An ellipse's outline, one pixel thick: a ripple on water. */
export function ring(g: G, cx: number, cy: number, rx: number, ry: number, c: Colour): void {
	g.fillStyle = css(c);
	const seen = new Set<number>();
	const n = Math.max(12, Math.ceil((rx + ry) * 3));
	for (let i = 0; i < n; i++) {
		const a = (i / n) * Math.PI * 2;
		const x = Math.round(cx + Math.cos(a) * rx);
		const y = Math.round(cy + Math.sin(a) * ry);
		const k = x * 4096 + y;
		if (seen.has(k)) continue;
		seen.add(k);
		g.fillRect(x, y, 1, 1);
	}
}

const tintsOf = new WeakMap<Pix, Map<string, Pix>>();

/**
 * A picture as seen under water: every pixel leans towards the water's colour and lets some of it
 * through, so a fish swimming below the surface reads as below it.
 */
export function underwater(pix: Pix, water: Colour, amount = 0.5, alpha = 170): Pix {
	const key = `${water}:${amount}:${alpha}`;
	let byPix = tintsOf.get(pix);
	if (!byPix) tintsOf.set(pix, (byPix = new Map()));
	let out = byPix.get(key);
	if (!out) {
		out = new Pix(pix.w, pix.h);
		for (let i = 0; i < pix.c.length; i++) {
			const col = pix.c[i];
			if (!col) continue;
			const [r, g, b] = unpack(mix(col, water, amount));
			out.c[i] = ((alpha << 24) | (b << 16) | (g << 8) | r) >>> 0;
		}
		byPix.set(key, out);
	}
	return out;
}

/** Whether the person has asked for less movement on screen. */
export function stillWanted(): boolean {
	return typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/** A repeatable number in [0, 1) for an integer, for scattering things the same way every frame. */
export function hash(n: number, seed = 0): number {
	let h = Math.imul(n | 0, 374761393) + Math.imul(seed | 0, 668265263);
	h = Math.imul(h ^ (h >>> 13), 1274126177);
	return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}

/** Eases 0..1 in and out. */
export const ease = (t: number) => (t < 0 ? 0 : t > 1 ? 1 : t * t * (3 - 2 * t));

/** Time stepped into whole frames of `fps`, so movement jumps the way old games do. */
export const stepped = (t: number, fps: number) => Math.floor((t * fps) / 1000) / fps * 1000;
