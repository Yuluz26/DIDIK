/*
 * A small round window into each game's world, in pixels: the picture that stands for a game in the
 * lobby, the game picker and a parent's list. Forty pixels across, one scene each.
 */
import { memo, sheetOf } from './cache';
import { M } from './palette';
import { Pix, type Colour, mix, rgba } from './pix';

const N = 40;

function bands(p: Pix, y0: number, y1: number, top: Colour, bottom: Colour) {
	const rows = y1 - y0;
	for (let y = y0; y < y1; y++) p.hline(0, y, N, mix(top, bottom, Math.min(1, (y - y0) / Math.max(1, rows - 1))));
}

function sea(p: Pix, y0: number, tone = M.water) {
	p.rect(0, y0, N, N - y0, tone.c[2]);
	for (const [x, y] of [[4, 4], [24, 9], [12, 15], [30, 20]]) {
		p.hline(x, y0 + y, 5, tone.c[3]);
		p.hline(x + 1, y0 + y + 1, 3, tone.c[1]);
	}
}

function sky(p: Pix, y1: number, a = '#bfe6f6', b = '#e8f8ff') {
	bands(p, 0, y1, rgba(a), rgba(b));
}

const scenes: Record<string, (p: Pix) => void> = {
	sungai(p) {
		sky(p, 17);
		p.poly([[0, 17], [0, 12], [10, 10], [22, 13], [40, 11], [40, 17]], M.leaf.c[2]);
		p.blob(9, 11, 5, 4, M.leaf, { bias: -0.2 });
		p.blob(31, 10, 5, 4, M.leaf, { bias: -0.4 });
		sea(p, 17);
		p.poly([[10, 25], [30, 25], [27, 31], [13, 31]], M.roof.c[2], M.roof.ink);
		p.hline(10, 25, 20, M.roof.c[4], M.roof.ink);
		p.hline(12, 27, 16, M.gold.c[3]);
		p.ellipse(20, 22, 3.4, 3.4, rgba('#e7b98a'), M.roof.ink);
		p.vline(27, 14, 11, M.bark.c[2]);
		p.poly([[28, 14], [34, 16.5], [28, 19]], M.gold.c[3], M.gold.ink);
	},
	kolam(p) {
		p.rect(0, 0, N, N, M.deep.c[2]);
		for (const [x, y] of [[3, 6], [26, 4], [14, 33], [30, 31]]) p.hline(x, y, 6, M.deep.c[4]);
		p.ellipse(12, 26, 10, 5, M.sand.c[2], M.sand.ink);
		p.ellipse(12, 24.5, 8.5, 4, M.grass.c[3], M.grass.ink);
		p.ellipse(29, 27, 9, 4.6, M.sand.c[2], M.sand.ink);
		p.ellipse(29, 25.5, 7.5, 3.6, rgba('#f29c7a'), M.roof.ink);
		for (const [x, y] of [[8, 24], [9, 25], [10, 24], [11, 23], [12, 22]]) p.set(x + 1, y, rgba('#ffffff'));
		for (const [x, y] of [[26, 23], [27, 24], [28, 25], [29, 26], [30, 27], [30, 23], [29, 24], [27, 26], [26, 27]]) p.set(x, y - 1, rgba('#ffffff'));
		p.blob(20, 12, 4.4, 4.2, M.stone, { rim: true });
		p.rect(17, 14, 6, 6, M.stone.c[2], M.stone.ink);
	},
	pulau(p) {
		p.rect(0, 0, N, N, M.water.c[2]);
		for (const [x, y] of [[3, 5], [28, 8], [4, 33], [27, 34]]) p.hline(x, y, 6, M.water.c[3]);
		p.ellipse(20, 26, 18, 9, M.water.c[3]);
		p.ellipse(20, 26, 16, 7.6, M.sand.c[2], M.sand.ink);
		p.ellipse(20, 24, 14, 5, M.sand.c[3]);
		p.vline(26, 11, 14, M.bark.c[2], M.bark.ink);
		for (const [dx, dy] of [[-7, 2], [-4, -2], [3, -2], [7, 3]]) p.blob(26 + dx / 2, 11 + dy / 2, 3.2, 1.8, M.leaf, { rim: true });
		p.blob(26, 10, 2.6, 2.2, M.leaf, { rim: true, bias: 0.4 });
		const red = rgba('#c0503a');
		for (const [x, y] of [[9, 23], [10, 24], [11, 25], [12, 26], [12, 23], [11, 24], [10, 25], [9, 26]]) p.set(x, y, red);
		p.rect(17, 27, 8, 5, M.roof.c[2], M.roof.ink);
		p.hline(17, 27, 8, M.roof.c[4], M.roof.ink);
		p.set(21, 29, M.gold.c[3]);
	},
	hutan(p) {
		p.rect(0, 0, N, N, M.grass.c[2]);
		p.speckle(M.grass.c[1], 0.1, 5);
		p.poly([[14, 40], [24, 40], [26, 24], [30, 0], [22, 0], [18, 24]], M.dirt.c[3], M.dirt.ink);
		p.blob(9, 13, 7, 8, M.leaf, { rim: true });
		p.cyl(8, 19, 3, 6, M.bark);
		p.blob(31, 27, 6, 7, M.pine, { rim: true });
		p.cyl(30, 32, 3, 5, M.bark);
		p.rect(18, 29, 6, 5, M.roof.c[2], M.roof.ink);
		p.hline(18, 29, 6, M.roof.c[4], M.roof.ink);
		p.set(20, 31, M.gold.c[3]);
	},
	peta(p) {
		p.rect(0, 0, N, N, M.deep.c[2]);
		const tile = (cx: number, cy: number, tone: typeof M.leaf) => {
			p.poly([[cx, cy - 8], [cx + 7, cy - 4], [cx + 7, cy + 4], [cx, cy + 8], [cx - 7, cy + 4], [cx - 7, cy - 4]], tone.c[2], tone.ink);
			p.line(cx - 6, cy - 3, cx, cy - 7, tone.c[4]);
		};
		const orange = { ...M.autumn };
		const teal = { c: [rgba('#0b665e'), rgba('#0f857a'), rgba('#14958a'), rgba('#3fb8ac'), rgba('#8fe0d6')], ink: rgba('#063a36') };
		tile(13, 14, orange);
		tile(27, 14, M.grass);
		tile(20, 26, teal);
		tile(6, 26, M.grass);
		tile(34, 26, M.grass);
		p.vline(14, 9, 7, M.bark.c[2]);
		p.poly([[15, 9], [19, 10.5], [15, 12]], rgba('#ffffff'));
		p.vline(21, 21, 7, M.bark.c[2]);
		p.poly([[22, 21], [26, 22.5], [22, 24]], rgba('#ffffff'));
	},
	kampung(p) {
		p.rect(0, 0, N, N, M.grass.c[2]);
		p.speckle(M.grass.c[1], 0.1, 6);
		p.rect(0, 27, N, 6, M.dirt.c[3]);
		p.hline(0, 27, N, M.dirt.c[1]);
		for (const x of [10, 22]) p.cyl(x, 20, 2, 7, M.bark);
		p.rect(7, 12, 22, 9, M.plank.c[3], M.plank.ink);
		p.rect(14, 14, 4, 7, M.bark.c[1]);
		p.poly([[4, 13], [18, 3], [32, 13]], M.roof.c[2], M.roof.ink);
		p.poly([[18, 3], [32, 13], [18, 13]], M.roof.c[1], M.roof.ink);
		p.vline(35, 14, 13, M.bark.c[2], M.bark.ink);
		p.blob(35, 12, 4, 3, M.leaf, { rim: true });
	},
	galeri(p) {
		p.rect(0, 0, N, 24, M.cream.c[3]);
		p.rect(0, 24, N, 16, M.plank.c[3]);
		for (const y of [28, 32, 36]) p.hline(0, y, N, M.plank.c[2]);
		p.rect(9, 5, 22, 19, M.bark.c[2], M.bark.ink);
		for (let j = 0; j < 4; j++) {
			for (let i = 0; i < 4; i++) {
				const open = i === 1 && j === 2;
				p.rect(11 + i * 4.5, 7 + j * 4, 4, 3, open ? rgba('#1d2a50') : (i + j) % 2 ? rgba('#239a91') : rgba('#2bb0a6'));
			}
		}
		p.line(15, 24, 12, 36, M.bark.c[2], M.bark.ink);
		p.line(25, 24, 28, 36, M.bark.c[2], M.bark.ink);
		p.ellipse(20, 34, 12, 3, rgba('#2bb0a6'), rgba('#0c6a62'));
	},
	kebun(p) {
		p.rect(0, 0, N, N, M.grass.c[2]);
		p.speckle(M.grass.c[1], 0.1, 7);
		p.rect(5, 16, 30, 17, M.plank.c[2], M.plank.ink);
		p.rect(7, 18, 26, 8, M.bark.c[1], M.bark.ink);
		p.hline(5, 16, 30, M.plank.c[4], M.plank.ink);
		for (const [x, h] of [[12, 8], [20, 10], [28, 7]] as const) {
			p.vline(x, 18 - h, h, M.leaf.c[2], M.leaf.ink);
			p.blob(x - 2, 18 - h + 2, 2.4, 1.4, M.leaf, { rim: true });
			p.blob(x + 2, 18 - h + 1, 2.4, 1.4, M.leaf, { rim: true, bias: 0.4 });
		}
		p.ellipse(20, 5, 3.2, 3.2, M.red.c[2], M.red.ink);
		p.set(20, 5, M.gold.c[3]);
	},
};

/** The round badge for a game's world. */
export function badge(world: string) {
	return memo(`badge:${world}`, () => {
		const scene = new Pix(N, N);
		(scenes[world] ?? scenes.sungai)(scene);
		// keep only the disc, and ring it
		const out = new Pix(N, N);
		const dark = rgba('#2a1f2d');
		for (let y = 0; y < N; y++) {
			for (let x = 0; x < N; x++) {
				const d = Math.hypot(x + 0.5 - N / 2, y + 0.5 - N / 2);
				if (d <= N / 2 - 1.5) out.set(x, y, scene.c[y * N + x] || rgba('#ffffff'));
				else if (d <= N / 2 - 0.2) out.set(x, y, dark);
			}
		}
		return sheetOf(out);
	});
}
