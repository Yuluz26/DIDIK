/*
 * Pulau Harta Karun in pixels: a small island of sand in a deep blue sea, the X marks and holes where
 * a child digs, and what is found there.
 */
import { TILE, memo, sheetOf } from '$lib/pixel/cache';
import { landMap, paintGround } from '$lib/pixel/ground';
import { M } from '$lib/pixel/palette';
import { Pix, ramp, rgba } from '$lib/pixel/pix';
import { propArt } from '$lib/pixel/props';

export const MARK = { w: 28, h: 16 };
export const LOOT = 16;

/** The sea, a shallow lagoon, the sandy island with its grass at the back. */
export function islandGround(W: number, H: number) {
	return memo(`island:${W}:${H}`, () => {
		const map = landMap(Array.from({ length: H }, () => 'd'.repeat(W)), { d: 'deep' });
		const cx = 7.4 * TILE;
		const cy = 5.7 * TILE;
		const blob = (grow: number, rx: number, ry: number) => (x: number, y: number) => {
			const dx = (x + 0.5 - cx) / (rx * TILE);
			const dy = (y + 0.5 - cy) / (ry * TILE);
			const a = Math.atan2(dy, dx);
			const wob = 1 + 0.045 * Math.sin(3 * a + 0.6) + 0.035 * Math.sin(5 * a + 2);
			return Math.hypot(dx, dy) <= (1 + grow) * wob;
		};
		return paintGround(map, {
			seed: 17,
			meadow: 0,
			shapes: [
				{ land: 'water', test: blob(0.14, 6.1, 4.1) },
				{ land: 'sand', test: blob(0, 5.7, 3.7) },
				{ land: 'grass', test: (x, y) => ((x + 0.5 - 7.4 * TILE) / (4.3 * TILE)) ** 2 + ((y + 0.5 - 3.25 * TILE) / (0.85 * TILE)) ** 2 <= 1 }
			]
		});
	});
}

/** A spot to dig: a mound of pale sand with a red X, bobbing when a shovel is ready. */
export function spotMark() {
	return memo('treasure:mark', () => {
		const p = new Pix(MARK.w, MARK.h);
		p.shadow(14, 12.5, 12, 2);
		p.blob(14, 9, 12.4, 4.8, M.sand, { rim: true, bias: 0.5, dither: 0.2 });
		p.blob(12, 7.4, 6, 2.4, M.sand, { bias: 1.4 });
		const red = rgba('#c0503a');
		for (const [x, y] of [[9, 4], [10, 5], [11, 6], [12, 7], [13, 8], [14, 9], [15, 8], [16, 7], [17, 6], [18, 5], [19, 4], [9, 9], [10, 8], [18, 8], [19, 9]]) p.set(x, y, red, M.red.ink);
		for (const [x, y] of [[10, 4], [11, 5], [12, 6], [18, 4], [17, 5], [16, 6]]) p.set(x, y, rgba('#e8785a'));
		return sheetOf(p.outline());
	});
}

/** A hole already dug: dark earth inside a rim of sand. */
export function spotHole() {
	return memo('treasure:hole', () => {
		const p = new Pix(MARK.w, MARK.h);
		p.shadow(14, 12.5, 12, 2);
		p.ellipse(14, 9, 12.2, 4.8, M.sand.c[2], M.sand.ink);
		p.hline(5, 6, 8, M.sand.c[3]);
		p.ellipse(14, 8.5, 8.6, 3.2, M.bark.c[1], M.bark.ink);
		p.ellipse(14, 9.2, 6.6, 2.2, M.bark.c[0]);
		p.rect(18, 6, 3, 1, M.bark.c[2]);
		return sheetOf(p.outline());
	});
}

const gold = M.gold;

function coins(): Pix {
	const p = new Pix(LOOT, LOOT);
	p.shadow(8, 14, 6.5, 1.2);
	for (const [x, y] of [[8, 12], [8, 10], [7, 8]]) {
		p.ellipse(x, y, 5.6, 2.6, gold.c[1], gold.ink);
		p.ellipse(x, y - 1, 5.6, 2.6, gold.c[3], gold.ink);
		p.hline(x - 3, y - 2, 3, gold.c[4]);
	}
	p.ellipse(11, 5.4, 3.6, 3.8, gold.c[3], gold.ink);
	p.vline(11, 3, 5, gold.c[1]);
	p.set(9, 4, gold.c[4]);
	return p.outline();
}

function gem(): Pix {
	const p = new Pix(LOOT, LOOT);
	const t = ramp(['#0a5a62', '#12807f', '#2bb0a6', '#6fd8c8', '#c4f6ea']);
	p.shadow(8, 14, 5.5, 1.1);
	p.poly([[4, 5], [12, 5], [15, 8.5], [8, 14.5], [1, 8.5]], t.c[2], t.ink);
	p.poly([[4, 5], [8, 5], [6, 8.5], [1, 8.5]], t.c[3]);
	p.poly([[8, 5], [12, 5], [15, 8.5], [10, 8.5]], t.c[1]);
	p.poly([[1, 8.5], [6, 8.5], [8, 14.5]], t.c[2]);
	p.poly([[10, 8.5], [15, 8.5], [8, 14.5]], t.c[0]);
	p.hline(5, 6, 3, t.c[4]);
	p.set(3, 8, t.c[4]);
	return p.outline();
}

function map(): Pix {
	const p = new Pix(LOOT, LOOT);
	p.shadow(8, 14.2, 6, 1);
	const paper = ramp(['#9a6e34', '#c79d58', '#e8cf90', '#f6e3b4', '#fff6d6']);
	p.rect(2, 3, 12, 10, paper.c[3], paper.ink);
	p.hline(2, 3, 12, paper.c[4], paper.ink);
	p.hline(2, 12, 12, paper.c[1], paper.ink);
	p.vline(5, 3, 10, paper.c[2]);
	p.vline(10, 3, 10, paper.c[2]);
	const red = rgba('#e8553f');
	for (const [x, y] of [[3, 10], [4, 9], [6, 9], [7, 10], [8, 9], [9, 8], [11, 8], [12, 7]]) p.set(x, y, red);
	for (const [x, y] of [[11, 5], [13, 5], [12, 6], [11, 7], [13, 7]]) p.set(x, y, red);
	return p.outline();
}

function parrot(): Pix {
	const p = new Pix(LOOT, LOOT);
	p.shadow(8, 14.4, 5, 1);
	p.vline(6, 12, 2, rgba('#e8a800'));
	p.vline(9, 12, 2, rgba('#e8a800'));
	p.blob(7.5, 8.4, 5, 5, M.red, { rim: true });
	p.blob(6, 9, 2.6, 3.6, ramp(['#0b5a56', '#12807f', '#2bb0a6', '#6fd8c8', '#c4f6ea']), { rim: true });
	p.blob(10, 4.6, 3, 3, M.red, { rim: true, bias: 0.3 });
	p.poly([[12, 3.5], [15, 5], [12, 6.4]], gold.c[3], gold.ink);
	p.set(10, 4, rgba('#ffffff'));
	p.set(10, 4, rgba('#241b2c'));
	return p.outline();
}

function crab(): Pix {
	const p = new Pix(LOOT, LOOT);
	p.shadow(8, 14, 6.5, 1.1);
	for (const dx of [-1, 1]) {
		for (let i = 0; i < 3; i++) p.line(8 + dx * 4, 11 + i, 8 + dx * (6 + i), 13 + i * 0.4, M.red.c[1], M.red.ink);
		p.blob(8 + dx * 6, 5.4, 2.4, 2.4, M.red, { rim: true });
		p.line(8 + dx * 4, 8, 8 + dx * 5.4, 6.4, M.red.c[1], M.red.ink);
	}
	p.blob(8, 10, 5.2, 3.2, M.red, { rim: true });
	p.set(6, 7, rgba('#ffffff'), M.red.ink);
	p.set(10, 7, rgba('#ffffff'), M.red.ink);
	p.set(6, 6, rgba('#241b2c'));
	p.set(10, 6, rgba('#241b2c'));
	return p.outline();
}

function pile(): Pix {
	const p = new Pix(LOOT, LOOT);
	p.shadow(8, 13.5, 6, 1);
	p.blob(8, 11, 6.4, 3.4, M.sand, { rim: true, bias: 0.2 });
	p.set(5, 10, M.sand.c[1]);
	p.set(10, 9, M.sand.c[1]);
	return p.outline();
}

const MAKE: Record<string, () => Pix> = { coins, gem, map, parrot, crab, sand: pile };

/** What a dig turns up; the chest is the same one that stands in the worlds. */
export function lootSprite(kind: string) {
	if (kind === 'chest') return propArt('chest', 0, 'open')!.sheet;
	const make = MAKE[kind] ?? pile;
	return memo(`loot:${kind}`, () => sheetOf(make()));
}

