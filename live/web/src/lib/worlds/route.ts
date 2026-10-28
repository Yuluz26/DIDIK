/**
 * Walking round an obstacle: a straight walk that would cross an ellipse (a fountain's basin) goes
 * round it instead, in front of it or behind it, by the shortest way that stays clear. Positions are
 * in tiles, with y growing down the screen.
 */

export type Spot = [number, number];

export interface Basin {
	x: number;
	y: number;
	rx: number;
	ry: number;
}

/** Whether the straight walk from a to b passes through the basin (sampled along the way). */
export function crosses(a: Spot, b: Spot, basin: Basin): boolean {
	const steps = Math.max(8, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) * 12));
	for (let i = 0; i <= steps; i++) {
		const t = i / steps;
		const dx = (a[0] + (b[0] - a[0]) * t - basin.x) / basin.rx;
		const dy = (a[1] + (b[1] - a[1]) * t - basin.y) / basin.ry;
		if (dx * dx + dy * dy < 1) return true;
	}
	return false;
}

const length = (path: Spot[]) => path.slice(1).reduce((sum, p, i) => sum + Math.hypot(p[0] - path[i][0], p[1] - path[i][1]), 0);

/** The way from a to b, with the corners to walk past so it never crosses the basin. */
export function route(a: Spot, b: Spot, basin: Basin): Spot[] {
	if (!crosses(a, b, basin)) return [a, b];
	const { x, y, rx, ry } = basin;
	const front = y + ry + 0.25;
	const back = y - ry - 0.25;
	const side = rx + 0.3;
	const arounds: Spot[][] = [
		[[x, front]],
		[[x, back]],
		[[x - side, y + ry * 0.55], [x + side, y + ry * 0.55]],
		[[x - side, y - ry * 0.55], [x + side, y - ry * 0.55]],
		[[x - side, y], [x, front], [x + side, y]],
		[[x - side, y], [x, back], [x + side, y]]
	];
	const ways = arounds
		.flatMap((via) => [[a, ...via, b], [a, ...[...via].reverse(), b]])
		.filter((path) => path.slice(1).every((p, i) => !crosses(path[i], p, basin)));
	return ways.sort((p, q) => length(p) - length(q))[0] ?? [a, b];
}
