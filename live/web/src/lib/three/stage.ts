// The 3D games draw with three.js. This module, and everything that imports
// `three`, is only ever loaded with a dynamic import from those games, so the rest of the app does
// not download it.
//
// One WebGL renderer serves the whole visit: a game's scene mounts and unmounts between stages,
// and browsers cap (and leak on churn) live WebGL contexts, so the canvas moves between
// containers instead of being rebuilt.

import { NeutralToneMapping, SRGBColorSpace, Vector3, WebGLRenderer, type PerspectiveCamera, type Scene } from 'three';

/** A game's 3D world, drawn by `Stage3D`. */
export interface World3D {
	readonly scene: Scene;
	readonly camera: PerspectiveCamera;
	/** Set by the stage: asks for frames again after the world went still (e.g. new state arrived). */
	wake?: () => void;
	resize(width: number, height: number): void;
	/** Advances animations by `dt` seconds; returns true while anything is still moving. */
	tick(dt: number, time: number): boolean;
	/** After each drawn frame: place HTML labels over the scene. */
	afterRender?(width: number, height: number): void;
	dispose(): void;
}

let shared: WebGLRenderer | null = null;

/** The page's renderer, created on first use. Throws when the device has no WebGL. */
export function renderer(): WebGLRenderer {
	if (shared) return shared;
	// Ask quietly first: three.js reports a failed context as a console error.
	const probe = document.createElement('canvas');
	const context = probe.getContext('webgl2') ?? probe.getContext('webgl');
	if (!context) throw new Error('WebGL is not available');
	context.getExtension('WEBGL_lose_context')?.loseContext();
	const created = new WebGLRenderer({
		// Multisampling is costly on phones and barely visible on dense screens.
		antialias: window.devicePixelRatio < 2,
		powerPreference: 'high-performance'
	});
	created.outputColorSpace = SRGBColorSpace;
	// Neutral keeps the brand colours' hue and saturation, unlike filmic curves.
	created.toneMapping = NeutralToneMapping;
	created.domElement.addEventListener('webglcontextlost', (event) => event.preventDefault());
	shared = created;
	return created;
}

export function reducedMotion(): boolean {
	return typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * HTML name tags pinned to points in the scene. A label registers itself with `attach(id)` (a
 * Svelte attachment); the world calls `place` after each frame with where each id now is.
 */
export class Tags {
	private readonly els = new Map<string, HTMLElement>();
	private readonly point = new Vector3();

	attach(id: string) {
		return (el: HTMLElement) => {
			this.els.set(id, el);
			return () => {
				if (this.els.get(id) === el) this.els.delete(id);
			};
		};
	}

	get size(): number {
		return this.els.size;
	}

	place(camera: PerspectiveCamera, width: number, height: number, where: (id: string, out: Vector3) => boolean): void {
		const placed: { el: HTMLElement; x: number; y: number; w: number; h: number }[] = [];
		for (const [id, el] of this.els) {
			if (!where(id, this.point)) {
				el.style.visibility = 'hidden';
				continue;
			}
			this.point.project(camera);
			if (this.point.z > 1) {
				el.style.visibility = 'hidden';
				continue;
			}
			placed.push({
				el,
				x: (this.point.x * 0.5 + 0.5) * width,
				y: (-this.point.y * 0.5 + 0.5) * height,
				w: el.offsetWidth,
				h: el.offsetHeight
			});
		}
		// Nearer the bottom of the screen means nearer the camera: those keep their place, and a
		// label that would cover one already placed moves up above it.
		placed.sort((a, b) => b.y - a.y);
		const taken: { x: number; y: number; w: number; h: number }[] = [];
		for (const tag of placed) {
			for (const other of taken) {
				const across = Math.abs(tag.x - other.x) < (tag.w + other.w) / 2 + 2;
				const overlap = tag.y > other.y - other.h - 2 && tag.y - tag.h < other.y;
				if (across && overlap) tag.y = other.y - other.h - 3;
			}
			taken.push(tag);
			tag.el.style.visibility = 'visible';
			tag.el.style.transform = `translate3d(${tag.x.toFixed(1)}px, ${tag.y.toFixed(1)}px, 0) translate(-50%, -100%)`;
		}
	}
}
