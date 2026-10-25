// Shared pieces for the low-poly worlds: the brand palette, flat-shaded vertex-coloured parts merged
// into one mesh (one draw call per object, which keeps phones fast), a gradient sky, soft blob
// shadows instead of real-time shadow maps, the light rig, and easing.

import {
	BufferAttribute,
	BufferGeometry,
	CanvasTexture,
	Color,
	DataTexture,
	DirectionalLight,
	HemisphereLight,
	Mesh,
	MeshBasicMaterial,
	MeshToonMaterial,
	NearestFilter,
	PlaneGeometry,
	RedFormat,
	SRGBColorSpace,
	type Material,
	type Object3D,
	type Scene,
	type Texture
} from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

/** The app's colours (app.css), plus a few for the worlds. */
export const C = {
	ink: 0x1f2d27,
	night: 0x13303d,
	paper: 0xfff8ec,
	sun: 0xffb627,
	sunDeep: 0xc98400,
	coral: 0xd0452f,
	sea: 0x12847a,
	sky: 0x2d78c4,
	leaf: 0x6cb33f,
	grass: 0x3d7d47,
	asphalt: 0x2f3539,
	white: 0xf4f1ea,
	wood: 0x9a6235,
	woodDark: 0x6e4122,
	skin: 0xe7b98a
} as const;

/** The avatar colours (names.ts COLOURS) as numbers, for karts, kits and tower blocks. */
export function hex(css: string | undefined, fallback: number = C.sun): number {
	return css && /^#[0-9a-f]{6}$/i.test(css) ? parseInt(css.slice(1), 16) : fallback;
}

export interface Part {
	geometry: BufferGeometry;
	color: number;
}

/** Paints each part one colour and merges them into a single geometry. */
export function merge(parts: Part[]): BufferGeometry {
	const painted = parts.map(({ geometry, color }) => {
		const flat = geometry.index ? geometry.toNonIndexed() : geometry;
		if (flat !== geometry) geometry.dispose();
		const tint = new Color(color);
		const count = flat.getAttribute('position').count;
		const colours = new Float32Array(count * 3);
		for (let i = 0; i < count; i++) colours.set([tint.r, tint.g, tint.b], i * 3);
		flat.setAttribute('color', new BufferAttribute(colours, 3));
		flat.deleteAttribute('uv');
		return flat;
	});
	const merged = mergeGeometries(painted, false);
	painted.forEach((g) => g.dispose());
	if (!merged) throw new Error('parts could not be merged');
	merged.computeVertexNormals();
	return merged;
}

let steps: DataTexture | null = null;

/** Light falls in four hard steps, like the shading in a drawing, not in a smooth gradient. */
function toonSteps(): DataTexture {
	if (!steps) {
		steps = new DataTexture(new Uint8Array([88, 150, 210, 255]), 4, 1, RedFormat);
		steps.minFilter = NearestFilter;
		steps.magFilter = NearestFilter;
		steps.needsUpdate = true;
	}
	return steps;
}

/** A toon material that takes the options a Lambert one did (flat shading is how every part is cut). */
export class ToonMaterial extends MeshToonMaterial {
	constructor(params: ConstructorParameters<typeof MeshToonMaterial>[0] & { flatShading?: boolean } = {}) {
		const { flatShading: _flat, ...rest } = params;
		void _flat;
		super({ gradientMap: toonSteps(), ...rest });
	}
}

/** The one material most low-poly objects share: stepped shading, colours from the vertices. */
export function painted(): MeshToonMaterial {
	return new MeshToonMaterial({ vertexColors: true, gradientMap: toonSteps() });
}

export function solid(color: number): MeshToonMaterial {
	return new MeshToonMaterial({ color, gradientMap: toonSteps() });
}

/** A vertical gradient for `scene.background`: cheap, and it never shows a seam. */
export function skyTexture(stops: [number, string][]): CanvasTexture {
	const canvas = document.createElement('canvas');
	canvas.width = 4;
	canvas.height = 256;
	const ctx = canvas.getContext('2d')!;
	const gradient = ctx.createLinearGradient(0, 0, 0, 256);
	for (const [at, colour] of stops) gradient.addColorStop(at, colour);
	ctx.fillStyle = gradient;
	ctx.fillRect(0, 0, 4, 256);
	const texture = new CanvasTexture(canvas);
	texture.colorSpace = SRGBColorSpace;
	return texture;
}

/** A small canvas drawn once and used as a texture (stripes, crowds, windows, a checkered line). */
export function drawnTexture(width: number, height: number, draw: (ctx: CanvasRenderingContext2D) => void): CanvasTexture {
	const canvas = document.createElement('canvas');
	canvas.width = width;
	canvas.height = height;
	draw(canvas.getContext('2d')!);
	const texture = new CanvasTexture(canvas);
	texture.colorSpace = SRGBColorSpace;
	texture.anisotropy = 4;
	return texture;
}

let blobTexture: CanvasTexture | null = null;

/** A soft dark ellipse under an object, in place of a real shadow. */
export function blobShadow(width: number, depth: number, opacity = 0.32): Mesh {
	blobTexture ??= drawnTexture(64, 64, (ctx) => {
		const g = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
		g.addColorStop(0, 'rgba(0,0,0,1)');
		g.addColorStop(1, 'rgba(0,0,0,0)');
		ctx.fillStyle = g;
		ctx.fillRect(0, 0, 64, 64);
	});
	const mesh = new Mesh(
		new PlaneGeometry(width, depth),
		new MeshBasicMaterial({ map: blobTexture, transparent: true, opacity, depthWrite: false, color: 0x000000 })
	);
	mesh.rotation.x = -Math.PI / 2;
	mesh.renderOrder = 1;
	return mesh;
}

/** Sky light from above, warm sun from one side. */
export function light(scene: Scene, { sky = 0xdcecff, ground = 0x4a5a3a, sun = 0xfff1d6, strength = 1 } = {}): DirectionalLight {
	scene.add(new HemisphereLight(sky, ground, 1.9 * strength));
	const key = new DirectionalLight(sun, 2.1 * strength);
	key.position.set(-30, 50, 25);
	scene.add(key);
	return key;
}

/** Disposes every geometry, material and texture under `root`. */
export function disposeTree(root: Object3D, extra: (Texture | Material | BufferGeometry)[] = []): void {
	root.traverse((node) => {
		const mesh = node as Mesh;
		mesh.geometry?.dispose();
		const materials = Array.isArray(mesh.material) ? mesh.material : mesh.material ? [mesh.material] : [];
		for (const material of materials) {
			for (const value of Object.values(material)) if ((value as Texture)?.isTexture) (value as Texture).dispose();
			material.dispose();
		}
	});
	extra.forEach((item) => item.dispose());
}

// ------------------------------------------------------------------ motion

export const ease = {
	outCubic: (t: number) => 1 - Math.pow(1 - t, 3),
	inOutCubic: (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
	outBack: (t: number) => {
		const c = 1.70158;
		return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2);
	}
};

/** Frame-rate independent approach of `current` toward `target`. */
export function damp(current: number, target: number, lambda: number, dt: number): number {
	return target + (current - target) * Math.exp(-lambda * dt);
}

export const clamp01 = (t: number) => Math.min(1, Math.max(0, t));

/** A geometry with a flat bottom at y = 0 (three's primitives are centred). */
export function seated<T extends BufferGeometry>(geometry: T, y = 0): T {
	geometry.computeBoundingBox();
	const box = geometry.boundingBox!;
	geometry.translate(0, y - box.min.y, 0);
	return geometry;
}
