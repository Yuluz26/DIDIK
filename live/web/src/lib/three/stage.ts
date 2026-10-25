// The 3D games draw with three.js. This module, and everything that imports
// `three`, is only ever loaded with a dynamic import from those games, so the rest of the app does
// not download it.
//
// One WebGL renderer serves the whole visit: a game's scene mounts and unmounts between stages,
// and browsers cap (and leak on churn) live WebGL contexts, so the canvas moves between
// containers instead of being rebuilt.

import {
	Mesh,
	NearestFilter,
	NeutralToneMapping,
	OrthographicCamera,
	PlaneGeometry,
	SRGBColorSpace,
	Scene as ThreeScene,
	ShaderMaterial,
	Vector2,
	Vector3,
	WebGLRenderTarget,
	WebGLRenderer,
	type PerspectiveCamera,
	type Scene
} from 'three';

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
		// Pixels are meant to be hard edged: no smoothing between them.
		antialias: false,
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
			// A kart at the very edge of the picture keeps its whole label inside it.
			tag.x = Math.min(Math.max(tag.x, tag.w / 2 + 4), width - tag.w / 2 - 4);
			for (const other of taken) {
				const across = Math.abs(tag.x - other.x) < (tag.w + other.w) / 2 + 2;
				const overlap = tag.y > other.y - other.h - 2 && tag.y - tag.h < other.y;
				if (across && overlap) tag.y = other.y - other.h - 3;
			}
			tag.y = Math.max(tag.y, tag.h + 4);
			taken.push(tag);
			tag.el.style.visibility = 'visible';
			tag.el.style.transform = `translate3d(${tag.x.toFixed(1)}px, ${tag.y.toFixed(1)}px, 0) translate(-50%, -100%)`;
		}
	}
}

/**
 * The pixel look for every 3D world: the scene is drawn small (see `pixelSize`), then a last pass
 * lays dark one-pixel edges where one thing ends and another begins, and rounds every colour to a
 * limited set, dithered in a fixed pattern, as an old console would. The browser then magnifies the
 * small picture without smoothing it.
 */
export class PixelPass {
	private readonly target = new WebGLRenderTarget(1, 1, { minFilter: NearestFilter, magFilter: NearestFilter });
	private readonly quad = new ThreeScene();
	private readonly camera = new OrthographicCamera(-1, 1, 1, -1, 0, 1);
	private readonly material: ShaderMaterial;
	private readonly size = new Vector2(1, 1);

	constructor(private readonly gl: WebGLRenderer) {
		this.material = new ShaderMaterial({
			uniforms: { tDiffuse: { value: this.target.texture }, texel: { value: new Vector2(1, 1) }, levels: { value: 22 } },
			vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
			fragmentShader: `
				uniform sampler2D tDiffuse;
				uniform vec2 texel;
				uniform float levels;
				varying vec2 vUv;
				float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }
				float bayer(vec2 p) {
					vec2 q = mod(floor(p), 4.0);
					float i = q.x + q.y * 4.0;
					// 4x4 ordered dither, 0..15
					float m = i < 8.0
						? (i < 4.0 ? (i < 1.0 ? 0.0 : i < 2.0 ? 8.0 : i < 3.0 ? 2.0 : 10.0) : (i < 5.0 ? 12.0 : i < 6.0 ? 4.0 : i < 7.0 ? 14.0 : 6.0))
						: (i < 12.0 ? (i < 9.0 ? 3.0 : i < 10.0 ? 11.0 : i < 11.0 ? 1.0 : 9.0) : (i < 13.0 ? 15.0 : i < 14.0 ? 7.0 : i < 15.0 ? 13.0 : 5.0));
					return m / 16.0;
				}
				void main() {
					vec3 c = texture2D(tDiffuse, vUv).rgb;
					float l = luma(c);
					float up = luma(texture2D(tDiffuse, vUv + vec2(0.0, texel.y)).rgb);
					float left = luma(texture2D(tDiffuse, vUv - vec2(texel.x, 0.0)).rgb);
					float down = luma(texture2D(tDiffuse, vUv - vec2(0.0, texel.y)).rgb);
					float right = luma(texture2D(tDiffuse, vUv + vec2(texel.x, 0.0)).rgb);
					// a pixel that is darker than a neighbour by a clear step is the edge of its object
					float step_ = max(max(up - l, left - l), max(down - l, right - l));
					float edge = smoothstep(0.045, 0.09, step_ / max(0.08, l + 0.12));
					c *= 1.0 - 0.42 * edge;
					gl_FragColor = vec4(c, 1.0);
					#include <tonemapping_fragment>
					#include <colorspace_fragment>
					float d = bayer(gl_FragCoord.xy) - 0.5;
					vec3 q = floor(gl_FragColor.rgb * levels + 0.5 + d * 0.55) / levels;
					gl_FragColor = vec4(clamp(q, 0.0, 1.0), 1.0);
				}`,
			depthTest: false,
			depthWrite: false
		});
		this.quad.add(new Mesh(new PlaneGeometry(2, 2), this.material));
	}

	setSize(width: number, height: number): void {
		this.size.set(width, height);
		this.target.setSize(width, height);
		(this.material.uniforms.texel.value as Vector2).set(1 / width, 1 / height);
	}

	render(scene: Scene, camera: PerspectiveCamera): void {
		this.gl.setRenderTarget(this.target);
		this.gl.render(scene, camera);
		this.gl.setRenderTarget(null);
		this.gl.render(this.quad, this.camera);
	}

	dispose(): void {
		this.target.dispose();
		this.material.dispose();
	}
}

/** CSS pixels to a pixel of the 3D picture: the same chunky size the 2D worlds are drawn at. */
export function pixelSize(cssWidth: number): number {
	return Math.min(4, Math.max(2, Math.round(cssWidth / 280)));
}
