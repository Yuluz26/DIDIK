/*
 * Islands on open water, for the front page: each island is a soft-edged blob (the same outlines
 * the page always had), painted in layers like the worlds' ground: a lagoon, surf, an earth bank,
 * a beach, then grass. Nothing is painted beyond the lagoon, so the picture floats on the sea
 * behind it.
 */
import { TILE } from './cache';
import { type GroundShape, type Land, landMap, paintGround } from './ground';
import type { Pix } from './pix';

/** One island's outline: an ellipse (in tiles) pushed in and out by `reach`, turned by `turn`. */
export interface Isle {
	cx: number;
	cy: number;
	rx: number;
	ry: number;
	reach: number[];
	turn?: number;
	/** What lies on the beach, from the outside in; `k` is its size against the island, `dy` how far it sits up (-) or down (+), in tiles. */
	tops?: { land: Land; k: number; dy: number }[];
}

type Test = (x: number, y: number) => boolean;

/** A smooth radius around the island: the reach values joined by a Catmull-Rom curve. */
function radius(reach: readonly number[], turn: number) {
	const n = reach.length;
	return (theta: number) => {
		const t = ((((theta - turn) / (Math.PI * 2)) * n) % n + n) % n;
		const i = Math.floor(t);
		const f = t - i;
		const [p0, p1, p2, p3] = [reach[(i - 1 + n) % n], reach[i], reach[(i + 1) % n], reach[(i + 2) % n]];
		return 0.5 * (2 * p1 + (p2 - p0) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f + (3 * p1 - p0 - 3 * p2 + p3) * f * f * f);
	};
}

/** The pixels inside an island, its size multiplied by `k` and moved down by `dy` tiles. */
export function inIsle(isle: Isle, k = 1, dy = 0): Test {
	const r = radius(isle.reach, isle.turn ?? 0);
	return (x, y) => {
		const u = ((x + 0.5) / TILE - isle.cx) / (isle.rx * k);
		const v = ((y + 0.5) / TILE - isle.cy - dy) / (isle.ry * k);
		return Math.hypot(u, v) <= r(Math.atan2(v, u));
	};
}

export const inEllipse =
	(cx: number, cy: number, rx: number, ry: number): Test =>
	(x, y) =>
		(((x + 0.5) / TILE - cx) / rx) ** 2 + (((y + 0.5) / TILE - cy) / ry) ** 2 <= 1;

export const inPoly =
	(pts: readonly (readonly [number, number])[]): Test =>
	(x, y) => {
		const px = (x + 0.5) / TILE;
		const py = (y + 0.5) / TILE;
		let inside = false;
		for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
			const [xi, yi] = pts[i];
			const [xj, yj] = pts[j];
			if (yi > py !== yj > py && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi) inside = !inside;
		}
		return inside;
	};

/** Points along cubic curves (tile units), for a winding path: `from`, then (c1, c2, to) triples. */
export function curve(from: readonly [number, number], ...segments: [number, number][][]): [number, number][] {
	const out: [number, number][] = [[from[0], from[1]]];
	let [x0, y0] = from;
	for (const [[x1, y1], [x2, y2], [x3, y3]] of segments) {
		for (let i = 1; i <= 12; i++) {
			const t = i / 12;
			const u = 1 - t;
			out.push([u * u * u * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t * t * t * x3, u * u * u * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t * t * t * y3]);
		}
		[x0, y0] = [x3, y3];
	}
	return out;
}

/** The pixels within half of `width` tiles of a line of points. */
export function alongPath(pts: readonly (readonly [number, number])[], width: number): Test {
	const half = width / 2;
	return (x, y) => {
		const px = (x + 0.5) / TILE;
		const py = (y + 0.5) / TILE;
		for (let i = 1; i < pts.length; i++) {
			const [ax, ay] = pts[i - 1];
			const [bx, by] = pts[i];
			const dx = bx - ax;
			const dy = by - ay;
			const len = dx * dx + dy * dy || 1;
			const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / len));
			if (Math.hypot(px - (ax + dx * t), py - (ay + dy * t)) <= half) return true;
		}
		return false;
	};
}

export interface IslandPlan {
	/** Size in tiles. */
	w: number;
	h: number;
	isles: Isle[];
	seed: number;
	/** Shapes laid over the beach and grass (paths, a jetty), in pixels' tests; see the helpers above. */
	over?: GroundShape[];
	meadow?: number;
	/** How wide the lagoon reaches, against the island (about 1.2). */
	lagoon?: number;
}

const GRASS_TOP = [{ land: 'grass' as Land, k: 0.88, dy: -0.04 }];

/** Paints the islands, w × h tiles, transparent beyond their lagoons. */
export function paintIsland(plan: IslandPlan): Pix {
	const map = landMap(Array.from({ length: Math.ceil(plan.h) }, () => 'n'.repeat(Math.ceil(plan.w))), { n: 'none' });
	const shapes: GroundShape[] = [];
	const layer = (land: Land, k: number, dy: number) => {
		for (const isle of plan.isles) shapes.push({ land, test: inIsle(isle, k, dy) });
	};
	const lagoon = plan.lagoon ?? 1.26;
	layer('water', lagoon, 0.06);
	layer('foam', 1 + (lagoon - 1) * 0.28, 0.04);
	layer('cliff', 1, 0.2);
	layer('sand', 1, 0);
	for (const isle of plan.isles) for (const top of isle.tops ?? GRASS_TOP) shapes.push({ land: top.land, test: inIsle(isle, top.k, top.dy) });
	shapes.push(...(plan.over ?? []));
	const full = paintGround(map, { seed: plan.seed, shapes, meadow: plan.meadow ?? 0.35, corner: 0 });
	return full.crop(0, 0, Math.round(plan.w * TILE), Math.round(plan.h * TILE));
}
