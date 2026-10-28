/*
 * A child's character in pixels: a big-headed chibi in an animal hoodie. The hood tells you the
 * animal, the hoodie is the child's colour, the face has their skin tone, and a fringe of hair
 * (dark, with a few warm browns picked from the look, so friends do not all share one head) shows
 * under the rim. One sheet holds everything a world needs: four walking frames facing the viewer, away
 * from it and sideways (left; the right is a mirror), plus the face moods.
 *
 *   row 0  front walk x4      row 1  back walk x4      row 2  side walk x4 (facing left)
 *   row 3  cheer x2, oops, sleep (front)
 */
import { ANIMALS, COLOURS } from '$lib/names';
import { type Sheet, memo, sheetOf } from './cache';
import { BLUSH, EYE, HAIRS, M, WHITE, coat, skin } from './palette';
import { Pix, type Ramp, mix, pick, rampFrom, rgba } from './pix';

export const CW = 18;
export const CH = 32;
export type Mood = 'happy' | 'cheer' | 'oops' | 'sleep';
export const FRAMES = 4;
export const ROW = { front: 0, back: 1, side: 2, mood: 3 } as const;

interface Hood {
	base: Ramp;
	inner: Ramp;
}

const HOODS: Record<string, Hood> = {
	kancil: { base: rampFrom('#c98f5a'), inner: rampFrom('#f7c6c0') },
	harimau: { base: rampFrom('#f28c28'), inner: rampFrom('#fff0dc') },
	penyu: { base: rampFrom('#4fa35b'), inner: rampFrom('#b6e08a') },
	enggang: { base: rampFrom('#34303c'), inner: rampFrom('#f5c542') },
	gajah: { base: rampFrom('#9aa7b3'), inner: rampFrom('#efc6c6') },
	kucing: { base: rampFrom('#f1e8da'), inner: rampFrom('#f7b7b2') },
	arnab: { base: rampFrom('#f6f1f4'), inner: rampFrom('#f7b7b2') },
	beruang: { base: rampFrom('#6a4c3c'), inner: rampFrom('#e3b67a') }
};

const ANIMAL_INDEX = Object.keys(ANIMALS);

/** The same child always gets the same hair, wherever they are drawn. */
function hairFor(animal: string, colour: string, tone: string): Ramp {
	let h = 7;
	for (const ch of animal + colour + tone) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
	return HAIRS[h % HAIRS.length];
}

// The face opening of the hood, row by row from the top: [first x, last x].
const OPENING: [number, number][] = [
	[5, 12],
	[4, 13],
	[3, 14],
	[3, 14],
	[3, 14],
	[3, 14],
	[3, 14],
	[3, 14],
	[4, 13],
	[5, 12],
	[6, 11]
];
const HEAD_TOP = 7;
const FACE_TOP = 10;

interface Look {
	hood: Hood;
	coat: Ramp;
	skin: Ramp;
	hair: Ramp;
	animal: string;
}

function look(animal: string, colour: string, tone: string): Look {
	return { hood: HOODS[animal] ?? HOODS.kancil, coat: coat(colour), skin: skin(tone), hair: hairFor(animal, colour, tone), animal };
}

// ------------------------------------------------------------------ parts that sit behind the head

function earsBehind(p: Pix, l: Look, dy: number) {
	const { base, inner } = l.hood;
	const ear = (cx: number, cy: number, rx: number, ry: number) => {
		p.blob(cx, cy + dy, rx, ry, base, { rim: true });
		p.ellipse(cx, cy + dy + 0.4, Math.max(1, rx - 1.2), Math.max(1, ry - 1.4), inner.c[2]);
	};
	switch (l.animal) {
		case 'harimau':
		case 'beruang':
			ear(3.5, 9, 2.6, 2.6);
			ear(14.5, 9, 2.6, 2.6);
			break;
		case 'kancil':
			ear(3.2, 9.5, 2.2, 3.4);
			ear(14.8, 9.5, 2.2, 3.4);
			break;
		case 'arnab':
			ear(6.2, 5.2, 2.3, 5);
			ear(11.8, 5.2, 2.3, 5);
			break;
		case 'kucing': {
			const tri = (pts: [number, number][], inn: [number, number][]) => {
				p.poly(pts.map(([x, y]) => [x, y + dy]), base.c[2], base.ink);
				p.poly(inn.map(([x, y]) => [x, y + dy]), inner.c[2], base.ink);
			};
			tri([[2.5, 11], [3.5, 4.5], [8, 8.5]], [[3.6, 9.6], [4.2, 6.8], [6.2, 8.8]]);
			tri([[15.5, 11], [14.5, 4.5], [10, 8.5]], [[14.4, 9.6], [13.8, 6.8], [11.8, 8.8]]);
			break;
		}
		default:
			break;
	}
}

// ------------------------------------------------------------------ the head

function hood(p: Pix, l: Look, dy: number) {
	p.blob(9, HEAD_TOP + 7 + dy, 8, 7.2, l.hood.base, { rim: true });
}

function overlays(p: Pix, l: Look, dy: number, view: 'front' | 'back') {
	const { base, inner } = l.hood;
	const dark = rgba('#2a2024');
	const px = (x: number, y: number, c: number) => p.set(x, y + dy, c, base.ink);
	switch (l.animal) {
		case 'harimau':
			for (const [x, y] of [[8, 7], [9, 7], [8, 8], [9, 8], [5, 8], [12, 8], [6, 7], [11, 7]]) px(x, y, dark);
			if (view === 'front') for (const [x, y] of [[1, 13], [2, 13], [1, 15], [2, 15], [15, 13], [16, 13], [15, 15], [16, 15]]) px(x, y, dark);
			break;
		case 'penyu':
			for (const [x, y] of [[6, 7], [7, 8], [8, 7], [9, 7], [10, 8], [11, 7], [5, 9], [12, 9]]) px(x, y, l.hood.inner.c[2]);
			break;
		case 'enggang':
			p.rect(7, 3 + dy, 5, 3, inner.c[2], base.ink);
			p.rect(8, 2 + dy, 3, 1, rgba('#e2483d'), base.ink);
			p.set(7, 6 + dy, inner.c[3], base.ink);
			p.set(11, 6 + dy, inner.c[1], base.ink);
			px(9, 5, rgba('#f7d98a'));
			break;
		case 'kancil':
			for (const [x, y] of [[3, 12], [14, 12], [2, 15], [15, 15], [6, 8], [11, 8]]) px(x, y, inner.c[3]);
			break;
		case 'kucing':
			if (view === 'front') for (const [x, y] of [[10, 7], [11, 7], [12, 8], [13, 9], [11, 8], [12, 9], [12, 10]]) px(x, y, rgba('#f29c4b'));
			else p.rect(8, 8 + dy, 5, 3, rgba('#f29c4b'));
			break;
		case 'beruang':
			if (view === 'front') for (const [x, y] of [[8, 7], [9, 7], [7, 8], [8, 8], [9, 8], [10, 8]]) px(x, y, inner.c[2]);
			break;
		case 'gajah': {
			// Big floppy ears, over the sides of the hood.
			for (const [cx, sign] of [[2.2, -1], [15.8, 1]] as const) {
				p.blob(cx, 15 + dy, 2.7, 5, l.hood.base, { rim: true, bias: 0.4 });
				p.ellipse(cx - sign * 0.3, 15.3 + dy, 1.2, 3.2, inner.c[2]);
			}
			break;
		}
		default:
			break;
	}
}

/** The face in the hood's opening: skin, a fringe of hair, eyes, cheeks, a mouth. */
function face(p: Pix, l: Look, mood: Mood, dy: number) {
	const s = l.skin;
	OPENING.forEach(([a, b], i) => {
		for (let x = a; x <= b; x++) p.set(x, FACE_TOP + i + dy, i >= OPENING.length - 3 ? s.c[1] : s.c[2], s.ink);
	});
	// the rim of the hood around the opening, one pixel lighter, so the face looks set inside it
	OPENING.forEach(([a, b], i) => {
		p.set(a - 1, FACE_TOP + i + dy, l.hood.base.c[3], l.hood.base.ink);
		p.set(b + 1, FACE_TOP + i + dy, l.hood.base.c[1], l.hood.base.ink);
	});
	// fringe
	const hair = l.hair;
	for (let x = 5; x <= 12; x++) p.set(x, FACE_TOP + dy, hair.c[1], hair.ink);
	for (let x = 4; x <= 13; x++) p.set(x, FACE_TOP + 1 + dy, hair.c[1], hair.ink);
	for (const x of [3, 4, 5, 8, 9, 12, 13, 14]) p.set(x, FACE_TOP + 2 + dy, hair.c[1], hair.ink);
	for (const x of [3, 14]) p.set(x, FACE_TOP + 3 + dy, hair.c[1], hair.ink);
	p.set(6, FACE_TOP + 1 + dy, hair.c[3]);
	p.set(10, FACE_TOP + 1 + dy, hair.c[3]);

	const ey = FACE_TOP + 4 + dy;
	if (mood === 'cheer') {
		for (const x of [5, 11]) {
			p.set(x, ey + 1, EYE);
			p.set(x + 1, ey, EYE);
			p.set(x + 2, ey + 1, EYE);
		}
	} else if (mood === 'sleep') {
		for (const x of [5, 11]) p.rect(x, ey + 1, 3, 1, EYE);
	} else {
		const big = mood === 'oops';
		for (const x of [5, 11]) {
			p.rect(x, ey, 2, big ? 3 : 3, EYE);
			p.set(x, ey, WHITE);
			if (big) p.set(x + 1, ey + 2, EYE);
		}
	}
	for (const x of [4, 12]) p.rect(x, ey + 3, 2, 1, BLUSH);
	const my = ey + 4;
	if (mood === 'cheer') {
		p.rect(8, my - 1, 2, 1, rgba('#7a2b3a'));
		p.rect(8, my, 2, 1, rgba('#d04c5c'));
	} else if (mood === 'oops') p.rect(8, my - 1, 2, 2, rgba('#7a2b3a'));
	else if (mood !== 'sleep') p.rect(8, my, 2, 1, rgba('#9a4a50'));
	else p.rect(8, my, 2, 1, rgba('#b06a6a'));
}

// ------------------------------------------------------------------ the body

interface Pose {
	/** The upper body sits this many pixels higher (a step's bounce). */
	dy: number;
	/** Which foot is up: -1 the left (on screen), 1 the right, 0 neither. */
	lift: -1 | 0 | 1;
	/** How far the arms swing: the left goes down by `swing`, the right up. */
	swing: number;
	/** Both arms over the head. */
	cheer?: boolean;
}

const FRONT_POSES: Pose[] = [
	{ dy: 0, lift: 0, swing: 0 },
	{ dy: -1, lift: -1, swing: 1 },
	{ dy: 0, lift: 0, swing: 0 },
	{ dy: -1, lift: 1, swing: -1 }
];

const SHOE = rgba('#3c2f3a');
const SHOE_HI = rgba('#6a5868');
const PANTS = M.night;

function legsFront(p: Pix, pose: Pose) {
	for (const [i, x] of [[-1, 5], [1, 10]] as const) {
		const up = pose.lift === i ? 1 : 0;
		p.rect(x, 27 - up, 3, 3 + up - 1, PANTS.c[2], PANTS.ink);
		p.rect(x - 1, 29 - up, 4, 2, SHOE, PANTS.ink);
		p.set(x - 1, 29 - up, SHOE_HI, PANTS.ink);
	}
}

function bodyFront(p: Pix, l: Look, pose: Pose) {
	const c = l.coat;
	const dy = pose.dy;
	// arms first, so the hoodie overlaps their top
	const arm = (x: number, lift: number) => {
		if (pose.cheer) {
			p.rect(x, 17 + dy, 2, 6, c.c[1], c.ink);
			p.rect(x, 15 + dy, 2, 2, l.skin.c[2], l.skin.ink);
		} else {
			p.rect(x, 22 + dy + lift, 2, 4, c.c[1], c.ink);
			p.rect(x, 26 + dy + lift, 2, 2, l.skin.c[2], l.skin.ink);
		}
	};
	arm(2, pose.swing);
	arm(14, -pose.swing);
	p.rect(4, 21 + dy, 10, 6, c.c[2], c.ink);
	p.rect(4, 21 + dy, 10, 1, c.c[3], c.ink);
	p.vline(4, 22 + dy, 5, c.c[3], c.ink);
	p.vline(13, 22 + dy, 5, c.c[1], c.ink);
	p.hline(4, 26 + dy, 10, c.c[1], c.ink);
	// pocket and strings
	p.hline(7, 25 + dy, 4, c.c[1]);
	p.vline(8, 22 + dy, 2, WHITE);
	p.vline(9, 22 + dy, 2, WHITE);
}

function bodyBack(p: Pix, l: Look, pose: Pose) {
	const c = l.coat;
	const dy = pose.dy;
	const arm = (x: number, lift: number) => {
		p.rect(x, 22 + dy + lift, 2, 4, c.c[1], c.ink);
		p.rect(x, 26 + dy + lift, 2, 2, l.skin.c[2], l.skin.ink);
	};
	arm(2, pose.swing);
	arm(14, -pose.swing);
	p.rect(4, 21 + dy, 10, 6, c.c[2], c.ink);
	p.rect(4, 21 + dy, 10, 1, c.c[3], c.ink);
	p.vline(13, 22 + dy, 5, c.c[1], c.ink);
	p.hline(4, 26 + dy, 10, c.c[1], c.ink);
	// the hood hangs down the back
	p.rect(6, 21 + dy, 6, 3, l.hood.base.c[2], l.hood.base.ink);
	p.hline(6, 23 + dy, 6, l.hood.base.c[1], l.hood.base.ink);
}

function frontCell(p: Pix, l: Look, pose: Pose, mood: Mood) {
	const dy = pose.dy;
	p.shadow(9, 30.2, 6.5, 1.4);
	legsFront(p, pose);
	bodyFront(p, l, pose);
	earsBehind(p, l, dy);
	hood(p, l, dy);
	overlays(p, l, dy, 'front');
	face(p, l, mood, dy);
	p.outline();
}

function backCell(p: Pix, l: Look, pose: Pose) {
	const dy = pose.dy;
	p.shadow(9, 30.2, 6.5, 1.4);
	legsFront(p, pose);
	bodyBack(p, l, pose);
	earsBehind(p, l, dy);
	hood(p, l, dy);
	overlays(p, l, dy, 'back');
	// hair at the back of the neck, under the hood's edge
	for (let x = 5; x <= 12; x++) p.set(x, HEAD_TOP + 11 + dy, l.hair.c[1], l.hair.ink);
	for (let x = 6; x <= 11; x++) p.set(x, HEAD_TOP + 12 + dy, l.hair.c[1], l.hair.ink);
	// a seam down the middle of the hood
	p.vline(9, HEAD_TOP + 2 + dy, 8, l.hood.base.c[1]);
	p.outline();
}

// Side view faces left: the viewer sees the near arm and one leg forward, one back.
function sideCell(p: Pix, l: Look, frame: number) {
	const c = l.coat;
	const dy = frame % 2 ? -1 : 0;
	const phase = [0, 1, 0, -1][frame];
	p.shadow(9, 30.2, 5.5, 1.4);
	// legs scissor
	for (const [x, dir] of [[8, -1], [8, 1]] as const) {
		const off = phase * dir * 2;
		p.rect(x + off, 27, 3, 2, PANTS.c[dir === 1 ? 1 : 2], PANTS.ink);
		p.rect(x + off - 1, 29, 4, 2, SHOE, PANTS.ink);
		p.set(x + off - 1, 29, SHOE_HI, PANTS.ink);
	}
	// far arm, then body, then near arm
	p.rect(8 + phase, 22 + dy, 2, 4, c.c[1], c.ink);
	p.rect(5, 21 + dy, 8, 6, c.c[2], c.ink);
	p.rect(5, 21 + dy, 8, 1, c.c[3], c.ink);
	p.vline(5, 22 + dy, 5, c.c[3], c.ink);
	p.vline(12, 22 + dy, 5, c.c[1], c.ink);
	p.hline(5, 26 + dy, 8, c.c[1], c.ink);
	p.rect(7 - phase * 2, 22 + dy, 3, 4, c.c[3], c.ink);
	p.rect(7 - phase * 2, 26 + dy, 3, 2, l.skin.c[2], l.skin.ink);
	// ear behind the head, then the head: the hood's back is on the right, the face looks left
	if (l.animal === 'harimau' || l.animal === 'beruang') {
		p.blob(10, 9 + dy, 2.7, 2.7, l.hood.base, { rim: true });
		p.ellipse(10, 9.4 + dy, 1.3, 1.3, l.hood.inner.c[2]);
	} else if (l.animal === 'kancil') {
		p.blob(11, 9.5 + dy, 2.2, 3.4, l.hood.base, { rim: true });
		p.ellipse(11, 9.8 + dy, 1, 2, l.hood.inner.c[2]);
	} else if (l.animal === 'arnab') {
		p.blob(11, 5 + dy, 2.3, 5, l.hood.base, { rim: true });
		p.ellipse(11, 5.4 + dy, 1, 3.6, l.hood.inner.c[2]);
	} else if (l.animal === 'kucing') {
		p.poly([[8, 10], [10, 4], [14, 9]].map(([x, y]) => [x, y + dy] as [number, number]), l.hood.base.c[2], l.hood.base.ink);
		p.poly([[9.6, 9], [10.4, 6.4], [12.2, 8.8]].map(([x, y]) => [x, y + dy] as [number, number]), l.hood.inner.c[2], l.hood.base.ink);
	}
	p.blob(9.5, HEAD_TOP + 7 + dy, 7.4, 7.2, l.hood.base, { rim: true });
	if (l.animal === 'enggang') {
		p.rect(4, 3 + dy, 6, 3, l.hood.inner.c[2], l.hood.base.ink);
		p.rect(3, 2 + dy, 3, 1, rgba('#e2483d'), l.hood.base.ink);
	}
	if (l.animal === 'gajah') {
		p.blob(11, 15 + dy, 2.7, 5, l.hood.base, { rim: true, bias: 0.4 });
		p.ellipse(11, 15.3 + dy, 1.2, 3.2, l.hood.inner.c[2]);
	}
	if (l.animal === 'harimau') for (const [x, y] of [[8, 7], [9, 7], [12, 9], [13, 12], [13, 14]]) p.set(x, y + dy, rgba('#2a2024'), l.hood.base.ink);
	// the face: a profile opening on the left of the head
	const rows: [number, number][] = [[3, 8], [2, 9], [2, 10], [2, 10], [2, 10], [2, 10], [2, 10], [2, 10], [3, 9], [4, 8], [5, 8]];
	rows.forEach(([a, b], i) => {
		for (let x = a; x <= b; x++) p.set(x, FACE_TOP + i + dy, i >= rows.length - 3 ? l.skin.c[1] : l.skin.c[2], l.skin.ink);
	});
	rows.forEach(([a], i) => p.set(a - 1, FACE_TOP + i + dy, l.hood.base.c[3], l.hood.base.ink));
	const hair = l.hair;
	for (let x = 3; x <= 11; x++) p.set(x, FACE_TOP + dy, hair.c[1], hair.ink);
	for (let x = 2; x <= 11; x++) p.set(x, FACE_TOP + 1 + dy, hair.c[1], hair.ink);
	for (const x of [2, 3, 6, 7, 10, 11]) p.set(x, FACE_TOP + 2 + dy, hair.c[1], hair.ink);
	for (const x of [9, 10, 11]) p.set(x, FACE_TOP + 3 + dy, hair.c[1], hair.ink);
	p.rect(3, FACE_TOP + 4 + dy, 2, 3, EYE);
	p.set(3, FACE_TOP + 4 + dy, WHITE);
	p.rect(5, FACE_TOP + 7 + dy, 2, 1, BLUSH);
	p.rect(2, FACE_TOP + 8 + dy, 2, 1, rgba('#9a4a50'));
	p.outline();
}

// ------------------------------------------------------------------ the sheet

/** All of one child's character: every frame of every view. */
export function chibiSheet(animal: string, colour: string, tone: string): Sheet {
	return memo(`chibi:${animal}:${colour}:${tone}`, () => {
		const l = look(animal, colour, tone);
		const pix = new Pix(CW * FRAMES, CH * 4);
		const cell = (col: number, row: number, paint: (p: Pix) => void) => {
			const p = new Pix(CW, CH);
			paint(p);
			pix.stamp(p, col * CW, row * CH);
		};
		for (let f = 0; f < FRAMES; f++) {
			cell(f, ROW.front, (p) => frontCell(p, l, FRONT_POSES[f], 'happy'));
			cell(f, ROW.back, (p) => backCell(p, l, FRONT_POSES[f]));
			cell(f, ROW.side, (p) => sideCell(p, l, f));
		}
		cell(0, ROW.mood, (p) => frontCell(p, l, { dy: 0, lift: 0, swing: 0, cheer: true }, 'cheer'));
		cell(1, ROW.mood, (p) => frontCell(p, l, { dy: -2, lift: 0, swing: 0, cheer: true }, 'cheer'));
		cell(2, ROW.mood, (p) => frontCell(p, l, { dy: 0, lift: 0, swing: 0 }, 'oops'));
		cell(3, ROW.mood, (p) => frontCell(p, l, { dy: 1, lift: 0, swing: 0 }, 'sleep'));
		return sheetOf(pix, CW, CH);
	});
}

export const AW = 26;
export const AH = 34;

/** The whole child, head to shoes, standing in front of a round disc in their colour: lists, scoreboards, the HUD. */
export function avatarSheet(animal: string, colour: string, tone: string, mood: Mood = 'happy'): Sheet {
	return memo(`avatar:${animal}:${colour}:${tone}:${mood}`, () => {
		const full = chibiSheet(animal, colour, tone);
		const [col, row] = mood === 'cheer' ? [0, ROW.mood] : mood === 'oops' ? [2, ROW.mood] : mood === 'sleep' ? [3, ROW.mood] : [0, ROW.front];
		const src = full.pix.crop(col * CW, row * CH, CW, CH);
		const base = rgba(COLOURS[colour] ?? COLOURS.hijau);
		const tint = mix(base, rgba('#ffffff'), 0.74);
		const ring = mix(base, rgba('#2a1f4a'), 0.35);
		const p = new Pix(AW, AH);
		const inDisc = (x: number, y: number, r: number) => ((x + 0.5 - 13) / r) ** 2 + ((y + 0.5 - 15) / r) ** 2 <= 1;
		p.ellipse(13, 15, 12, 12, (x, y) => (inDisc(x, y, 10.6) ? tint : ring), ring);
		// every row of the child, so the legs and shoes stand below the disc
		for (let y = 0; y < CH; y++) {
			for (let x = 0; x < CW; x++) {
				const c = src.c[y * CW + x];
				const ay = y + 1;
				const ax = x + 4;
				if (!c || c >>> 24 < 200 || ay >= AH) continue;
				p.set(ax, ay, c, src.ink[y * CW + x]);
			}
		}
		return sheetOf(p, AW, AH);
	});
}

export { M, pick };
