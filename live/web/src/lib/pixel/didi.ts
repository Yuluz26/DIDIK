/*
 * Didi the mouse-deer, the mascot of DIDIK, in pixels: big ears turned outwards, big dark eyes, a
 * cream chin and a green scarf. Moods change the eyes, the mouth and the arms; `look` turns the eyes
 * toward something (the pointer); a closed-eyes copy of each is what a blink shows.
 */
import { type Sheet, memo, sheetOf } from './cache';
import { M } from './palette';
import { Pix, ramp, rampFrom, rgba } from './pix';

export const DIDI = { w: 44, h: 52 };
export type DidiMood = 'happy' | 'cheer' | 'think' | 'hint' | 'wave';

const fur = rampFrom('#e7b98a');
const pink = rampFrom('#f7a8a0');
const scarf = rampFrom('#1c6b4a');
const cream = M.cream;
const INK = rgba('#1f2d27');
const WHITE = rgba('#ffffff');
const dark = ramp(['#1f2d27', '#2f3f37', '#3f5248']);

function limb(p: Pix, x0: number, y0: number, x1: number, y1: number, r: number) {
	const steps = Math.ceil(Math.hypot(x1 - x0, y1 - y0));
	for (let i = 0; i <= steps; i++) {
		const t = steps ? i / steps : 0;
		p.blob(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, r, r, fur, { bias: 0.3 });
	}
}

function didi(mood: DidiMood, frame: number, look: [number, number], closed: boolean): Pix {
	const p = new Pix(DIDI.w, DIDI.h);
	const hop = mood === 'cheer' && frame === 1 ? -1 : 0;
	p.shadow(22, 50.5, 14, 1.6);

	// feet and body
	p.blob(14, 49.5, 4.4, 2.2, fur, { rim: true });
	p.blob(30, 49.5, 4.4, 2.2, fur, { rim: true });
	p.blob(22, 42 + hop, 15, 9, fur, { rim: true });
	p.blob(22, 45 + hop, 8, 6.2, cream, { rim: true, bias: 0.6 });
	for (const [x, y] of [[9, 42], [12, 47], [35, 42], [32, 47]]) p.blob(x, y + hop, 1.5, 1.5, cream, { bias: 1 });

	// arms
	if (mood === 'cheer') {
		limb(p, 9, 38 + hop, 3.5, 25 + hop, 2.6);
		limb(p, 35, 38 + hop, 40.5, 25 + hop, 2.6);
	} else if (mood === 'wave') {
		limb(p, 8, 42, 7, 46, 2.6);
		limb(p, 35, 38, frame ? 42 : 40, frame ? 28 : 25, 2.6);
	} else if (mood === 'think') {
		limb(p, 8, 42, 7, 46, 2.6);
		limb(p, 35, 40, 28, 34, 2.6);
	} else {
		limb(p, 8, 42, 7, 47, 2.6);
		limb(p, 36, 42, 37, 47, 2.6);
	}

	// the scarf, and its tail
	p.poly([[26, 33 + hop], [33, 34 + hop], [31, 44 + hop], [26, 41 + hop]], scarf.c[2], scarf.ink);
	p.hline(27, 35 + hop, 5, scarf.c[3]);
	p.ellipse(22, 33.5 + hop, 13.5, 3.2, (x, y) => (y < 33 + hop ? scarf.c[3] : scarf.c[2]), scarf.ink);

	// ears, turned outwards, then the head
	for (const [cx, sign] of [[7.5, 1], [36.5, -1]] as const) {
		p.blob(cx, 14 + hop, 9.5, 5.2, fur, { rim: true, angle: sign * 0.45 });
		p.blob(cx + sign * 0.6, 14 + hop, 6, 2.8, pink, { bias: 0.2, angle: sign * 0.45 });
	}
	p.blob(22, 22 + hop, 17, 13.5, fur, { rim: true });
	p.blob(22, 30 + hop, 10.5, 7.2, fur, { bias: 0.4 });
	p.blob(22, 33 + hop, 6.8, 3.8, cream, { rim: true, bias: 0.8 });
	p.ellipse(9.5, 27 + hop, 2.6, 2, pink.c[2]);
	p.ellipse(34.5, 27 + hop, 2.6, 2, pink.c[2]);

	// eyes
	const [lx, ly] = look;
	const eye = (cx: number) => {
		const x = cx + lx;
		const y = 21 + ly + hop;
		if (closed || mood === 'cheer') {
			if (mood === 'cheer') {
				p.set(x - 3, y, INK);
				p.set(x - 2, y - 1, INK);
				p.set(x - 1, y - 2, INK);
				p.set(x, y - 2, INK);
				p.set(x + 1, y - 1, INK);
				p.set(x + 2, y, INK);
				p.set(x + 3, y, INK);
			} else p.rect(x - 3, y + 1, 7, 1, INK);
			return;
		}
		p.ellipse(x, y, 3.3, 4.2, INK);
		p.rect(x - 2, y - 3, 2, 2, WHITE);
		p.set(x + 1, y + 2, WHITE);
	};
	eye(14.5);
	eye(29.5);
	if (mood === 'think') {
		p.line(10, 15 + hop, 16, 14 + hop, INK);
		p.line(16, 14 + hop, 18, 15 + hop, INK);
	} else if (mood === 'hint') {
		p.line(10, 16 + hop, 17, 14 + hop, INK);
		p.line(34, 16 + hop, 27, 14 + hop, INK);
	}

	// nose and mouth
	p.ellipse(22, 28.4 + hop, 2.8, 2, dark.c[1]);
	p.set(21, 27 + hop, WHITE);
	if (mood === 'cheer') {
		p.rect(19, 31 + hop, 6, 3, INK);
		p.rect(20, 33 + hop, 4, 1, pink.c[2]);
	} else if (mood === 'think') p.rect(24, 31 + hop, 2, 2, INK);
	else {
		p.set(19, 31 + hop, INK);
		p.set(20, 32 + hop, INK);
		p.set(21, 32 + hop, INK);
		p.set(22, 31 + hop, INK);
		p.set(23, 32 + hop, INK);
		p.set(24, 32 + hop, INK);
		p.set(25, 31 + hop, INK);
	}
	return p.outline();
}

/** Didi's picture: one cell per frame (the cheering and waving moods have two). */
export function didiSheet(mood: DidiMood, look: [number, number] = [0, 0], closed = false): Sheet {
	return memo(`didi:${mood}:${look}:${closed}`, () => {
		const frames = mood === 'cheer' || mood === 'wave' ? 2 : 1;
		const pix = new Pix(DIDI.w * frames, DIDI.h);
		for (let f = 0; f < frames; f++) pix.stamp(didi(mood, f, look, closed), f * DIDI.w, 0);
		return sheetOf(pix, DIDI.w, DIDI.h);
	});
}
