/*
 * The pixels of the six newer games (Pancing Ikan, Lumba Wau, Kubu Pasir, Kereta Api Kampung, Pasar
 * Malam, Kejar Bintang): fish, a wau bulan, sandcastle floors, a steam train, a market stall and
 * stars, in the same palette and outlined the same way as every other sprite (pix.ts).
 */
import { memo, sheetOf, type Sheet } from '$lib/pixel/cache';
import { M } from '$lib/pixel/palette';
import { Pix, type Ramp, rampFrom, rgba } from '$lib/pixel/pix';

const INK = rgba('#2a1f2d');
const WHITE = rgba('#ffffff');

// ------------------------------------------------------------------ Pancing Ikan

const FISH_LOOK: Record<string, { body: Ramp; belly: string; fin: Ramp; w: number }> = {
	bilis: { body: rampFrom('#9fb7c9'), belly: '#e9f2f7', fin: rampFrom('#7f97ab'), w: 12 },
	puyu: { body: rampFrom('#7d9a52'), belly: '#d9e3a6', fin: rampFrom('#5d7a3c'), w: 14 },
	keli: { body: rampFrom('#5b5248'), belly: '#a89f8f', fin: rampFrom('#3d3630'), w: 18 },
	patin: { body: rampFrom('#9aa3ad'), belly: '#f0f2f4', fin: rampFrom('#6d7783'), w: 18 },
	kelah: { body: rampFrom('#c8783a'), belly: '#f3d19c', fin: rampFrom('#d24a3a'), w: 20 },
	arowana: { body: M.gold, belly: '#fff6b0', fin: rampFrom('#e0742a'), w: 22 }
};

/** A fish swimming to the left (or the old boot). */
export function fish(kind: string): Sheet {
	return memo(`fun:fish:${kind}`, () => {
		if (kind === 'kasut') {
			const p = new Pix(16, 12);
			p.rect(3, 1, 6, 7, M.bark.c[2], M.bark.ink);
			p.rect(3, 7, 12, 4, M.bark.c[2], M.bark.ink);
			p.hline(3, 10, 12, M.bark.c[0], M.bark.ink);
			p.hline(4, 2, 4, M.bark.c[3]);
			for (const x of [5, 7]) p.set(x, 4, M.cream.c[3]);
			p.outline();
			return sheetOf(p);
		}
		const look = FISH_LOOK[kind] ?? FISH_LOOK.bilis;
		const w = look.w;
		const h = Math.round(w * 0.55);
		const p = new Pix(w + 6, h + 2);
		const cy = (h + 2) / 2;
		// tail, then body, belly, fin and eye
		p.poly([[w - 1, cy], [w + 5, cy - h / 2], [w + 5, cy + h / 2]], look.fin.c[2], look.fin.ink);
		p.blob(w / 2, cy, w / 2, h / 2 - 0.2, look.body, { bias: 0.3 });
		p.ellipse(w / 2, cy + h / 5, w / 2.6, h / 5, rgba(look.belly));
		p.poly([[w / 2 - 2, cy - h / 2 + 1], [w / 2 + 3, cy - h / 2 - 1], [w / 2 + 4, cy - h / 2 + 2]], look.fin.c[3], look.fin.ink);
		p.set(Math.round(w / 5), Math.round(cy - 1), WHITE);
		p.set(Math.round(w / 5), Math.round(cy), INK);
		if (kind === 'keli') {
			p.line(1, cy + 1, -2, cy + 3, look.fin.c[1]);
			p.line(2, cy, 0, cy - 2, look.fin.c[1]);
		}
		p.outline();
		return sheetOf(p);
	});
}

// ------------------------------------------------------------------ Lumba Wau

const KITE_COLOURS = ['#e2483d', '#2f7fcf', '#f5c518', '#2bb0a6', '#8a5cd1', '#ec6ca5', '#6cb33f', '#e0742a'];

/** A wau bulan: the moon kite, its crescent tail and ribbons, in one of eight colours. */
export function kite(index: number): Sheet {
	const tone = KITE_COLOURS[((index % KITE_COLOURS.length) + KITE_COLOURS.length) % KITE_COLOURS.length];
	return memo(`fun:kite:${tone}`, () => {
		const r = rampFrom(tone);
		const p = new Pix(24, 30);
		// wings, head and the crescent "moon" at the foot
		p.poly([[12, 2], [22, 9], [12, 13], [2, 9]], r.c[2], r.ink);
		p.poly([[12, 3], [17, 8], [12, 10], [7, 8]], r.c[3], r.ink);
		p.poly([[9, 13], [15, 13], [13, 18], [11, 18]], r.c[1], r.ink);
		p.poly([[3, 17], [12, 22], [21, 17], [19, 23], [12, 26], [5, 23]], r.c[2], r.ink);
		p.vline(12, 2, 22, M.bark.c[3]);
		p.hline(4, 9, 16, M.bark.c[3]);
		p.set(12, 6, M.gold.c[4]);
		p.set(6, 20, M.gold.c[3]).set(18, 20, M.gold.c[3]);
		p.outline();
		// ribbons
		p.line(11, 26, 9, 29, M.gold.c[3]);
		p.line(13, 26, 15, 29, WHITE);
		return sheetOf(p);
	});
}

// ------------------------------------------------------------------ Kubu Pasir

/** One floor of a sandcastle, with a little window; the top floor has battlements. */
export function castleFloor(top: boolean): Sheet {
	return memo(`fun:floor:${top}`, () => {
		const p = new Pix(30, top ? 11 : 8);
		const y0 = top ? 3 : 0;
		p.rect(1, y0, 28, 8, M.sand.c[2], M.sand.ink);
		p.hline(1, y0, 28, M.sand.c[4], M.sand.ink);
		p.hline(1, y0 + 7, 28, M.sand.c[1], M.sand.ink);
		for (let x = 3; x < 28; x += 6) p.set(x, y0 + 3, M.sand.c[1]).set(x + 2, y0 + 5, M.sand.c[3]);
		p.rect(13, y0 + 2, 4, 4, M.sand.c[0], M.sand.ink);
		if (top) for (const x of [1, 8, 15, 22]) p.rect(x, 0, 5, 4, M.sand.c[3], M.sand.ink);
		p.outline();
		return sheetOf(p);
	});
}

/** A low sea wall of packed sand and shells. */
export function seaWall(): Sheet {
	return memo('fun:wall', () => {
		const p = new Pix(40, 8);
		p.rect(0, 2, 40, 6, M.sand.c[1], M.sand.ink);
		p.hline(0, 2, 40, M.sand.c[3], M.sand.ink);
		for (let x = 3; x < 40; x += 7) p.set(x, 4, M.pink.c[3]).set(x + 1, 4, M.pink.c[4]).set(x + 3, 6, M.cream.c[4]);
		p.outline();
		return sheetOf(p);
	});
}

export function flag(index: number): Sheet {
	const tone = ['#e2483d', '#f5c518', '#2f7fcf'][index % 3];
	return memo(`fun:flag:${tone}`, () => {
		const r = rampFrom(tone);
		const p = new Pix(8, 12);
		p.vline(1, 0, 12, M.bark.c[2], M.bark.ink);
		p.poly([[2, 1], [7, 3], [2, 6]], r.c[2], r.ink);
		p.outline();
		return sheetOf(p);
	});
}

// ------------------------------------------------------------------ Kereta Api Kampung

/** The little steam engine, facing right. */
export function engine(): Sheet {
	return memo('fun:engine', () => {
		const p = new Pix(34, 22);
		p.rect(2, 8, 22, 9, M.red.c[2], M.red.ink); // boiler
		p.hline(2, 8, 22, M.red.c[4], M.red.ink);
		p.rect(18, 3, 12, 14, M.sky.c[2], M.sky.ink); // cab
		p.rect(20, 5, 7, 5, M.water.c[4], M.sky.ink);
		p.rect(17, 1, 15, 3, M.sky.c[1], M.sky.ink);
		p.rect(5, 2, 4, 6, M.metal.c[2], M.metal.ink); // chimney
		p.rect(4, 1, 6, 2, M.metal.c[3], M.metal.ink);
		p.rect(0, 15, 34, 2, M.metal.c[1], M.metal.ink);
		for (const x of [6, 14, 25]) {
			p.ellipse(x, 18, 3.4, 3.4, M.metal.c[1], M.metal.ink);
			p.set(x, 18, M.gold.c[3]);
		}
		p.set(2, 11, M.gold.c[4]).set(2, 12, M.gold.c[4]);
		p.outline();
		return sheetOf(p);
	});
}

const CAR_COLOURS = ['#2bb0a6', '#f5c518', '#8a5cd1', '#ec6ca5', '#6cb33f', '#e0742a', '#2f7fcf'];

/** A passenger carriage; `riders` faces show in its windows. */
export function carriage(index: number, riders: number): Sheet {
	const tone = CAR_COLOURS[index % CAR_COLOURS.length];
	return memo(`fun:car:${tone}:${riders}`, () => {
		const r = rampFrom(tone);
		const p = new Pix(28, 20);
		p.rect(1, 3, 26, 12, r.c[2], r.ink);
		p.rect(0, 1, 28, 3, r.c[1], r.ink);
		p.hline(1, 14, 26, r.c[0], r.ink);
		for (let i = 0; i < 3; i++) {
			const x = 3 + i * 8;
			p.rect(x, 6, 6, 5, M.water.c[4], r.ink);
			if (i < riders) {
				p.ellipse(x + 3, 9, 1.8, 1.8, rgba('#e7b98a'));
				p.set(x + 2, 8, INK).set(x + 4, 8, INK);
			}
		}
		for (const x of [6, 22]) {
			p.ellipse(x, 17, 2.6, 2.6, M.metal.c[1], M.metal.ink);
			p.set(x, 17, M.metal.c[3]);
		}
		p.outline();
		return sheetOf(p);
	});
}

// ------------------------------------------------------------------ Pasar Malam

/** A night-market stall; each decoration shows (lamp, awning, sign, music). */
export function stall(decor: readonly string[], good: string): Sheet {
	const key = [...decor].sort().join(',');
	return memo(`fun:stall:${key}:${good}`, () => {
		const has = (d: string) => decor.includes(d);
		const p = new Pix(56, 46);
		// posts, counter and goods
		p.rect(5, 12, 3, 32, M.plank.c[1], M.plank.ink);
		p.rect(48, 12, 3, 32, M.plank.c[1], M.plank.ink);
		p.rect(2, 30, 52, 14, M.plank.c[2], M.plank.ink);
		p.hline(2, 30, 52, M.plank.c[4], M.plank.ink);
		for (let x = 6; x < 50; x += 6) p.vline(x, 32, 11, M.plank.c[1]);
		const goods = GOOD_TONE[good] ?? GOOD_TONE.satay;
		for (let i = 0; i < 6; i++) p.blob(10 + i * 7, 27, 2.6, 2.2, goods, { bias: 0.2 });
		// the roof: plain cloth, or a striped awning
		if (has('kanopi')) {
			for (let x = 0; x < 56; x++) p.vline(x, 6, 8, Math.floor(x / 5) % 2 ? M.red.c[2] : M.cream.c[3]);
			for (let x = 0; x < 56; x += 5) p.ellipse(x + 2.5, 14, 2.5, 1.6, Math.floor(x / 5) % 2 ? M.red.c[2] : M.cream.c[3]);
		} else {
			p.rect(0, 8, 56, 5, M.cloth.c[1], M.cloth.ink);
		}
		if (has('papan')) {
			p.rect(14, 0, 28, 6, M.night.c[2], M.night.ink);
			for (let x = 16; x < 40; x += 3) p.set(x, 2, M.pink.c[4]).set(x + 1, 3, M.sun.c[4]);
		}
		if (has('lampu')) for (let x = 6; x < 52; x += 7) p.ellipse(x, 17, 1.6, 1.6, M.sun.c[4], M.gold.ink);
		if (has('muzik')) {
			p.rect(50, 34, 6, 9, M.metal.c[2], M.metal.ink);
			p.ellipse(53, 38, 2, 2, M.metal.c[0], M.metal.ink);
		}
		p.outline();
		return sheetOf(p);
	});
}

const GOOD_TONE: Record<string, Ramp> = {
	satay: M.autumn,
	air: M.water,
	kuih: M.pink,
	jagung: M.gold,
	aiskrim: M.cloth
};

// ------------------------------------------------------------------ Kejar Bintang

/** A five-point star, gold or the pale grey of one not yet caught. */
export function star(lit: boolean): Sheet {
	return memo(`fun:star:${lit}`, () => {
		const r = lit ? M.gold : M.night;
		const p = new Pix(9, 9);
		p.poly([[4.5, 0], [5.8, 3.2], [9, 3.4], [6.5, 5.5], [7.4, 9], [4.5, 7], [1.6, 9], [2.5, 5.5], [0, 3.4], [3.2, 3.2]], r.c[lit ? 3 : 3], r.ink);
		if (lit) p.set(4, 3, M.gold.c[4]).set(5, 4, M.gold.c[4]);
		p.outline();
		return sheetOf(p);
	});
}
