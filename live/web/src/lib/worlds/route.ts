/**
 * Walking round things in the way: a straight walk that would cross one of them (the fountain's basin,
 * a lamp post, a bench) goes round instead, by a short way that stays clear of all of them. Positions are
 * in tiles, with y growing down the screen; each obstacle is where it stands on the ground, an ellipse.
 *
 * The way is found on a fine grid (a fifth of a tile) and then pulled tight, so a child walks in a few
 * straight legs from corner to corner rather than in little steps.
 */

export type Spot = [number, number];

export interface Basin {
	x: number;
	y: number;
	rx: number;
	ry: number;
}

export interface Box {
	left: number;
	top: number;
	right: number;
	bottom: number;
}

/** A child is a little wider than a point: walks keep this much clear of everything. */
const CLEAR = 1.12;
const CELL = 0.2;

const inside = (x: number, y: number, o: Basin, grow = 1) => ((x - o.x) / (o.rx * grow)) ** 2 + ((y - o.y) / (o.ry * grow)) ** 2 < 1;

/** Whether the straight walk from a to b passes through the basin (sampled along the way). */
export function crosses(a: Spot, b: Spot, basin: Basin, grow = 1): boolean {
	const steps = Math.max(8, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) * 12));
	for (let i = 0; i <= steps; i++) {
		const t = i / steps;
		if (inside(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, basin, grow)) return true;
	}
	return false;
}

const clear = (a: Spot, b: Spot, obstacles: Basin[], grow: number) => obstacles.every((o) => !crosses(a, b, o, grow));

const grids = new WeakMap<Basin[], Uint8Array>();

/** The way from a to b round every obstacle, as the corners to walk through (a first, b last). */
export function route(a: Spot, b: Spot, obstacles: Basin[], box: Box): Spot[] {
	if (clear(a, b, obstacles, 1)) return [a, b];

	const cols = Math.round((box.right - box.left) / CELL) + 1;
	const rows = Math.round((box.bottom - box.top) / CELL) + 1;
	const at = (c: number, r: number): Spot => [box.left + c * CELL, box.top + r * CELL];
	// which cells are clear, worked out once for these obstacles and reused by every walk
	let grid = grids.get(obstacles);
	if (!grid) {
		grid = new Uint8Array(cols * rows);
		for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) grid[r * cols + c] = obstacles.some((o) => inside(...at(c, r), o, CLEAR)) ? 0 : 1;
		grids.set(obstacles, grid);
	}
	const cells0 = grid;
	const open = (c: number, r: number) => c >= 0 && r >= 0 && c < cols && r < rows && cells0[r * cols + c] === 1;
	const cellOf = ([x, y]: Spot): [number, number] => [Math.round((x - box.left) / CELL), Math.round((y - box.top) / CELL)];
	// the nearest open cell to a spot (a child may stand right beside a bench, in its clearance)
	const nearestOpen = (spot: Spot): [number, number] | null => {
		const [c0, r0] = cellOf(spot);
		for (let d = 0; d < 12; d++) {
			let best: [number, number] | null = null;
			let bestD = Infinity;
			for (let c = c0 - d; c <= c0 + d; c++) {
				for (let r = r0 - d; r <= r0 + d; r++) {
					if (Math.max(Math.abs(c - c0), Math.abs(r - r0)) !== d || !open(c, r)) continue;
					const dist = Math.hypot(...(at(c, r).map((v, i) => v - spot[i]) as Spot));
					if (dist < bestD) [best, bestD] = [[c, r], dist];
				}
			}
			if (best) return best;
		}
		return null;
	};

	const start = nearestOpen(a);
	const goal = nearestOpen(b);
	if (!start || !goal) return [a, b];

	// A* over the grid, eight ways
	const key = (c: number, r: number) => r * cols + c;
	const g = new Map<number, number>([[key(...start), 0]]);
	const came = new Map<number, number>();
	const queue = new Heap();
	queue.push([0, ...start]);
	const h = (c: number, r: number) => Math.hypot(c - goal[0], r - goal[1]);
	const goalKey = key(...goal);
	while (queue.size) {
		const [, c, r] = queue.pop();
		const k = key(c, r);
		if (k === goalKey) break;
		for (let dc = -1; dc <= 1; dc++) {
			for (let dr = -1; dr <= 1; dr++) {
				if ((!dc && !dr) || !open(c + dc, r + dr)) continue;
				const step = dc && dr ? Math.SQRT2 : 1;
				const nk = key(c + dc, r + dr);
				const cost = (g.get(k) ?? 0) + step;
				if (cost < (g.get(nk) ?? Infinity)) {
					g.set(nk, cost);
					came.set(nk, k);
					queue.push([cost + h(c + dc, r + dr), c + dc, r + dr]);
				}
			}
		}
	}
	if (!g.has(goalKey)) return [a, b];

	const cells: Spot[] = [];
	for (let k: number | undefined = goalKey; k !== undefined; k = came.get(k)) cells.unshift(at(k % cols, Math.floor(k / cols)));
	const points: Spot[] = [a, ...cells, b];

	// pull tight: from each corner, go straight to the furthest point still in clear sight
	const out: Spot[] = [a];
	let i = 0;
	while (i < points.length - 1) {
		let j = points.length - 1;
		while (j > i + 1 && !clear(points[i], points[j], obstacles, 1.04)) j--;
		out.push(points[j]);
		i = j;
	}
	return out;
}

/** The smallest-first queue A* takes its next cell from: [priority, column, row]. */
class Heap {
	private items: [number, number, number][] = [];
	get size() {
		return this.items.length;
	}
	push(item: [number, number, number]) {
		const a = this.items;
		a.push(item);
		let i = a.length - 1;
		while (i > 0) {
			const up = (i - 1) >> 1;
			if (a[up][0] <= a[i][0]) break;
			[a[up], a[i]] = [a[i], a[up]];
			i = up;
		}
	}
	pop(): [number, number, number] {
		const a = this.items;
		const top = a[0];
		const last = a.pop()!;
		if (a.length) {
			a[0] = last;
			let i = 0;
			for (;;) {
				const l = i * 2 + 1;
				const r = l + 1;
				let m = i;
				if (l < a.length && a[l][0] < a[m][0]) m = l;
				if (r < a.length && a[r][0] < a[m][0]) m = r;
				if (m === i) break;
				[a[m], a[i]] = [a[i], a[m]];
				i = m;
			}
		}
		return top;
	}
}
