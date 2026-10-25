/*
 * Things that stand in the worlds, painted in pixels: trees, benches, a fountain, a welcome arch.
 * Every picture is in a 3/4 view, front and top, with its foot at the bottom centre of its cell so
 * the world can sort it against the characters by how far down the screen it stands. Their sizes
 * keep the footprint they had before (in 16-pixel tiles), so every map keeps its layout.
 */
import { type Sheet, memo, sheetOf } from './cache';
import { M } from './palette';
import { Pix, type Ramp, noise, pack, ramp, rgba } from './pix';

export interface PropArt {
	sheet: Sheet;
	frames: number;
	/** The time one loop of the frames takes. */
	ms: number;
	/** Where the sign of a banner or arch is, in pixels of one cell, for text set over it. */
	sign?: { x: number; y: number; w: number; h: number };
}

const LEAVES: Ramp[] = [M.leaf, ramp(['#23564a', '#2f7656', '#43945f', '#69b36d', '#9ad088']), M.leaf];
const grain = (seed: number) => (x: number, y: number) => (noise(x, y, seed) - 0.5) * 1.5;

function clump(p: Pix, cx: number, cy: number, rx: number, ry: number, r: Ramp, seed: number, bias = 0) {
	p.blob(cx, cy, rx, ry, r, { rim: true, bias, grain: grain(seed), dither: 0.3 });
}

const RED = rgba('#e2483d');
const RED_HI = rgba('#ff7a6a');

function tree(variant: number): Pix {
	const p = new Pix(29, 37);
	const r = LEAVES[variant % 3];
	p.shadow(14.5, 35, 11, 2.2);
	p.cyl(13, 22, 4, 13, M.bark);
	p.rect(12, 33, 6, 2, M.bark.c[1], M.bark.ink);
	p.set(11, 34, M.bark.c[1], M.bark.ink);
	p.set(18, 34, M.bark.c[0], M.bark.ink);
	clump(p, 14.5, 15, 13, 11.5, r, 1, -0.9);
	clump(p, 8, 17.5, 7, 6.2, r, 2, -0.3);
	clump(p, 21, 18, 7, 6, r, 3, -0.6);
	clump(p, 14.5, 10, 8.8, 7.6, r, 4, 0);
	clump(p, 9.5, 9, 5.2, 4.4, r, 5, 0.5);
	clump(p, 18.5, 13, 4, 3.4, r, 6, -0.2);
	if (variant === 2) {
		for (const [x, y] of [[8, 16], [19, 19], [14, 13], [23, 14], [11, 21]]) {
			p.set(x, y, RED, M.leaf.ink);
			p.set(x + 1, y, RED, M.leaf.ink);
			p.set(x, y + 1, rgba('#b02a30'), M.leaf.ink);
			p.set(x + 1, y + 1, rgba('#b02a30'), M.leaf.ink);
			p.set(x, y, RED_HI);
		}
	}
	return p.outline();
}

function autumnTree(): Pix {
	const p = new Pix(29, 37);
	const r = M.autumn;
	p.shadow(14.5, 35, 11, 2.2);
	p.cyl(13, 22, 4, 13, M.bark);
	p.rect(12, 33, 6, 2, M.bark.c[1], M.bark.ink);
	clump(p, 14.5, 15, 13, 11.5, r, 31, -0.9);
	clump(p, 8, 17.5, 7, 6.2, r, 32, -0.3);
	clump(p, 21, 18, 7, 6, r, 33, -0.6);
	clump(p, 14.5, 10, 8.8, 7.6, r, 34, 0);
	clump(p, 9.5, 9, 5.2, 4.4, r, 35, 0.5);
	return p.outline();
}

function pine(variant: number): Pix {
	const p = new Pix(22, 38);
	const r = variant % 3 === 1 ? ramp(['#1d4a3c', '#2a6a4a', '#3d8858', '#5aa668', '#88c986']) : M.pine;
	p.shadow(11, 36.2, 8, 1.8);
	p.cyl(9, 31, 4, 6, M.bark);
	const tier = (apex: number, half: number, h: number) => {
		const mid = 11;
		const pts: [number, number][] = [[mid, apex]];
		const base = apex + h;
		// a jagged lower edge, like layers of needles
		for (let i = 0; i <= 8; i++) pts.push([mid + half - (i * 2 * half) / 8, base - (i % 2 ? 0 : 1.2)]);
		p.poly(
			pts,
			(x, y) => {
				const t = (x - mid) / half;
				const edge = noise(x, y, 41) < 0.12 ? 1 : 0;
				if (t < -0.35) return r.c[3 - edge];
				if (t > 0.35) return r.c[1 - (edge && 1 ? 1 : 0)];
				return r.c[2 + (y < apex + h * 0.25 ? 1 : 0) - edge];
			},
			r.ink
		);
		p.hline(mid - half + 1, base - 1, half * 2 - 1, r.c[0], r.ink);
	};
	tier(15, 10.4, 17);
	tier(8, 8.2, 14);
	tier(1, 5.6, 12);
	return p.outline();
}

function palm(): Pix {
	const p = new Pix(29, 40);
	p.shadow(14.5, 38, 9, 1.8);
	// a trunk that leans, in rings
	const pts: [number, number][] = [];
	for (let i = 0; i <= 26; i++) {
		const t = i / 26;
		const x = (1 - t) * (1 - t) * 12 + 2 * (1 - t) * t * 9 + t * t * 16.5;
		const y = (1 - t) * (1 - t) * 38 + 2 * (1 - t) * t * 24 + t * t * 13;
		pts.push([x, y]);
	}
	pts.forEach(([x, y], i) => {
		const w = 4 - Math.min(1.2, i / 14);
		for (let dx = 0; dx < w; dx++) p.set(x - w / 2 + dx, y, M.bark.c[dx < 1 ? 3 : dx >= w - 1 ? 1 : 2], M.bark.ink);
		if (i % 4 === 0) p.hline(x - w / 2, y, w, M.bark.c[1], M.bark.ink);
	});
	const [cx, cy] = [16.5, 13];
	const frond = (dx: number, dy: number, sag: number, shade: number) => {
		for (let i = 0; i <= 12; i++) {
			const t = i / 12;
			const x = cx + dx * t;
			const y = cy + dy * t + sag * t * t;
			const r = 2.6 - t * 1.7;
			p.blob(x, y, Math.max(0.9, r), Math.max(0.9, r * 0.8), M.leaf, { rim: true, bias: shade - t * 0.6 });
		}
	};
	frond(-14, 1, 8, 0.3);
	frond(12, 1, 8, -0.5);
	frond(-10, -9, 6, 0.6);
	frond(9, -10, 6, 0);
	frond(0, -11, 3, 0.5);
	frond(-6, 6, 8, -0.2);
	frond(6, 6, 8, -0.7);
	p.blob(15.2, 14.8, 1.8, 1.8, M.bark, { rim: true });
	p.blob(18.4, 15.4, 1.7, 1.7, M.bark, { rim: true, bias: -0.4 });
	return p.outline();
}

function bush(variant: number): Pix {
	const p = new Pix(19, 14);
	p.shadow(9.5, 12.5, 8, 1.4);
	clump(p, 5.4, 8, 5, 4.4, M.leaf, 51, -0.7);
	clump(p, 13.6, 8, 5, 4.4, M.leaf, 52, -0.6);
	clump(p, 9.5, 6, 6.6, 5, M.leaf, 53, 0);
	clump(p, 6.5, 4.6, 3, 2.4, M.leaf, 54, 0.8);
	if (variant % 2 === 0) {
		for (const [x, y, c] of [[4, 8, '#ff7aa2'], [11, 3, '#ffd34d'], [14, 8, '#ff7aa2'], [8, 9, '#fff4e6']] as const) {
			p.set(x, y, rgba(c), M.leaf.ink);
			p.set(x + 1, y, rgba(c), M.leaf.ink);
		}
	}
	return p.outline();
}

function rock(): Pix {
	const p = new Pix(18, 13);
	p.shadow(9, 11.6, 8, 1.4);
	p.blob(8.4, 7, 7.6, 5.2, M.stone, { rim: true, dither: 0.2 });
	p.blob(13.6, 8.2, 3.8, 3.2, M.stone, { rim: true, bias: -0.3 });
	p.blob(6, 4.6, 3.2, 1.8, M.stone, { bias: 1.2 });
	p.line(9, 8, 11, 6, M.stone.c[1]);
	p.line(11, 6, 11, 5, M.stone.c[1]);
	return p.outline();
}

function flowers(variant: number): Pix {
	const p = new Pix(14, 9);
	const heads: [number, number, string][] = variant % 2 ? [[3, 3, '#ffd34d'], [7, 1, '#ffffff'], [11, 3, '#ff7aa2']] : [[3, 3, '#ff7aa2'], [7, 1, '#ffffff'], [11, 3, '#c99cff']];
	for (const [x, y] of heads) p.vline(x, y + 1, 6, M.leaf.c[2], M.leaf.ink);
	p.hline(2, 7, 4, M.leaf.c[1], M.leaf.ink);
	p.hline(8, 7, 5, M.leaf.c[1], M.leaf.ink);
	for (const [x, y, c] of heads) {
		const col = rgba(c);
		for (const [dx, dy] of [[0, -1], [-1, 0], [1, 0], [0, 1]]) p.set(x + dx, y + dy, col, M.pink.ink);
		p.set(x, y, rgba('#ffe27a'), M.pink.ink);
	}
	return p.outline();
}

function mushroom(): Pix {
	const p = new Pix(10, 10);
	p.shadow(5, 8.8, 4, 1);
	p.rect(4, 5, 3, 4, rgba('#fff4e6'), M.cream.ink);
	p.set(4, 8, M.cream.c[0]);
	p.blob(5.5, 4.4, 4.6, 3.4, M.red, { rim: true });
	p.set(3, 3, rgba('#ffffff'));
	p.set(7, 2, rgba('#ffffff'));
	p.set(8, 4, rgba('#ffffff'));
	return p.outline();
}

function lamp(lit: boolean, frame = 0): Pix {
	const p = new Pix(10, 30);
	p.shadow(5, 28.4, 3.5, 1);
	if (lit) {
		const glow = pack(255, 226, 140, frame ? 56 : 44);
		for (let y = 0; y < 12; y++) {
			for (let x = 0; x < 10; x++) if (((x - 5) / 4.8) ** 2 + ((y - 6.5) / 5.6) ** 2 <= 1) p.blend(x, y, glow);
		}
	}
	p.cyl(4, 11, 2, 16, M.metal);
	p.rect(2, 26, 6, 2, M.metal.c[2], M.metal.ink);
	p.rect(3, 25, 4, 1, M.metal.c[3], M.metal.ink);
	p.rect(2, 4, 6, 7, M.metal.c[1], M.metal.ink);
	p.rect(3, 5, 4, 5, lit ? rgba('#ffe9a8') : rgba('#d8cfae'), M.metal.ink);
	if (lit) p.rect(4, 6, 2, 3, rgba('#fff8d6'));
	p.poly([[1.5, 4], [8.5, 4], [7, 1.5], [3, 1.5]], M.metal.c[2], M.metal.ink);
	return p.outline();
}

function bench(): Pix {
	const p = new Pix(22, 14);
	p.shadow(11, 12.6, 10, 1.3);
	for (const x of [3, 17]) p.rect(x, 8, 2, 5, M.metal.c[2], M.metal.ink);
	p.rect(1, 7, 20, 3, M.plank.c[2], M.plank.ink);
	p.hline(1, 7, 20, M.plank.c[4], M.plank.ink);
	p.hline(1, 9, 20, M.plank.c[1], M.plank.ink);
	p.rect(1, 2, 20, 2, M.plank.c[3], M.plank.ink);
	p.rect(1, 5, 20, 2, M.plank.c[2], M.plank.ink);
	p.hline(1, 3, 20, M.plank.c[1], M.plank.ink);
	p.hline(1, 6, 20, M.plank.c[1], M.plank.ink);
	return p.outline();
}

function sign(): Pix {
	const p = new Pix(18, 21);
	p.shadow(9, 19.6, 4, 1);
	p.cyl(7, 7, 3, 13, M.bark);
	p.poly([[1.5, 3], [13, 3], [16.5, 7], [13, 11], [1.5, 11]], M.plank.c[3], M.plank.ink);
	p.hline(2, 4, 11, M.plank.c[4], M.plank.ink);
	p.hline(2, 10, 11, M.plank.c[1], M.plank.ink);
	p.line(4, 7, 11, 7, M.bark.c[1]);
	p.line(9, 5, 11, 7, M.bark.c[1]);
	p.line(9, 9, 11, 7, M.bark.c[1]);
	return p.outline();
}

function fence(): Pix {
	const p = new Pix(17, 13);
	p.shadow(8.5, 11.8, 7.5, 1.1);
	p.rect(0, 5, 17, 2, M.plank.c[3], M.plank.ink);
	p.rect(0, 8, 17, 2, M.plank.c[2], M.plank.ink);
	for (const x of [1, 12]) {
		p.rect(x, 2, 3, 10, M.plank.c[2], M.plank.ink);
		p.vline(x, 2, 10, M.plank.c[3], M.plank.ink);
		p.vline(x + 2, 2, 10, M.plank.c[1], M.plank.ink);
		p.hline(x, 2, 3, M.plank.c[4], M.plank.ink);
	}
	return p.outline();
}

function stump(): Pix {
	const p = new Pix(14, 10);
	p.shadow(7, 8.8, 6, 1.2);
	p.cyl(2, 4, 10, 4, M.bark);
	p.ellipse(7, 4, 5.2, 2.4, M.plank.c[3], M.bark.ink);
	p.ellipse(7, 4, 3.2, 1.3, M.plank.c[3], M.bark.ink);
	p.hline(5, 4, 4, M.plank.c[1]);
	p.rect(3, 7, 8, 1, M.bark.c[1], M.bark.ink);
	return p.outline();
}

function reeds(): Pix {
	const p = new Pix(13, 14);
	for (const [x, top, lean] of [[3, 3, -1], [6, 0, 0], [10, 5, 1]] as const) {
		for (let y = top; y < 13; y++) p.set(x + Math.round((lean * (13 - y)) / 6), y, M.leaf.c[y % 3 ? 2 : 1], M.leaf.ink);
	}
	p.rect(5, 1, 3, 4, M.bark.c[2], M.bark.ink);
	p.vline(5, 1, 4, M.bark.c[3], M.bark.ink);
	return p.outline();
}

function lily(): Pix {
	const p = new Pix(13, 6);
	p.ellipse(6, 3.5, 5.4, 2.2, M.leaf.c[2], M.leaf.ink);
	p.hline(2, 2, 6, M.leaf.c[3]);
	p.poly([[6, 3.5], [12, 1.8], [12, 4]], M.water.c[2]);
	p.rect(8, 1, 3, 2, rgba('#ff9ec4'), M.pink.ink);
	p.set(9, 1, rgba('#fff4e6'));
	return p.outline();
}

function chest(state: string): Pix {
	const p = new Pix(15, 14);
	p.shadow(7.5, 12.6, 6.5, 1.1);
	const wood = state === 'locked' ? M.stone : ramp(['#5a2a1d', '#8a3a28', '#b04a30', '#cf6a40', '#e88a58']);
	if (state === 'open') {
		p.rect(1, 6, 13, 7, wood.c[2], wood.ink);
		p.hline(1, 6, 13, wood.c[1], wood.ink);
		p.vline(1, 6, 7, wood.c[3], wood.ink);
		p.vline(13, 6, 7, wood.c[1], wood.ink);
		p.hline(1, 12, 13, wood.c[0], wood.ink);
		p.rect(2, 2, 11, 5, wood.c[3], wood.ink);
		p.rect(3, 3, 9, 3, wood.c[1], wood.ink);
		p.ellipse(7.5, 6.4, 5, 1.8, M.gold.c[3], M.gold.ink);
		p.set(5, 6, rgba('#fff6b0'));
		p.set(9, 5, rgba('#fff6b0'));
		p.set(7, 4, rgba('#fff6b0'));
	} else {
		p.rect(1, 6, 13, 7, wood.c[2], wood.ink);
		p.vline(1, 6, 7, wood.c[3], wood.ink);
		p.vline(13, 6, 7, wood.c[1], wood.ink);
		p.hline(1, 12, 13, wood.c[0], wood.ink);
		p.blob(7.5, 6.4, 6.5, 4.4, wood, { rim: true, bias: 0.6 });
		p.hline(1, 6, 13, wood.c[0], wood.ink);
		p.vline(4, 3, 9, wood.c[0]);
		p.vline(11, 3, 9, wood.c[0]);
		p.rect(6, 6, 3, 4, state === 'locked' ? M.metal.c[3] : M.gold.c[3], M.gold.ink);
		p.set(7, 8, M.metal.c[0]);
	}
	return p.outline();
}

function gate(open: boolean): Pix {
	const p = new Pix(42, 46);
	p.shadow(21, 44, 19, 1.6);
	for (const x of [3, 33]) {
		p.cyl(x, 6, 5, 38, M.bark);
		p.rect(x - 1, 42, 7, 2, M.bark.c[1], M.bark.ink);
	}
	if (open) {
		p.rect(8, 14, 25, 30, rgba('#bfe8a5'), M.leaf.ink);
		p.rect(9, 16, 23, 3, rgba('#d8f2c4'));
		p.poly([[8, 15], [3, 18], [3, 43], [8, 41]], M.plank.c[3], M.plank.ink);
		p.poly([[33, 15], [38, 18], [38, 43], [33, 41]], M.plank.c[2], M.plank.ink);
	} else {
		p.rect(8, 14, 25, 30, M.plank.c[2], M.plank.ink);
		for (const y of [20, 27, 34]) p.hline(8, y, 25, M.plank.c[1], M.plank.ink);
		p.vline(20, 14, 30, M.plank.c[1], M.plank.ink);
		p.rect(18, 26, 5, 5, M.gold.c[3], M.gold.ink);
		p.set(20, 28, M.metal.c[0]);
	}
	p.rect(1, 3, 40, 6, M.roof.c[2], M.roof.ink);
	p.hline(1, 3, 40, M.roof.c[4], M.roof.ink);
	p.hline(1, 8, 40, M.roof.c[1], M.roof.ink);
	p.rect(12, 9, 18, 3, M.bark.c[2], M.bark.ink);
	return p.outline();
}

function hibiscus(): Pix {
	const p = new Pix(16, 15);
	p.shadow(8, 13.6, 7, 1.2);
	clump(p, 4.8, 9.4, 4.6, 4.2, M.leaf, 61, -0.7);
	clump(p, 11.2, 9.4, 4.6, 4.2, M.leaf, 62, -0.6);
	clump(p, 8, 6.4, 5.6, 4.8, M.leaf, 63, 0);
	for (const [x, y, s] of [[4, 7, 2.4], [11, 5, 2.6], [9, 10, 2]] as const) {
		for (const [dx, dy] of [[0, -1], [-1, 0], [1, 0], [0, 1], [-1, -1], [1, 1]]) p.set(x + dx * (s > 2.2 ? 1 : 0.8), y + dy, RED, M.red.ink);
		p.set(x, y, rgba('#ffd34d'), M.red.ink);
		p.set(x - 1, y - 1, RED_HI);
	}
	return p.outline();
}

function pelita(frame: number): Pix {
	const p = new Pix(13, 22);
	p.shadow(6.5, 20.6, 5, 1);
	for (const [x, top] of [[2, 9], [6, 5], [10, 11]] as const) {
		p.vline(x, top, 21 - top, rgba('#c2a24a'), rgba('#6a561d'));
		p.set(x, top + 5, rgba('#8f7a2e'));
		p.set(x, top + 10, rgba('#8f7a2e'));
		p.rect(x - 1, top - 2, 3, 2, M.metal.c[3], M.metal.ink);
		const big = frame === 0;
		p.set(x, top - 3, rgba('#ffb627'), M.gold.ink);
		p.set(x, top - 4, rgba(big ? '#ffd34d' : '#ffb627'), M.gold.ink);
		if (big) p.set(x, top - 5, rgba('#ffd34d'), M.gold.ink);
		const glow = pack(255, 226, 140, 40);
		p.blend(x - 1, top - 4, glow);
		p.blend(x + 1, top - 4, glow);
	}
	return p.outline();
}

function wau(frame: number): Pix {
	const p = new Pix(21, 37);
	p.shadow(10.5, 35.4, 2.5, 0.8);
	p.rect(10, 31, 2, 5, M.bark.c[2], M.bark.ink);
	const sway = frame ? 1 : 0;
	// the string up from the peg
	for (let y = 17; y < 31; y++) p.set(10 + Math.round(Math.sin((y - 17) / 4) * 1.4 * (frame ? -1 : 1)), y, rgba('#fffbe6'));
	const ox = sway;
	p.poly([[10 + ox, 1], [8 + ox, 6], [8 + ox, 15], [10 + ox, 17], [12 + ox, 15], [12 + ox, 6]], M.sun.c[3], M.sun.ink);
	p.poly([[10 + ox, 7], [1, 8 + ox], [0, 12], [10 + ox, 11], [20, 12], [19, 8 + ox]], M.red.c[2], M.red.ink);
	p.poly([[4 + ox, 15], [6 + ox, 18], [14 + ox, 18], [16 + ox, 15], [10 + ox, 17]], M.sky.c[2], M.sky.ink);
	p.hline(3, 9 + ox, 14, rgba('#fff4e6'));
	p.set(10 + ox, 3, M.sky.c[2]);
	return p.outline();
}

function cat(frame: number): Pix {
	const p = new Pix(12, 11);
	const fur = ramp(['#9a4f1a', '#d9762a', '#f29c4b', '#ffbe7c', '#ffe0b4']);
	p.shadow(6, 9.6, 5, 1);
	const tail = frame ? [[9, 8], [10, 7], [11, 6], [11, 5]] : [[9, 8], [10, 8], [11, 7], [11, 6]];
	for (const [x, y] of tail) p.set(x, y, fur.c[1], fur.ink);
	p.blob(5, 7, 3.8, 3, fur, { rim: true });
	p.rect(3, 8, 4, 2, rgba('#fde7c8'), M.cream.ink);
	p.blob(5, 4, 3.6, 3.2, fur, { rim: true, bias: 0.4 });
	p.poly([[1.8, 3], [2.4, 0], [4.6, 2]], fur.c[2], fur.ink);
	p.poly([[8.2, 3], [7.6, 0], [5.4, 2]], fur.c[2], fur.ink);
	p.set(3, 4, EYE_C);
	p.set(7, 4, EYE_C);
	p.set(5, 5, rgba('#e8798a'));
	return p.outline();
}
const EYE_C = rgba('#241b2c');

function hen(frame: number): Pix {
	const p = new Pix(12, 11);
	const fur = ramp(['#6e3014', '#a8562b', '#d9893f', '#f0b060', '#ffd8a0']);
	p.shadow(6, 9.8, 5, 1);
	p.vline(5, 8, 2, rgba('#e8a800'));
	p.vline(8, 8, 2, rgba('#e8a800'));
	p.ellipse(5.5, 6, 4.8, 3, fur.c[2], fur.ink);
	p.rect(2, 5, 5, 2, fur.c[1], fur.ink);
	p.poly([[1, 3], [0, 6], [3, 5]], rgba('#3d2b22'), rgba('#1a1210'));
	const hy = frame ? 3 : 0;
	p.blob(9, 3 + hy, 2.2, 2.2, fur, { rim: true, bias: 0.4 });
	p.set(8, 0 + hy, RED, M.red.ink);
	p.set(9, 0 + hy, RED, M.red.ink);
	p.set(11, 3 + hy, rgba('#f2b33d'));
	p.set(9, 3 + hy, EYE_C);
	return p.outline();
}

function pot(): Pix {
	const p = new Pix(14, 22);
	p.shadow(7, 20.6, 5.5, 1);
	for (const [dx, dy, w] of [[-4, 0, 3], [3, -2, 3.4], [0, -5, 3], [-2, -2, 2.4], [5, 2, 2.6]] as const) {
		p.blob(7 + dx, 8 + dy, w, w * 1.6, M.leaf, { rim: true, bias: dx > 0 ? -0.3 : 0.2 });
	}
	p.poly([[2, 13], [12, 13], [11, 20], [3, 20]], M.roof.c[2], M.roof.ink);
	p.rect(1, 12, 12, 3, M.roof.c[1], M.roof.ink);
	p.hline(1, 12, 12, M.roof.c[3], M.roof.ink);
	return p.outline();
}

function banner(variant: number): Pix {
	const p = new Pix(38, 30);
	p.shadow(19, 28.6, 17, 1);
	for (const x of [2, 33]) {
		p.cyl(x, 4, 3, 24, M.bark);
		p.rect(x, 2, 3, 2, M.gold.c[3], M.gold.ink);
	}
	if (variant === 0) {
		p.rect(5, 5, 28, 11, rgba('#ffffff'), M.cloth.ink);
		for (let i = 0; i < 14; i++) {
			p.rect(5 + i * 2, 5 + (i % 2 ? 0 : 2), 2, 2, rgba('#1f2d27'));
			p.rect(5 + i * 2, 14 - (i % 2 ? 0 : 2), 2, 2, rgba('#1f2d27'));
		}
	} else {
		p.rect(5, 6, 28, 10, rgba('#1f9d55'), rgba('#0f5a30'));
		p.hline(5, 6, 28, rgba('#4fd08a'), rgba('#0f5a30'));
	}
	return p.outline();
}

function fountain(frame: number): Pix {
	const p = new Pix(38, 27);
	p.shadow(19, 24.6, 17, 1.8);
	p.ellipse(19, 18, 17.4, 6.4, M.stone.c[2], M.stone.ink);
	p.rect(2, 15, 34, 5, M.stone.c[2], M.stone.ink);
	p.vline(2, 15, 5, M.stone.c[3], M.stone.ink);
	p.vline(35, 15, 5, M.stone.c[1], M.stone.ink);
	p.hline(4, 20, 30, M.stone.c[1], M.stone.ink);
	p.ellipse(19, 15, 17.4, 6.4, M.stone.c[4], M.stone.ink);
	p.ellipse(19, 15.4, 15, 4.9, M.water.c[2], M.water.ink);
	p.hline(8, 15, 6, M.water.c[3]);
	p.hline(24, 17, 6, M.water.c[3]);
	p.cyl(17, 6, 4, 9, M.stone);
	p.ellipse(19, 6, 5, 1.8, M.stone.c[4], M.stone.ink);
	const spray = rgba('#c1efe8');
	const jet = [[0, 0], [0, 1], [0, 2]];
	void jet;
	for (let i = 0; i < 7; i++) {
		const f = (i + frame * 2) % 7;
		p.set(19, 4 - f, spray, M.water.ink);
	}
	for (const dir of [-1, 1]) {
		for (let i = 0; i < 6; i++) {
			const t = (i + frame * 2) / 6;
			p.set(19 + dir * (1 + t * 7), 4 - Math.sin(t * Math.PI) * 5 + t * t * 6, spray, M.water.ink);
		}
	}
	return p.outline();
}

function pondok(): Pix {
	const p = new Pix(38, 38);
	p.shadow(19, 36.6, 16, 1.4);
	for (const x of [8, 28]) p.cyl(x, 26, 2, 10, M.bark);
	p.line(17, 28, 15, 36, M.bark.c[2]);
	p.line(21, 28, 23, 36, M.bark.c[2]);
	p.hline(15, 32, 8, M.bark.c[2]);
	p.rect(5, 25, 28, 3, M.plank.c[2], M.plank.ink);
	p.hline(5, 25, 28, M.plank.c[3], M.plank.ink);
	p.rect(8, 15, 22, 10, M.plank.c[3], M.plank.ink);
	p.hline(8, 19, 22, M.plank.c[2]);
	p.hline(8, 22, 22, M.plank.c[2]);
	p.rect(16, 17, 6, 8, M.bark.c[1], M.bark.ink);
	p.poly([[1, 16], [19, 2], [37, 16]], (x, y) => (x > 19 ? M.thatch.c[1] : M.thatch.c[2]), M.thatch.ink);
	for (let i = 0; i < 6; i++) p.hline(3 + i * 2, 15 - i * 2 - (i % 2), 4 + (i % 2), M.thatch.c[3]);
	p.set(19, 2, M.thatch.c[4]);
	p.speckle(M.thatch.c[1], 0.18, 71, (x, y) => y < 16 && y > 2);
	return p.outline();
}

function tempayan(): Pix {
	const p = new Pix(14, 15);
	p.shadow(7, 13.6, 5.5, 1);
	p.blob(7, 9, 5.8, 4.8, M.roof, { rim: true, dither: 0.1 });
	p.rect(4, 3, 6, 3, M.roof.c[2], M.roof.ink);
	p.vline(4, 3, 3, M.roof.c[3], M.roof.ink);
	p.vline(9, 3, 3, M.roof.c[1], M.roof.ink);
	p.ellipse(7, 2.6, 3.6, 1.4, M.roof.c[1], M.roof.ink);
	p.ellipse(7, 2.6, 2.6, 0.9, rgba('#4fc3f7'));
	p.hline(3, 7, 8, M.roof.c[1]);
	return p.outline();
}

function scarecrow(): Pix {
	const p = new Pix(18, 30);
	p.shadow(9, 28.6, 3.5, 1);
	p.cyl(8, 8, 2, 20, M.bark);
	p.rect(2, 12, 14, 2, M.bark.c[2], M.bark.ink);
	p.poly([[3, 11], [15, 11], [15, 14], [12, 14], [11, 21], [7, 21], [6, 14], [3, 14]], M.sky.c[2], M.sky.ink);
	p.rect(7, 15, 3, 2, M.sun.c[3]);
	for (const x of [1, 16]) p.vline(x, 12, 3, rgba('#e8c06a'));
	p.ellipse(9, 8, 3, 3, rgba('#f0d9a6'), M.cream.ink);
	p.set(8, 8, EYE_C);
	p.set(10, 8, EYE_C);
	p.hline(8, 10, 3, rgba('#8e5a2e'));
	p.poly([[2.5, 7], [9, 2], [15.5, 7]], rgba('#e8c06a'), rgba('#7a5a2a'));
	p.hline(2, 7, 14, rgba('#c9a24a'), rgba('#7a5a2a'));
	return p.outline();
}

function arch(): Pix {
	const p = new Pix(51, 48);
	p.shadow(25.5, 46.4, 23, 1.4);
	for (const x of [4, 42]) {
		p.cyl(x, 8, 5, 38, M.bark);
		p.rect(x - 1, 44, 7, 2, M.bark.c[1], M.bark.ink);
	}
	p.rect(1, 6, 49, 6, M.roof.c[2], M.roof.ink);
	p.hline(1, 6, 49, M.roof.c[4], M.roof.ink);
	p.hline(1, 11, 49, M.roof.c[1], M.roof.ink);
	for (let i = 0; i < 8; i++) {
		const x = 10 + i * 4.2;
		const y = 13 + Math.sin(((i + 0.5) / 8) * Math.PI) * 2.6;
		const tone = [M.red, M.sun, M.sky, M.leaf][i % 4];
		p.poly([[x, y], [x + 3.4, y], [x + 1.7, y + 4]], tone.c[2], tone.ink);
	}
	p.rect(10, 0, 31, 8, rgba('#fff4e6'), M.bark.ink);
	p.hline(10, 7, 31, M.cream.c[0], M.bark.ink);
	for (const x of [7, 44]) {
		p.blob(x, 44, 4, 3.4, M.leaf, { rim: true });
		p.set(x - 2, 42, rgba('#ff7aa2'));
	}
	return p.outline();
}

const SIGNS: Record<string, PropArt['sign']> = {
	arch: { x: 11, y: 1, w: 29, h: 6 },
	banner: { x: 5, y: 6, w: 28, h: 10 },
	gate: { x: 13, y: 9, w: 16, h: 3 }
};

type Maker = { w: number; h: number; frames?: number; ms?: number; draw: (variant: number, state: string, frame: number) => Pix };

const MAKERS: Record<string, Maker> = {
	tree: { w: 29, h: 37, draw: (v) => (v === 3 ? autumnTree() : tree(v)) },
	pine: { w: 22, h: 38, draw: (v) => pine(v) },
	palm: { w: 29, h: 40, draw: () => palm() },
	bush: { w: 19, h: 14, draw: (v) => bush(v) },
	rock: { w: 18, h: 13, draw: () => rock() },
	flowers: { w: 14, h: 9, draw: (v) => flowers(v) },
	mushroom: { w: 10, h: 10, draw: () => mushroom() },
	lamp: { w: 10, h: 30, frames: 2, ms: 1100, draw: (_v, s, f) => lamp(s !== 'off', f) },
	bench: { w: 22, h: 14, draw: () => bench() },
	sign: { w: 18, h: 21, draw: () => sign() },
	fence: { w: 17, h: 13, draw: () => fence() },
	stump: { w: 14, h: 10, draw: () => stump() },
	reeds: { w: 13, h: 14, draw: () => reeds() },
	lily: { w: 13, h: 6, draw: () => lily() },
	chest: { w: 15, h: 14, draw: (_v, s) => chest(s) },
	gate: { w: 42, h: 46, draw: (_v, s) => gate(s === 'open') },
	hibiscus: { w: 16, h: 15, draw: () => hibiscus() },
	pelita: { w: 13, h: 22, frames: 2, ms: 900, draw: (_v, _s, f) => pelita(f) },
	wau: { w: 21, h: 37, frames: 2, ms: 1500, draw: (_v, _s, f) => wau(f) },
	cat: { w: 12, h: 11, frames: 2, ms: 1600, draw: (_v, _s, f) => cat(f) },
	hen: { w: 12, h: 11, frames: 2, ms: 1300, draw: (_v, _s, f) => hen(f) },
	pot: { w: 14, h: 22, draw: () => pot() },
	banner: { w: 38, h: 30, draw: (v) => banner(v) },
	fountain: { w: 38, h: 27, frames: 3, ms: 900, draw: (_v, _s, f) => fountain(f) },
	pondok: { w: 38, h: 38, draw: () => pondok() },
	tempayan: { w: 14, h: 15, draw: () => tempayan() },
	scarecrow: { w: 18, h: 30, draw: () => scarecrow() },
	arch: { w: 51, h: 48, draw: () => arch() }
};

export const PROP_KINDS = Object.keys(MAKERS);

/** The picture of a prop; null for a kind drawn elsewhere (buildings, crops). */
export function propArt(kind: string, variant = 0, state = ''): PropArt | null {
	const m = MAKERS[kind];
	if (!m) return null;
	return memo(`prop:${kind}:${variant}:${state}`, () => {
		const frames = m.frames ?? 1;
		const sheet = new Pix(m.w * frames, m.h);
		for (let f = 0; f < frames; f++) sheet.stamp(m.draw(variant, state, f), f * m.w, 0);
		return { sheet: sheetOf(sheet, m.w, m.h), frames, ms: m.ms ?? 1000, sign: SIGNS[kind] };
	});
}
