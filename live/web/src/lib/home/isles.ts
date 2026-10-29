/*
 * The ground of the front page's islands, painted in pixels (lib/pixel/island.ts): the town island
 * where children gather, and a small island for each of the games, with the details that flat ground
 * carries (a jetty, a path, buoys, a spot to dig, a board of hexagons, a pond, a railway, a plaza). Everything that stands up
 * is a prop the world draws on top.
 */
import { memo } from '$lib/pixel/cache';
import { TILE } from '$lib/pixel/cache';
import { type Pix, rgba } from '$lib/pixel/pix';
import { type Isle, alongPath, curve, inEllipse, inPoly, paintIsland } from '$lib/pixel/island';
import { buoy, digMark, hole, miniHex } from './sprites';

/** Lays a picture on the ground with its middle at a place given in tiles. */
function put(ground: Pix, art: { pix: Pix }, x: number, y: number) {
	ground.stamp(art.pix, Math.round(x * TILE - art.pix.w / 2), Math.round(y * TILE - art.pix.h / 2));
}

export const MAIN = { w: 12, h: 7.8 };
export const ISLE = { w: 6, h: 4.4 };

export function townGround(): Pix {
	return memo('isle:town', () => {
		const isle: Isle = { cx: 6, cy: 4.15, rx: 5.65, ry: 3.05, reach: [1, 0.95, 1.04, 0.97, 1.02, 0.94, 1.05, 0.98, 1, 0.96], turn: 0.3, tops: [{ land: 'grass', k: 0.93, dy: -0.02 }] };
		return paintIsland({
			...MAIN,
			seed: 11,
			isles: [isle],
			lagoon: 1.16,
			meadow: 0.3,
			over: [
				{ land: 'dirt', test: inPoly([[5.45, 2.3], [6.75, 2.3], [6.95, 3.6], [5.25, 3.6]]) },
				{ land: 'dirt', test: alongPath(curve([7.7, 5.5], [[8.3, 6.1], [8.6, 6.5], [8.8, 7.0]]), 0.62) },
				{ land: 'stone', test: inEllipse(6.1, 4.75, 3.1, 1.55) },
				{ land: 'plank', test: inPoly([[8.55, 6.9], [9.7, 6.75], [10.05, 7.55], [8.85, 7.75]]) }
			]
		});
	});
}

interface GameIsle {
	isles: Isle[];
	seed: number;
	over?: Parameters<typeof paintIsland>[0]['over'];
	/** Flat details laid on the finished ground. */
	detail?: (ground: Pix) => void;
}

const GRASS = (k = 0.88, dy = -0.04) => [{ land: 'grass' as const, k, dy }];

const HEX_ROWS: [number, number, (string | null)[]][] = [
	[3.0, 2.0, ['#f28c28', '#f28c28', null, '#14958a', '#14958a']],
	[3.0, 2.44, ['#f28c28', '#f28c28', null, null, '#14958a', '#14958a']],
	[3.0, 2.88, ['#f28c28', null, '#f28c28', '#14958a', '#14958a']]
];

const GAMES: Record<string, GameIsle> = {
	lumba: {
		seed: 21,
		isles: [{ cx: 2.4, cy: 2.5, rx: 2.0, ry: 1.15, reach: [1, 0.95, 1.05, 0.9, 1, 1.08, 0.92, 1], tops: GRASS() }],
		over: [{ land: 'plank', test: inPoly([[3.85, 2.55], [5.75, 2.72], [5.7, 3.0], [3.8, 2.85]]) }],
		detail(g) {
			for (const [x, y] of [[4.0, 3.75], [4.45, 3.62], [4.9, 3.5]]) put(g, buoy(), x, y);
		}
	},
	lompat: {
		seed: 22,
		isles: [
			{ cx: 1.3, cy: 3.0, rx: 0.85, ry: 0.48, reach: [1, 0.95, 1.05, 1, 0.95, 1], tops: GRASS() },
			{ cx: 3.0, cy: 2.2, rx: 0.9, ry: 0.5, reach: [1, 1.05, 0.95, 1, 1.05, 0.95], tops: GRASS() },
			// the wrong one is going under
			{ cx: 4.75, cy: 3.25, rx: 0.8, ry: 0.45, reach: [1, 0.9, 1.05, 1, 0.95, 1.05], tops: [{ land: 'water', k: 0.8, dy: 0.02 }] }
		]
	},
	harta: {
		seed: 23,
		isles: [{ cx: 3, cy: 2.65, rx: 2.45, ry: 1.3, reach: [1, 0.92, 1.06, 1, 0.94, 1.08, 1, 0.95], tops: GRASS(0.55, -0.28) }],
		detail(g) {
			put(g, digMark(), 4.03, 3.12);
			put(g, hole(), 1.85, 3.35);
			put(g, hole(), 4.75, 2.55);
		}
	},
	hutan: {
		seed: 24,
		isles: [{ cx: 3, cy: 2.6, rx: 2.55, ry: 1.32, reach: [1.04, 0.95, 1, 1.06, 0.93, 1, 1.05, 0.96], tops: [{ land: 'moss', k: 0.88, dy: -0.04 }] }],
		over: [{ land: 'dirt', test: alongPath(curve([3.1, 3.95], [[2.9, 3.4], [3.5, 3.0], [3.25, 2.55]], [[3.1, 2.2], [3.4, 1.9], [3.3, 1.6]]), 0.34) }]
	},
	pasukan: {
		seed: 25,
		isles: [{ cx: 3, cy: 2.62, rx: 2.6, ry: 1.36, reach: [1, 1.04, 0.96, 1, 1.03, 0.97, 1, 1.02], tops: GRASS() }],
		detail(g) {
			for (const [cx, cy, row] of HEX_ROWS) {
				row.forEach((colour, i) => {
					const hex = miniHex(colour);
					put(g, hex, cx + (i - (row.length - 1) / 2) * (13 / TILE), cy);
				});
			}
		}
	},
	kampung: {
		seed: 26,
		isles: [{ cx: 3, cy: 2.6, rx: 2.55, ry: 1.32, reach: [1, 0.94, 1.05, 1, 0.96, 1.06, 0.97, 1], tops: GRASS() }],
		over: [{ land: 'dirt', test: alongPath(curve([2.45, 2.85], [[2.6, 3.3], [3.3, 3.5], [3.6, 3.95]]), 0.28) }]
	},
	teka: {
		seed: 27,
		isles: [{ cx: 3, cy: 2.62, rx: 2.45, ry: 1.28, reach: [1.02, 0.96, 1, 1.05, 0.95, 1, 1.04, 0.97], tops: GRASS() }]
	},
	kebun: {
		seed: 28,
		isles: [{ cx: 3, cy: 2.62, rx: 2.55, ry: 1.32, reach: [1, 1.05, 0.95, 1, 1.04, 0.96, 1, 1.03], tops: GRASS() }]
	},
	pancing: {
		seed: 29,
		isles: [{ cx: 3, cy: 2.6, rx: 2.55, ry: 1.3, reach: [1, 0.96, 1.05, 0.98, 1, 1.06, 0.94, 1], tops: GRASS() }],
		over: [
			{ land: 'water', test: inEllipse(3.45, 2.95, 1.35, 0.62) },
			{ land: 'plank', test: inPoly([[1.85, 2.72], [2.75, 2.75], [2.75, 2.98], [1.85, 2.95]]) }
		]
	},
	wau: {
		seed: 30,
		isles: [{ cx: 3, cy: 2.75, rx: 2.5, ry: 1.2, reach: [1, 1.04, 0.96, 1, 1.05, 0.95, 1.02, 0.98], tops: GRASS() }],
		over: [{ land: 'dirt', test: alongPath(curve([1.2, 3.6], [[2.0, 3.2], [3.2, 3.5], [4.6, 3.1]]), 0.26) }]
	},
	kubu: {
		seed: 31,
		isles: [{ cx: 3, cy: 2.65, rx: 2.5, ry: 1.28, reach: [1, 0.94, 1.06, 1, 0.95, 1.05, 0.98, 1], tops: GRASS(0.42, -0.42) }]
	},
	keretapi: {
		seed: 32,
		isles: [{ cx: 3, cy: 2.6, rx: 2.6, ry: 1.32, reach: [1.03, 0.96, 1, 1.04, 0.95, 1, 1.05, 0.97], tops: GRASS() }],
		over: [{ land: 'stone', test: inPoly([[0.75, 3.0], [5.25, 3.0], [5.25, 3.42], [0.75, 3.42]]) }],
		detail(g) {
			// sleepers and the two rails along the ballast
			const y = Math.round(3.02 * TILE);
			for (let x = Math.round(0.85 * TILE); x < 5.15 * TILE; x += 5) g.rect(x, y, 2, 6, rgba('#6e4a30'));
			g.rect(Math.round(0.8 * TILE), y + 1, Math.round(4.4 * TILE), 1, rgba('#9a9caa'));
			g.rect(Math.round(0.8 * TILE), y + 4, Math.round(4.4 * TILE), 1, rgba('#9a9caa'));
		}
	},
	pasar: {
		seed: 33,
		isles: [{ cx: 3, cy: 2.6, rx: 2.55, ry: 1.3, reach: [1, 1.05, 0.95, 1, 1.04, 0.96, 1, 1.03], tops: GRASS() }],
		over: [{ land: 'stone', test: inEllipse(3.0, 3.0, 1.9, 0.75) }]
	},
	bintang: {
		seed: 34,
		isles: [{ cx: 3, cy: 2.7, rx: 2.45, ry: 1.25, reach: [1.02, 0.96, 1, 1.05, 0.95, 1, 1.04, 0.97], tops: [{ land: 'moss', k: 0.88, dy: -0.04 }] }]
	}
};

export function gameGround(game: string): Pix {
	return memo(`isle:${game}`, () => {
		const plan = GAMES[game] ?? GAMES.hutan;
		const ground = paintIsland({ ...ISLE, seed: plan.seed, isles: plan.isles, over: plan.over, meadow: 0.3 });
		plan.detail?.(ground);
		return ground;
	});
}
