/*
 * Kebun Ajaib's raised beds and crops in pixels. A crop is painted at four stages (a sprout, young,
 * grown, ready with its flowers or fruit) and stands on a bed, three small ones to a bed or one big
 * one; a drop for each watering it needs runs along the bed's front.
 */
import { memo, sheetOf } from '$lib/pixel/cache';
import { M } from '$lib/pixel/palette';
import { Pix, mix, pack, ramp, rgba } from '$lib/pixel/pix';

export const BED = { w: 46, h: 38 };
export const CROP = { w: 34, h: 40 };

const leaf = M.leaf;
const stalk = ramp(['#3a6a2a', '#4f8a38', '#6cb33f', '#8fd05e', '#c0eb8a']);

function sprout(p: Pix, cx: number, base: number) {
	p.ellipse(cx, base, 5, 1.6, M.bark.c[1], M.bark.ink);
	p.vline(cx, base - 5, 5, stalk.c[2], stalk.ink);
	p.blob(cx - 3, base - 6, 2.4, 1.5, leaf, { rim: true });
	p.blob(cx + 3, base - 7, 2.4, 1.5, leaf, { rim: true, bias: 0.4 });
}

function leafAt(p: Pix, x: number, y: number, dir: number, len: number, tone = 0) {
	for (let i = 0; i <= len; i++) {
		const t = i / len;
		p.blob(x + dir * i * 0.9, y - t * len * 0.35 + t * t * 2, 1.8 - t * 0.7, 1.2, leaf, { rim: true, bias: tone - t * 0.4 });
	}
}

function bunga(p: Pix, cx: number, base: number, t: number, ready: boolean) {
	const h = 8 + Math.round(t * 20);
	p.vline(cx, base - h, h, stalk.c[2], stalk.ink);
	leafAt(p, cx, base - h * 0.35, -1, 4 + t * 4, 0.2);
	leafAt(p, cx, base - h * 0.5, 1, 4 + t * 4, -0.2);
	if (t > 0.7) leafAt(p, cx, base - h * 0.8, -1, 3 + t * 3, 0.3);
	if (ready) {
		for (const [dx, dy, r] of [[0, -h - 3, 4.4], [-7, -h * 0.55, 3.2]] as const) {
			for (let a = 0; a < 5; a++) {
				const ang = (a * 72 * Math.PI) / 180;
				p.blob(cx + dx + Math.sin(ang) * r * 0.62, base + dy - Math.cos(ang) * r * 0.62, r * 0.55, r * 0.55, M.red, { rim: true, bias: 0.4 });
			}
			p.set(cx + dx, base + dy, M.gold.c[3], M.gold.ink);
			p.set(cx + dx + 1, base + dy - 1, M.gold.c[4]);
		}
	} else p.blob(cx, base - h - 2, 2, 3, leaf, { rim: true });
}

function cili(p: Pix, cx: number, base: number, t: number, ready: boolean) {
	const h = 8 + Math.round(t * 16);
	p.vline(cx, base - h, h, stalk.c[2], stalk.ink);
	p.line(cx, base - h * 0.5, cx - 5, base - h * 0.75, stalk.c[2], stalk.ink);
	p.line(cx, base - h * 0.6, cx + 5, base - h * 0.85, stalk.c[2], stalk.ink);
	leafAt(p, cx - 1, base - h * 0.9, -1, 3 + t * 4, 0.2);
	leafAt(p, cx + 1, base - h * 0.95, 1, 3 + t * 4, -0.1);
	leafAt(p, cx, base - h * 0.3, -1, 3 + t * 3);
	if (ready) {
		for (const [dx, dy] of [[-6, -h * 0.6], [6, -h * 0.7], [2, -h * 0.4], [-2, -h * 0.55]] as const) {
			p.vline(cx + dx, base + dy, 5, M.red.c[2], M.red.ink);
			p.set(cx + dx, base + dy + 5, M.red.c[1], M.red.ink);
			p.set(cx + dx, base + dy, stalk.c[1]);
			p.set(cx + dx - 1, base + dy + 1, M.red.c[4]);
		}
	}
}

function jagung(p: Pix, cx: number, base: number, t: number, ready: boolean) {
	const h = 10 + Math.round(t * 24);
	p.vline(cx, base - h, h, stalk.c[3], stalk.ink);
	p.vline(cx + 1, base - h, h, stalk.c[2], stalk.ink);
	for (const [f, dir] of [[0.25, -1], [0.45, 1], [0.65, -1], [0.8, 1]] as const) {
		if (t < 0.4 && f > 0.5) continue;
		for (let i = 0; i < 8 + t * 4; i++) {
			const tt = i / 11;
			p.blob(cx + dir * (2 + i * 0.9), base - h * f - i * 0.5 + tt * tt * 6, 1.7 - tt * 0.5, 1.1, leaf, { rim: true, bias: f * 0.6 - tt * 0.5 });
		}
	}
	for (const dx of [-2, 0, 2]) p.vline(cx + dx, base - h - 3, 3, rgba('#e8c06a'));
	if (ready) {
		for (const [dx, f] of [[3, 0.5], [-3, 0.7]] as const) {
			p.rect(cx + dx - 1, base - h * f - 4, 4, 9, rgba('#ffd34d'), M.gold.ink);
			p.vline(cx + dx - 1, base - h * f - 4, 9, rgba('#fff0a0'), M.gold.ink);
			p.rect(cx + dx - 1, base - h * f + 3, 4, 2, leaf.c[2], leaf.ink);
		}
	}
}

function tembikai(p: Pix, cx: number, base: number, t: number, ready: boolean) {
	for (let i = -12; i <= 12; i++) p.set(cx + i, base - 3 - Math.round(Math.sin(i / 3.2) * 1.4), stalk.c[1], stalk.ink);
	leafAt(p, cx - 9, base - 4, -1, 4 + t * 3, 0.2);
	leafAt(p, cx + 9, base - 4, 1, 4 + t * 3, -0.2);
	if (ready) {
		const stripe = rgba('#8fd05e');
		p.ellipse(cx, base - 7, 11, 6.4, (x, y) => ((x + (y >> 1)) % 6 < 2 ? stripe : rgba('#2e7d4f')), rgba('#123a24'));
		p.hline(cx - 7, base - 11, 6, rgba('#7fd0a0'));
		p.set(cx - 8, base - 10, rgba('#a8e8c0'));
	} else p.blob(cx, base - 5, 3.4, 3, leaf, { rim: true });
}

function durian(p: Pix, cx: number, base: number, t: number, ready: boolean) {
	const h = 10 + Math.round(t * 12);
	p.cyl(cx - 2, base - h, 4, h, M.bark);
	const r = 6 + t * 7;
	p.blob(cx, base - h - r * 0.5, r, r * 0.9, leaf, { rim: true, bias: -0.5 });
	p.blob(cx - r * 0.55, base - h - r * 0.25, r * 0.6, r * 0.55, leaf, { rim: true, bias: -0.2 });
	p.blob(cx + r * 0.55, base - h - r * 0.3, r * 0.6, r * 0.55, leaf, { rim: true, bias: -0.3 });
	p.blob(cx - r * 0.2, base - h - r * 0.9, r * 0.55, r * 0.45, leaf, { bias: 0.8 });
	if (ready) {
		for (const [dx, dy] of [[-7, -h - 2], [6, -h], [0, -h - 8]] as const) {
			p.blob(cx + dx, base + dy, 3.4, 3.4, ramp(['#6a7a14', '#8a9a28', '#b5c23a', '#d4e060', '#f0f6a0']), { rim: true });
			p.set(cx + dx - 2, base + dy - 2, rgba('#7a8a20'));
			p.set(cx + dx + 2, base + dy - 2, rgba('#7a8a20'));
			p.set(cx + dx, base + dy - 4, rgba('#7a8a20'));
			p.vline(cx + dx, base + dy - 6, 2, M.bark.c[2]);
		}
	}
}

const MAKE: Record<string, (p: Pix, cx: number, base: number, t: number, ready: boolean) => void> = { bunga, cili, jagung, tembikai, durian };

/** A crop at a growth stage: 0 a sprout, 1 young, 2 grown, 3 ready. The foot is the bottom centre. */
export function cropSheet(crop: string, stage: 0 | 1 | 2 | 3) {
	return memo(`crop:${crop}:${stage}`, () => {
		const p = new Pix(CROP.w, CROP.h);
		const cx = CROP.w / 2;
		const base = CROP.h - 3;
		if (stage === 0) sprout(p, cx, base);
		else (MAKE[crop] ?? bunga)(p, cx, base, stage === 1 ? 0.4 : stage === 2 ? 0.8 : 1, stage === 3);
		return sheetOf(p.outline());
	});
}

/** The stage a crop is drawn at from its watering progress. */
export function stageOf(grow: number, ready: boolean): 0 | 1 | 2 | 3 {
	if (ready) return 3;
	if (grow <= 0) return 0;
	return grow < 0.5 ? 1 : 2;
}

/** A raised bed, empty: soil in a frame of planks, or (locked) a plot of grass not yet bought. */
export function bedSheet(locked: boolean) {
	return memo(`bed:${locked}`, () => {
		const p = new Pix(BED.w, BED.h);
		if (locked) {
			p.ellipse(23, 26, 21, 9, mix(M.grass.c[2], M.grass.c[3], 0.4), M.grass.ink);
			for (const [x, y] of [[9, 24], [34, 21], [20, 31], [28, 26]]) {
				p.set(x, y, M.grass.c[1]);
				p.set(x + 1, y - 1, M.grass.c[1]);
				p.set(x + 2, y, M.grass.c[1]);
			}
			const white = rgba('#ffffff');
			for (let a = 0; a < 100; a++) {
				if (a % 5 > 2) continue;
				const t = (a / 100) * Math.PI * 2;
				p.set(23 + Math.cos(t) * 20.5, 26 + Math.sin(t) * 8.4, white);
			}
			p.rect(17, 21, 12, 10, M.cream.c[3], M.plank.ink);
			p.hline(17, 21, 12, M.cream.c[4], M.plank.ink);
			p.rect(22, 23, 2, 6, M.plank.c[1]);
			p.rect(20, 25, 6, 2, M.plank.c[1]);
			return sheetOf(p);
		}
		p.shadow(23, 36, 21, 1.6);
		// the soil, seen from above
		p.rect(3, 15, 40, 14, M.bark.c[1], M.bark.ink);
		for (const y of [18, 22, 26]) p.hline(5, y, 36, M.bark.c[0]);
		p.speckle(M.bark.c[2], 0.1, 3);
		// back rim, side rims, the front wall
		p.rect(1, 12, 44, 3, M.plank.c[3], M.plank.ink);
		p.hline(1, 12, 44, M.plank.c[4], M.plank.ink);
		p.rect(1, 14, 3, 15, M.plank.c[3], M.plank.ink);
		p.rect(42, 14, 3, 15, M.plank.c[2], M.plank.ink);
		p.rect(1, 28, 44, 8, M.plank.c[2], M.plank.ink);
		p.hline(1, 28, 44, M.plank.c[4], M.plank.ink);
		p.hline(1, 32, 44, M.plank.c[1]);
		p.hline(1, 35, 44, M.plank.c[1]);
		for (const x of [12, 23, 34]) p.vline(x, 28, 8, M.plank.c[1]);
		return sheetOf(p.outline());
	});
}

/** A drop of water on a bed's front: blue once given, a pale outline while still due. */
export function dropSheet(filled: boolean) {
	return memo(`drop:${filled}`, () => {
		const p = new Pix(7, 8);
		p.poly([[3.5, 0.5], [6.5, 4.6], [6, 6.6], [3.5, 7.5], [1, 6.6], [0.5, 4.6]], filled ? rgba('#4fc3f7') : pack(255, 255, 255, 190), filled ? rgba('#1d5a99') : rgba('#2f7fcf'));
		if (filled) p.set(2, 4, rgba('#c4efff'));
		return sheetOf(p);
	});
}

/** The glints on a bed whose crop is ready: two frames. */
export function sparkleSheet() {
	return memo('sparkle', () => {
		const p = new Pix(18, 9);
		const w = rgba('#fff6b0');
		for (const [ox, big] of [[0, true], [9, false]] as const) {
			const cx = ox + 4;
			p.set(cx, 4, w);
			for (const [dx, dy] of big ? [[0, -1], [0, 1], [-1, 0], [1, 0], [0, -2], [0, 2], [-2, 0], [2, 0]] : [[0, -1], [0, 1], [-1, 0], [1, 0]]) p.set(cx + dx, 4 + dy, w);
		}
		return sheetOf(p, 9, 9);
	});
}

/** The two things on sale in the garden shop: a bag of magic fertiliser and a new plot of land. */
export function shopSheet(key: string) {
	return memo(`shop:${key}`, () => {
		const p = new Pix(24, 24);
		if (key === 'baja') {
			p.poly([[5, 7], [19, 7], [21, 21], [3, 21]], M.plank.c[3], M.plank.ink);
			p.hline(5, 7, 14, M.plank.c[4], M.plank.ink);
			p.hline(6, 9, 12, M.plank.c[1]);
			p.blob(12, 15, 3.4, 4, leaf, { rim: true });
			p.vline(12, 12, 6, leaf.c[0]);
			for (const [x, y] of [[20, 3], [3, 4], [21, 11]]) {
				p.set(x, y, M.gold.c[3]);
				p.set(x - 1, y, M.gold.c[4]);
				p.set(x + 1, y, M.gold.c[4]);
				p.set(x, y - 1, M.gold.c[4]);
				p.set(x, y + 1, M.gold.c[4]);
			}
		} else {
			p.rect(2, 11, 20, 11, M.bark.c[1], M.bark.ink);
			p.hline(2, 11, 20, M.bark.c[3], M.bark.ink);
			for (const y of [14, 17, 20]) p.hline(4, y, 16, M.bark.c[0]);
			p.ellipse(18, 6, 5, 5, rgba('#1f9d55'), rgba('#0a3a28'));
			p.hline(15, 6, 7, rgba('#ffffff'));
			p.vline(18, 3, 7, rgba('#ffffff'));
		}
		return sheetOf(p.outline());
	});
}
