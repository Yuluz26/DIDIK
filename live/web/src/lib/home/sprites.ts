/*
 * The little pictures on the front page's islands that the games themselves do not use: a team
 * flag, the tick and cross on the jumping islets, a painter's easel, small hexagons, buoys and
 * the red cross that marks buried treasure.
 */
import { memo, sheetOf } from '$lib/pixel/cache';
import { M } from '$lib/pixel/palette';
import { Pix, rampFrom, rgba } from '$lib/pixel/pix';

const WHITE = rgba('#ffffff');

/** A round tick or cross, as the jumping game shows on a right and a wrong island. */
export function markBadge(yes: boolean) {
	return memo(`home:mark:${yes}`, () => {
		const p = new Pix(11, 11);
		const body = rampFrom(yes ? '#1f9d55' : '#e8553f');
		p.ellipse(5, 5, 5.2, 5.2, WHITE);
		p.blob(5, 5, 4.2, 4.2, body, { rim: false, bias: 0.2 });
		const marks = yes ? [[3, 5], [4, 6], [5, 7], [6, 6], [7, 5], [8, 4], [3, 4], [4, 5]] : [[3, 3], [4, 4], [5, 5], [6, 6], [7, 7], [7, 3], [6, 4], [4, 6], [3, 7]];
		for (const [x, y] of marks) p.set(x, y - (yes ? 1 : 0), WHITE);
		return sheetOf(p.outline());
	});
}

/** A flag on a pole, in two frames so it can flutter. */
export function flagSprite(colour: string) {
	return memo(`home:flag:${colour}`, () => {
		const W = 14;
		const H = 26;
		const p = new Pix(W * 2, H);
		const cloth = rampFrom(colour);
		for (let f = 0; f < 2; f++) {
			const q = new Pix(W, H);
			q.shadow(3, 24.5, 4, 1.1);
			q.vline(3, 1, 24, M.bark.c[2], M.bark.ink);
			q.vline(2, 1, 24, M.bark.c[3], M.bark.ink);
			const reach = f ? 8 : 10;
			const sag = f ? 1 : 0;
			q.poly([[4, 2], [4 + reach, 3 + sag], [4 + reach - 1, 6 + sag], [4 + reach, 9], [4, 9]], (x, y) => (y < 5 ? cloth.c[3] : cloth.c[2]), cloth.ink);
			q.set(3, 0, rgba('#ffd34d'), M.bark.ink);
			p.stamp(q.outline(), f * W, 0);
		}
		return sheetOf(p, W, H);
	});
}

const Q = ['##.', '..#', '.#.', '...', '.#.'];

/** A painter's easel with a landscape, some of its squares still covered. */
export function easelSprite() {
	return memo('home:easel', () => {
		const W = 34;
		const H = 40;
		const p = new Pix(W, H);
		p.shadow(17, 38.5, 12, 1.4);
		for (const [x0, x1] of [[8, 12], [26, 22]] as const) {
			p.line(x0, 38, x1, 26, M.bark.c[2], M.bark.ink);
			p.line(x0 + 1, 38, x1 + 1, 26, M.bark.c[1], M.bark.ink);
		}
		p.vline(17, 28, 10, M.bark.c[1], M.bark.ink);
		// the frame, the picture, then the covers
		p.rect(1, 1, 32, 26, M.bark.c[2], M.bark.ink);
		p.hline(1, 1, 32, M.bark.c[4], M.bark.ink);
		p.vline(1, 1, 26, M.bark.c[3], M.bark.ink);
		p.rect(4, 4, 26, 20, rgba('#cdebff'));
		p.ellipse(23, 9, 3, 3, rgba('#ffd34d'));
		p.poly([[4, 18], [10, 14], [16, 16], [22, 13], [30, 17], [30, 24], [4, 24]], rgba('#7dbe4e'));
		p.rect(9, 17, 8, 6, rgba('#c0503a'));
		p.poly([[8, 17], [13, 12], [18, 17]], rgba('#8c3b2b'));
		p.rect(12, 20, 2, 3, rgba('#fff4e6'));
		const cover = rgba('#ffb627');
		const edge = rgba('#ffd978');
		const dark = rgba('#b87200');
		for (const [i, j] of [[0, 0], [2, 0], [1, 1], [3, 1], [0, 2], [2, 2]] as const) {
			const x = 4 + i * 6.5;
			const y = 4 + j * 6.66;
			const w = i === 3 ? 6 : 6;
			p.rect(Math.round(x), Math.round(y), w, 6, cover);
			p.hline(Math.round(x), Math.round(y), w, edge);
			p.hline(Math.round(x), Math.round(y) + 5, w, dark);
			Q.forEach((row, r) => [...row].forEach((c, k) => c === '#' && p.set(Math.round(x) + 2 + k - 1, Math.round(y) + 1 + r - 0, dark)));
		}
		return sheetOf(p.outline());
	});
}

/** A flat hexagon, seen from a little above: grass or a team's colour. */
export function miniHex(colour: string | null) {
	return memo(`home:hex:${colour}`, () => {
		const p = new Pix(14, 12);
		const r = colour ? rampFrom(colour) : M.grass;
		const top = (dy: number): [number, number][] => [[7, dy], [13, dy + 2.5], [13, dy + 6], [7, dy + 8.5], [1, dy + 6], [1, dy + 2.5]];
		p.poly(top(2.5), r.c[1], r.ink);
		p.poly(top(0), (x, y) => (colour && (x + y) % 5 === 0 ? r.c[3] : r.c[2]), r.ink);
		p.line(1, 2, 7, 0, r.c[4]);
		p.line(7, 0, 13, 2, r.c[3]);
		return sheetOf(p.outline());
	});
}

/** A small red and white buoy. */
export function buoy() {
	return memo('home:buoy', () => {
		const p = Pix.sketch(['..kkk..', '.krrrk.', 'krwwrrk', 'kwwwwwk', 'krrrrrk', '.kkkkk.'], { k: '#2a1f2d', r: '#e2483d', w: '#ffffff' });
		const q = new Pix(9, 9);
		q.blend(4, 8, rgba('#0b3a55', 90));
		q.stamp(p, 1, 1);
		return sheetOf(q);
	});
}

/** The cross on the sand that says where to dig. */
export function digMark() {
	return memo('home:dig', () => {
		const p = new Pix(10, 8);
		const red = rgba('#d8452f');
		for (let i = 0; i < 6; i++) {
			for (const x of [2 + i, 3 + i, 7 - i, 8 - i]) p.set(x, 1 + i, red);
		}
		return sheetOf(p);
	});
}

/** A hole where someone has dug. */
export function hole() {
	return memo('home:hole', () => {
		const p = new Pix(12, 7);
		p.ellipse(6, 3.5, 5.5, 3, M.dirt.c[1], M.dirt.ink);
		p.ellipse(6, 3.8, 3.8, 1.8, M.bark.c[0]);
		p.hline(2, 1, 4, M.dirt.c[3]);
		return sheetOf(p);
	});
}
