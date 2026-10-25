/*
 * Backdrops for the big-screen charts: a daytime sky in dithered bands with a few clouds, and the
 * ground the towers of coins or harvest stand on. Each is a small picture the chart repeats sideways.
 */
import { memo } from './cache';
import { landMap, paintGround } from './ground';
import { M } from './palette';
import { Pix, noise, rgba } from './pix';

const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
const bayer = (x: number, y: number) => (BAYER[(y & 3) * 4 + (x & 3)] + 0.5) / 16;

export const SKY = { w: 96, h: 96 };

/** Three bands of blue, each dithered into the next, and two clouds. */
export function daySky(): Pix {
	return memo('backdrop:sky', () => {
		const p = new Pix(SKY.w, SKY.h);
		const bands = ['#79c4e8', '#9fd6f0', '#c4e8f8', '#e0f3fb'].map((h) => rgba(h));
		const band = SKY.h / bands.length;
		for (let y = 0; y < SKY.h; y++) {
			const k = Math.min(bands.length - 1, Math.floor(y / band));
			const into = y - k * band;
			for (let x = 0; x < SKY.w; x++) {
				let c = bands[k];
				if (k < bands.length - 1 && into >= band - 3) c = (into - (band - 3) + 1) / 7 + 0.14 > bayer(x, y) ? bands[k + 1] : bands[k];
				else if (k > 0 && into < 3) c = 1 - (into + 1) / 7 - 0.14 > bayer(x, y) ? bands[k - 1] : bands[k];
				p.set(x, y, c);
			}
		}
		const cloud = (cx: number, cy: number, w: number) => {
			p.blob(cx, cy, w, 3.2, M.cloth, { rim: false, bias: 0.4 });
			p.blob(cx - w * 0.45, cy + 1, w * 0.5, 2.4, M.cloth, { rim: false, bias: 0.4 });
			p.blob(cx + w * 0.4, cy + 1.2, w * 0.55, 2.2, M.cloth, { rim: false, bias: 0.4 });
		};
		cloud(22, 14, 8);
		cloud(70, 30, 10);
		return p;
	});
}

export const GROUND = { w: 64, h: 48 };

/** Ground along the foot of a chart: sand for coins, tilled soil for the harvest, grass on its lip. */
export function towerGround(kind: 'coins' | 'harvest'): Pix {
	return memo(`backdrop:ground:${kind}`, () => {
		const land = kind === 'coins' ? 'sand' : 'soil';
		const map = landMap(Array.from({ length: GROUND.h / 16 }, () => 'x'.repeat(GROUND.w / 16)), { x: land });
		const p = paintGround(map, { seed: kind === 'coins' ? 41 : 42, meadow: 0, corner: 0 });
		// a lip of grass, with blades hanging into the earth and tufts above it
		for (let x = 0; x < GROUND.w; x++) {
			const depth = 3 + Math.floor(noise(x >> 1, 0, 71) * 3);
			for (let y = 0; y < depth; y++) p.set(x, y, y === depth - 1 ? M.grass.c[1] : y === 0 ? M.grass.c[3] : M.grass.c[2], M.grass.ink);
			if (noise(x, 1, 72) < 0.18) p.set(x, 0, M.grass.c[4]);
		}
		return p;
	});
}
