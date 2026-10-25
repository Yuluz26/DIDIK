/*
 * Sprites are painted once at 1x, then turned into a picture at a whole-number magnification. The
 * magnification is the smallest whole number that covers the pixels the screen really has (CSS size
 * times the device's pixel ratio), so on screen the browser only ever shrinks a sharp picture by a
 * little: every pixel stays an even block, whatever size the world is drawn at.
 */
import type { Pix } from './pix';

/** Base pixels in one world tile. Everything in the worlds is measured in tiles of this size. */
export const TILE = 16;

/** A picture made of equal cells in a grid: an animation's frames, a character's views. */
export interface Sheet {
	pix: Pix;
	/** One cell, in base pixels. */
	cw: number;
	ch: number;
	cols: number;
	rows: number;
}

export function sheetOf(pix: Pix, cw = pix.w, ch = pix.h): Sheet {
	return { pix, cw, ch, cols: Math.round(pix.w / cw), rows: Math.round(pix.h / ch) };
}

const memos = new Map<string, unknown>();

/** Paints a thing once for a key and hands the same one out afterwards. */
export function memo<T>(key: string, make: () => T): T {
	if (!memos.has(key)) memos.set(key, make());
	return memos.get(key) as T;
}

const urls = new WeakMap<Pix, Map<number, string>>();

/** The picture of a sprite at a magnification, as a URL for an <img> or a background. */
export function urlOf(pix: Pix, k: number): string {
	let byK = urls.get(pix);
	if (!byK) urls.set(pix, (byK = new Map()));
	let url = byK.get(k);
	if (!url) byK.set(k, (url = pix.toURL(k)));
	return url;
}

const strips = new WeakMap<Pix, Pix[]>();

/**
 * The picture of one row of a sheet. Every row is its own image, so at the top and bottom edge of a
 * cell a row beside it can never show through, whatever fraction of a pixel the page lays it on.
 */
export function rowUrl(sheet: Sheet, row: number, k: number): string {
	if (sheet.rows === 1) return urlOf(sheet.pix, k);
	let rows = strips.get(sheet.pix);
	if (!rows) strips.set(sheet.pix, (rows = []));
	rows[row] ??= sheet.pix.crop(0, row * sheet.ch, sheet.pix.w, sheet.ch);
	return urlOf(rows[row], k);
}

export function pixelRatio(): number {
	return typeof window === 'undefined' ? 1 : window.devicePixelRatio || 1;
}

/** The whole-number magnification for a sprite shown at `s` CSS pixels per base pixel. */
export function prescale(s: number, max = 8): number {
	return Math.min(max, Math.max(1, Math.ceil(s * pixelRatio() - 0.01)));
}

/**
 * Snaps a size in CSS pixels per base pixel to whole, half or quarter steps, so a base pixel covers
 * a steady number of device pixels (whole numbers of them on most screens at the sizes children use).
 */
export function snapScale(raw: number, min = 1): number {
	// Large pixels move in half steps; below two, where a half step is a big jump, in quarter steps.
	const steps = raw < 2 ? 4 : 2;
	return Math.max(min, Math.floor(raw * steps + 1e-6) / steps);
}

/**
 * The size of a tile in CSS pixels for a world `cols` tiles wide in `avail` pixels (and, if given,
 * `rows` tall in `availH`): the largest whole or half step of the sprite scale that fits, never
 * below one base pixel per pixel nor above `max`.
 */
export function fitTile(avail: number, cols: number, o: { availH?: number; rows?: number; min?: number; max?: number } = {}): number {
	let raw = avail / cols;
	if (o.availH && o.rows) raw = Math.min(raw, o.availH / o.rows);
	const s = snapScale(Math.min(raw, o.max ?? 96) / TILE, o.min ?? 1);
	return s * TILE;
}
