/*
 * Teka Gambar's gallery in pixels: a papered wall with a wooden wainscot, two windows, and a floor
 * of wide boards with a rug under the easel; and the easel itself, with the hole its picture shows
 * through.
 */
import { TILE, memo, sheetOf } from '$lib/pixel/cache';
import { landMap, paintGround } from '$lib/pixel/ground';
import { M } from '$lib/pixel/palette';
import { Pix, mix, noise, ramp, rgba } from '$lib/pixel/pix';

/** The picture's window in the easel sprite, and the sprite's size, in pixels. */
export const EASEL = { w: 74, h: 84, pic: { x: 5, y: 4, size: 64 } };

const paper = ramp(['#d8c3a0', '#ecdcbc', '#f7ecd2', '#fdf4df', '#ffffff']);

function window_(p: Pix, x: number, y: number, w: number, h: number) {
	p.rect(x - 2, y - 2, w + 4, h + 4, M.bark.c[2], M.bark.ink);
	p.hline(x - 2, y - 2, w + 4, M.bark.c[3], M.bark.ink);
	p.rect(x, y, w, h, M.sky.c[3], M.sky.ink);
	for (let j = 0; j < h; j++) p.hline(x, y + j, w, j < h * 0.45 ? M.sky.c[3] : mix(M.sky.c[3], M.sky.c[4], 0.5));
	p.vline(x + Math.floor(w / 2), y, h, M.bark.c[2]);
	p.hline(x, y + Math.floor(h / 2), w, M.bark.c[2]);
	// a cloud and a hill
	p.hline(x + 2, y + 3, 5, rgba('#ffffff'));
	p.hline(x + 3, y + 2, 3, rgba('#ffffff'));
	p.poly([[x, y + h], [x + 5, y + h - 5], [x + 11, y + h - 2], [x + w, y + h]], M.leaf.c[2]);
	p.rect(x - 3, y + h + 2, w + 6, 2, M.plank.c[2], M.plank.ink);
}

export function galleryGround(W: number, H: number) {
	return memo(`gallery:${W}:${H}`, () => {
		const map = landMap(Array.from({ length: H }, () => 'f'.repeat(W)), { f: 'floor' });
		const p = paintGround(map, { seed: 41, meadow: 0 });
		const wall = Math.round(2.3 * TILE);
		// the wall: pale paper with faint stripes, a panelled wainscot, a rail and a skirting board
		for (let y = 0; y < wall; y++) {
			for (let x = 0; x < p.w; x++) {
				const stripe = Math.floor(x / 8) % 2 ? paper.c[3] : paper.c[2];
				const n = noise(x, y, 5);
				p.set(x, y, n < 0.03 ? paper.c[1] : stripe, paper.ink);
			}
		}
		for (let y = 22; y < wall; y++) {
			for (let x = 0; x < p.w; x++) p.set(x, y, (x + 3) % 16 === 0 ? M.plank.c[1] : y === 22 ? M.plank.c[4] : y === wall - 1 ? M.plank.c[1] : M.plank.c[3], M.plank.ink);
		}
		p.hline(0, 20, p.w, M.plank.c[2], M.plank.ink);
		p.hline(0, 21, p.w, M.plank.c[4], M.plank.ink);
		p.hline(0, wall, p.w, M.bark.c[1], M.bark.ink);
		window_(p, 16, 7, 18, 12);
		// a plant on the sill
		p.blob(25, 4, 3, 2.2, M.leaf, { rim: true });
		// a framed picture
		p.rect(93, 6, 17, 14, M.bark.c[2], M.bark.ink);
		p.rect(95, 8, 13, 10, rgba('#ffe7a3'), M.sun.ink);
		p.ellipse(101.5, 13, 2.6, 2.6, rgba('#e8553f'), M.red.ink);
		// the rug under the easel
		const cx = 4 * TILE;
		const cy = Math.round(5.25 * TILE);
		const teal = ramp(['#0c6a62', '#12857b', '#2bb0a6', '#5fd0c4', '#a4ece2']);
		for (let y = cy - 10; y <= cy + 10; y++) {
			for (let x = cx - 44; x <= cx + 44; x++) {
				const d = ((x + 0.5 - cx) / 42) ** 2 + ((y + 0.5 - cy) / 9) ** 2;
				if (d <= 1) p.set(x, y, d > 0.82 ? teal.c[1] : (x + y) % 6 === 0 ? teal.c[3] : teal.c[2], teal.ink);
			}
		}
		for (let a = 0; a < 80; a++) {
			if (a % 3) continue;
			const t = (a / 80) * Math.PI * 2;
			p.set(cx + Math.cos(t) * 36, cy + Math.sin(t) * 6.2, rgba('#ffffff'));
		}
		return p.crop(0, 0, W * TILE, H * TILE);
	});
}

/** The easel: a wooden frame with an open window for the picture, a ledge, and three legs. */
export function easel() {
	return memo('easel', () => {
		const p = new Pix(EASEL.w, EASEL.h);
		p.shadow(37, 82, 26, 1.6);
		// legs behind the frame
		for (const [x0, x1] of [[18, 26], [55, 47]] as const) {
			p.line(x0, 83, x1, 66, M.bark.c[2], M.bark.ink);
			p.line(x0 + 1, 83, x1 + 1, 66, M.bark.c[1], M.bark.ink);
		}
		p.vline(37, 70, 13, M.bark.c[1], M.bark.ink);
		// the frame, with the window left open
		const { x, y, size } = EASEL.pic;
		p.rect(0, 0, EASEL.w, size + 8, M.bark.c[2], M.bark.ink);
		p.hline(0, 0, EASEL.w, M.bark.c[4], M.bark.ink);
		p.vline(0, 0, size + 8, M.bark.c[3], M.bark.ink);
		p.vline(EASEL.w - 1, 0, size + 8, M.bark.c[1], M.bark.ink);
		for (let j = 0; j < size; j++) for (let i = 0; i < size; i++) p.c[(y + j) * EASEL.w + x + i] = 0;
		p.rect(x - 1, y - 1, size + 2, 1, M.bark.c[0]);
		p.rect(x - 1, y - 1, 1, size + 2, M.bark.c[0]);
		// the ledge
		p.rect(2, size + 8, EASEL.w - 4, 4, M.plank.c[3], M.plank.ink);
		p.hline(2, size + 8, EASEL.w - 4, M.plank.c[4], M.plank.ink);
		p.hline(2, size + 11, EASEL.w - 4, M.plank.c[1], M.plank.ink);
		p.outline();
		return sheetOf(p);
	});
}

