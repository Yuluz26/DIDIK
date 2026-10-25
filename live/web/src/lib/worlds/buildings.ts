/*
 * Kampung Kita's buildings in pixels, in the same front-and-above view as the other props: seven
 * buildings, an empty lot, and the materials waiting at a site. Each is 52 pixels square with its
 * foot at the middle of the bottom edge. The shops and the hall carry a word, set over the sign in
 * the pixel font.
 */
import { memo, sheetOf } from '$lib/pixel/cache';
import { M } from '$lib/pixel/palette';
import { Pix, type Ramp, noise, pack, ramp, rgba } from '$lib/pixel/pix';

export const B = { w: 52, h: 52 };

export interface BuildingArt {
	pix: Pix;
	sign?: { x: number; y: number; w: number; h: number; text: string; colour: string };
}

const glass = ramp(['#2f5a72', '#4b7f9a', '#7fb0c4', '#b8dcea', '#eaf8fc']);
const wall = ramp(['#a8793f', '#c79a58', '#dfb877', '#eed3a0', '#faebc8']);
const cream = M.cream;
const white = ramp(['#9a96b0', '#c8c4d8', '#e8e5f0', '#f8f6fb', '#ffffff']);

function window_(p: Pix, x: number, y: number, w: number, h: number, frame: Ramp = M.bark) {
	p.rect(x - 1, y - 1, w + 2, h + 2, frame.c[2], frame.ink);
	p.rect(x, y, w, h, glass.c[2], glass.ink);
	p.rect(x, y, w, 1, glass.c[4]);
	p.set(x + 1, y + 1, glass.c[4]);
	if (w >= 6) p.vline(x + Math.floor(w / 2), y, h, frame.c[2]);
}

function door(p: Pix, x: number, y: number, w: number, h: number, r: Ramp = M.bark) {
	p.rect(x, y, w, h, r.c[1], r.ink);
	p.vline(x, y, h, r.c[2], r.ink);
	p.rect(x + w - 2, y + Math.floor(h / 2), 1, 2, M.gold.c[3]);
}

function boards(p: Pix, x: number, y: number, w: number, h: number, r: Ramp, every = 4) {
	p.rect(x, y, w, h, r.c[2], r.ink);
	p.hline(x, y, w, r.c[3], r.ink);
	for (let yy = y + every; yy < y + h - 1; yy += every) p.hline(x, yy, w, r.c[1]);
	p.vline(x, y, h, r.c[3], r.ink);
	p.vline(x + w - 1, y, h, r.c[1], r.ink);
}

function roofTiles(p: Pix, pts: [number, number][], r: Ramp, split: number) {
	p.poly(
		pts,
		(x, y) => {
			const base = x < split ? r.c[3] : r.c[1];
			return y % 3 === 0 ? (x < split ? r.c[2] : r.c[0]) : base;
		},
		r.ink
	);
}

function rumah(): BuildingArt {
	const p = new Pix(B.w, B.h);
	p.shadow(26, 50, 22, 1.8);
	for (const x of [12, 25, 38]) p.cyl(x, 35, 2, 14, M.bark);
	p.rect(8, 33, 36, 3, M.plank.c[1], M.plank.ink);
	boards(p, 10, 22, 32, 11, M.plank, 4);
	window_(p, 14, 24, 6, 6);
	window_(p, 33, 24, 6, 6);
	door(p, 23, 23, 6, 10);
	for (let i = 0; i < 4; i++) p.rect(23 - i, 36 + i * 3, 6 + i * 2, 2, M.plank.c[2 + (i % 2)], M.plank.ink);
	roofTiles(p, [[3, 23], [26, 5], [49, 23]], M.roof, 26);
	p.poly([[22, 17], [26, 12], [30, 17]], M.cream.c[3], M.cream.ink);
	p.hline(3, 23, 46, M.roof.c[0], M.roof.ink);
	return { pix: p.outline() };
}

function kedai(): BuildingArt {
	const p = new Pix(B.w, B.h);
	p.shadow(26, 50, 22, 1.8);
	p.rect(6, 19, 40, 30, cream.c[3], cream.ink);
	p.vline(6, 19, 30, cream.c[4], cream.ink);
	p.vline(45, 19, 30, cream.c[1], cream.ink);
	const green = rgba('#2e7d4f');
	p.rect(5, 14, 42, 7, green, rgba('#164a2c'));
	p.hline(5, 14, 42, rgba('#4fa874'), rgba('#164a2c'));
	for (let i = 0; i < 7; i++) {
		const x = 6 + i * 6;
		p.poly([[x, 21], [x + 6, 21], [x + 6, 26], [x + 3, 28], [x, 26]], i % 2 ? rgba('#ffffff') : rgba('#3daa5c'), rgba('#164a2c'));
	}
	window_(p, 10, 31, 14, 9, M.bark);
	door(p, 33, 31, 10, 18);
	p.rect(9, 44, 16, 5, M.plank.c[2], M.plank.ink);
	for (const [x, c] of [[11, '#f28c28'], [15, '#ffd34d'], [19, '#e2483d'], [22, '#f28c28']] as const) p.ellipse(x, 43, 2, 2, rgba(c), rgba('#7a3a10'));
	return { pix: p.outline(), sign: { x: 6, y: 14, w: 40, h: 7, text: 'KEDAI RUNCIT', colour: '#ffffff' } };
}

function flag(p: Pix, x: number, y: number) {
	p.rect(x, y, 10, 7, rgba('#e2483d'), rgba('#7a1f1f'));
	for (const yy of [y + 2, y + 4]) p.hline(x, yy, 10, rgba('#ffffff'));
	p.rect(x, y, 5, 4, rgba('#1d3a8f'));
	p.set(x + 2, y + 2, rgba('#ffd34d'));
	p.set(x + 3, y + 1, rgba('#ffd34d'));
}

function sekolah(): BuildingArt {
	const p = new Pix(B.w, B.h);
	p.shadow(26, 50, 23, 1.8);
	boards(p, 3, 27, 46, 22, wall, 5);
	p.rect(3, 27, 46, 22, cream.c[3], cream.ink);
	p.vline(3, 27, 22, cream.c[4], cream.ink);
	p.vline(48, 27, 22, cream.c[1], cream.ink);
	p.poly([[1, 29], [7, 17], [45, 17], [51, 29]], (x, y) => (y < 20 ? M.sky.c[3] : y < 25 ? M.sky.c[2] : M.sky.c[1]), M.sky.ink);
	p.hline(7, 17, 38, M.sky.c[4], M.sky.ink);
	for (let i = 0; i < 4; i++) window_(p, 7 + i * 11 + (i > 1 ? 4 : 0), 32, 7, 6);
	door(p, 22, 40, 8, 9);
	p.vline(46, 2, 22, M.metal.c[3], M.metal.ink);
	flag(p, 37, 3);
	return { pix: p.outline() };
}

function jeti(): BuildingArt {
	const p = new Pix(B.w, B.h);
	p.ellipse(26, 41, 25, 9, M.water.c[2], M.water.ink);
	p.hline(8, 38, 8, M.water.c[3]);
	p.hline(32, 46, 8, M.water.c[3]);
	for (const x of [8, 39]) p.cyl(x, 36, 3, 11, M.bark);
	p.rect(4, 33, 44, 5, M.plank.c[2], M.plank.ink);
	p.hline(4, 33, 44, M.plank.c[4], M.plank.ink);
	for (let x = 10; x < 46; x += 8) p.vline(x, 33, 5, M.plank.c[1]);
	// a boat
	p.poly([[26, 42], [44, 42], [41, 47], [29, 47]], M.roof.c[2], M.roof.ink);
	p.hline(26, 42, 18, M.roof.c[4], M.roof.ink);
	p.vline(35, 28, 14, M.bark.c[2], M.bark.ink);
	p.poly([[36, 29], [36, 40], [44, 40]], rgba('#fff8ec'), M.cream.ink);
	// a hut
	boards(p, 7, 20, 14, 13, M.plank, 4);
	p.poly([[4, 21], [14, 10], [24, 21]], M.roof.c[2], M.roof.ink);
	p.poly([[14, 10], [24, 21], [14, 21]], M.roof.c[1], M.roof.ink);
	door(p, 12, 24, 5, 9);
	return { pix: p.outline() };
}

function masjid(): BuildingArt {
	const p = new Pix(B.w, B.h);
	p.shadow(26, 50, 23, 1.8);
	p.rect(6, 30, 32, 19, white.c[3], white.ink);
	p.hline(6, 30, 32, white.c[4], white.ink);
	p.rect(6, 30, 32, 3, white.c[2], white.ink);
	p.vline(6, 30, 19, white.c[4], white.ink);
	p.vline(37, 30, 19, white.c[1], white.ink);
	const green = ramp(['#0f5a30', '#1a7a44', '#1f9d55', '#4fd08a', '#a6f0c8']);
	p.blob(22, 29, 14, 11, green, { rim: true });
	p.vline(22, 12, 5, M.gold.c[3], M.gold.ink);
	p.set(21, 11, M.gold.c[4], M.gold.ink);
	p.set(23, 11, M.gold.c[4], M.gold.ink);
	for (const x of [10, 28]) {
		p.rect(x, 36, 6, 9, glass.c[2], glass.ink);
		p.ellipse(x + 3, 36, 3, 2.4, glass.c[2], glass.ink);
		p.set(x + 1, 37, glass.c[4]);
	}
	p.rect(19, 38, 6, 11, M.bark.c[1], M.bark.ink);
	p.ellipse(22, 38, 3, 2.4, M.bark.c[1], M.bark.ink);
	// the minaret
	p.rect(40, 16, 8, 33, white.c[3], white.ink);
	p.vline(40, 16, 33, white.c[4], white.ink);
	p.vline(47, 16, 33, white.c[1], white.ink);
	p.rect(40, 25, 8, 2, green.c[2], green.ink);
	p.poly([[39, 17], [44, 5], [49, 17]], green.c[2], green.ink);
	p.poly([[44, 5], [49, 17], [44, 17]], green.c[1], green.ink);
	p.set(44, 3, M.gold.c[3], M.gold.ink);
	p.rect(42, 31, 4, 5, glass.c[2], glass.ink);
	return { pix: p.outline() };
}

function rumahpanjang(): BuildingArt {
	const p = new Pix(B.w, B.h);
	p.shadow(26, 50, 24, 1.8);
	for (let i = 0; i < 6; i++) p.cyl(4 + i * 9, 36, 2, 13, M.bark);
	p.rect(2, 33, 48, 3, M.plank.c[1], M.plank.ink);
	boards(p, 2, 23, 48, 10, M.plank, 4);
	for (let i = 0; i < 5; i++) door(p, 6 + i * 9, 25, 5, 8, M.bark);
	p.poly([[0, 25], [7, 11], [45, 11], [52, 25]], (x, y) => (noise(x, y, 4) < 0.18 ? M.bark.c[0] : y < 15 ? M.bark.c[3] : y < 20 ? M.bark.c[2] : M.bark.c[1]), M.bark.ink);
	p.hline(7, 11, 38, M.bark.c[4], M.bark.ink);
	p.line(5, 15, 1, 8, M.bark.c[2], M.bark.ink);
	p.line(47, 15, 51, 8, M.bark.c[2], M.bark.ink);
	for (let i = 0; i < 3; i++) p.rect(21 + i, 37 + i * 4, 10 - i * 2, 2, M.plank.c[2 + (i % 2)], M.plank.ink);
	return { pix: p.outline() };
}

function balai(): BuildingArt {
	const p = new Pix(B.w, B.h);
	p.shadow(26, 50, 22, 1.8);
	p.rect(6, 27, 40, 22, cream.c[3], cream.ink);
	p.vline(6, 27, 22, cream.c[4], cream.ink);
	p.vline(45, 27, 22, cream.c[1], cream.ink);
	const orange = ramp(['#9a4a10', '#c4651a', '#e8821f', '#f4a548', '#ffcf86']);
	roofTiles(p, [[1, 29], [26, 8], [51, 29]], orange, 26);
	p.hline(1, 29, 50, orange.c[0], orange.ink);
	for (let i = 0; i < 4; i++) p.rect(8 + i * 10, 33, 3, 16, wall.c[3], wall.ink);
	const green = rgba('#1c6b4a');
	p.rect(15, 28, 22, 6, green, rgba('#0a3a28'));
	p.hline(15, 28, 22, rgba('#4fa874'), rgba('#0a3a28'));
	door(p, 22, 38, 8, 11);
	return { pix: p.outline(), sign: { x: 15, y: 28, w: 22, h: 6, text: 'BALAI RAYA', colour: '#ffffff' } };
}

/** An empty lot: a dashed outline on the grass and a signboard in the middle. */
export function plot(): Pix {
	const p = new Pix(B.w, B.h);
	const white = rgba('#ffffff');
	const dim = pack(255, 255, 255, 60);
	p.rect(5, 34, 42, 15, dim);
	for (let x = 5; x < 47; x++) if (x % 6 < 3) { p.set(x, 34, white); p.set(x, 48, white); }
	for (let y = 34; y < 49; y++) if (y % 6 < 3) { p.set(5, y, white); p.set(46, y, white); }
	p.cyl(25, 42, 2, 7, M.bark);
	p.rect(19, 36, 14, 7, M.plank.c[3], M.plank.ink);
	p.hline(19, 36, 14, M.plank.c[4], M.plank.ink);
	p.hline(21, 39, 10, M.bark.c[1]);
	return p.outline();
}

/** Planks and bricks stacked beside a building going up. */
export function materials(): Pix {
	const p = new Pix(B.w, B.h);
	p.rect(36, 44, 14, 3, M.plank.c[2], M.plank.ink);
	p.rect(38, 41, 11, 3, M.plank.c[3], M.plank.ink);
	p.rect(2, 43, 5, 4, M.roof.c[2], M.roof.ink);
	p.rect(8, 43, 5, 4, M.roof.c[2], M.roof.ink);
	p.rect(5, 39, 5, 4, M.roof.c[1], M.roof.ink);
	return p.outline();
}

const MAKERS: Record<string, () => BuildingArt> = { rumah, kedai, sekolah, jeti, masjid, rumahpanjang, balai };

export function buildingArt(kind: string): (BuildingArt & { sheet: ReturnType<typeof sheetOf> }) | null {
	const make = MAKERS[kind];
	if (!make) return null;
	return memo(`building:${kind}`, () => {
		const art = make();
		return { ...art, sheet: sheetOf(art.pix) };
	});
}

export const plotSheet = () => memo('building:plot', () => sheetOf(plot()));
export const materialsSheet = () => memo('building:materials', () => sheetOf(materials()));
