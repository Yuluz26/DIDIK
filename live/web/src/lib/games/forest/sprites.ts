/*
 * Hutan Misteri's ground in pixels, painted from the same rows of characters the server walks on:
 * a dark mossy floor under the trees, grass in the clearings, dirt paths, a river with plank bridges.
 */
import { TILE, memo } from '$lib/pixel/cache';
import { landMap, paintGround } from '$lib/pixel/ground';
import { M } from '$lib/pixel/palette';

const LEGEND = { '#': 'moss', ':': 'dirt', S: 'dirt', G: 'dirt', '~': 'water', '=': 'plank' } as const;

export function forestGround(map: readonly string[]) {
	return memo(`forest:${map.join('')}`, () => {
		const rows = landMap(map, LEGEND);
		const p = paintGround(rows, { seed: 23, meadow: 0.5 });
		// Rails along a bridge, on the two sides that are over the water.
		const at = (x: number, y: number) => map[y]?.[x] ?? '#';
		map.forEach((row, y) =>
			[...row].forEach((ch, x) => {
				if (ch !== '=') return;
				const across = at(x, y - 1) === '~' || at(x, y + 1) === '~';
				const x0 = x * TILE;
				const y0 = y * TILE;
				if (across) {
					p.rect(x0, y0, TILE, 2, M.bark.c[2], M.bark.ink);
					p.hline(x0, y0, TILE, M.bark.c[3], M.bark.ink);
					p.rect(x0, y0 + TILE - 2, TILE, 2, M.bark.c[1], M.bark.ink);
					for (const px of [x0 + 1, x0 + TILE - 3]) {
						p.rect(px, y0 - 1, 2, 4, M.bark.c[3], M.bark.ink);
						p.rect(px, y0 + TILE - 3, 2, 4, M.bark.c[2], M.bark.ink);
					}
				} else {
					p.rect(x0, y0, 2, TILE, M.bark.c[3], M.bark.ink);
					p.rect(x0 + TILE - 2, y0, 2, TILE, M.bark.c[1], M.bark.ink);
				}
			})
		);
		return p;
	});
}
