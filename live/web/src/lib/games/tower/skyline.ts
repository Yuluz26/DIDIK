// Menara 118 in 3D: the class's tower rising inside a faint outline of Merdeka 118, next to Komtar,
// Menara Kuala Lumpur and the Petronas Twin Towers at their real heights (1 unit = 1 m), in a city
// at dusk. On a phone the camera stays at the top of the tower, where the player's block slides
// back and forth until they drop it.

import {
	BoxGeometry,
	BufferGeometry,
	Color,
	ConeGeometry,
	CylinderGeometry,
	DynamicDrawUsage,
	EdgesGeometry,
	Fog,
	Group,
	InstancedMesh,
	LatheGeometry,
	LineBasicMaterial,
	LineSegments,
	Matrix4,
	Mesh,
	NearestFilter,
	Object3D,
	PerspectiveCamera,
	PlaneGeometry,
	Quaternion,
	RepeatWrapping,
	Scene,
	SphereGeometry,
	Vector2,
	Vector3
} from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { Tags, reducedMotion, type World3D } from '$lib/three/stage';
import { ToonMaterial, clamp01, damp, disposeTree, drawnTexture, ease, hex, light, merge, skyTexture, type Part } from '$lib/three/kit';

export const GOAL = 679;
const BODY = 600; // where Merdeka 118's spire begins
const MAX_OFFSET = 0.45;

/** The tower's half-width at height y: tapering to the crown, then the spire. */
export function radius(y: number): number {
	if (y < BODY) return 30 - 18 * (y / BODY);
	return Math.max(1.2, 12 - 10.8 * ((y - BODY) / (GOAL - BODY)));
}

export interface Block {
	who: string;
	m: number;
	x: number;
	base: number;
}

export interface Landmark {
	key: string;
	name: string;
	m: number;
	passed: boolean;
}

const LANDMARKS: Record<string, { x: number; z: number }> = {
	komtar: { x: -300, z: -60 },
	menarakl: { x: -165, z: -170 },
	petronas: { x: 240, z: -130 },
	merdeka: { x: 0, z: 0 }
};

export class SkylineWorld implements World3D {
	readonly scene = new Scene();
	readonly camera = new PerspectiveCamera(35, 16 / 9, 1, 6000);
	readonly tags = new Tags();
	wake?: () => void;

	private glass: InstancedMesh;
	private bands: InstancedMesh;
	private capacity = 0;
	private readonly lower: Mesh; // the part of the tower below the blocks a phone is sent
	private readonly slider: Group;
	private readonly sliderBand: ToonMaterial;
	private readonly flash: LineSegments;
	private readonly target: LineSegments; // where a block lands whole: the middle of the top
	private readonly landmarks = new Map<string, Group>();
	private readonly matrix = new Matrix4();
	private readonly quat = new Quaternion();
	private readonly scale = new Vector3();
	private readonly at = new Vector3();
	private readonly tint = new Color();
	private readonly still = reducedMotion();
	private blocks: Block[] = [];
	private colours = new Map<string, number>();
	private height = 0;
	private shownHeight = 0;
	private block = 10;
	private time = 0;
	private sliding = false;
	private slideStart = 0;
	private falling: { from: number; t: number } | null = null;
	private flashT = 1;
	private camY = 0;

	constructor(private readonly view: 'host' | 'phone') {
		this.scene.background = skyTexture([
			[0, '#14243d'],
			[0.5, '#3c4f72'],
			[0.82, '#d7865e'],
			[1, '#f2b077']
		]);
		this.scene.fog = new Fog(0xc98a6a, view === 'host' ? 1300 : 500, view === 'host' ? 3600 : 2200);
		light(this.scene, { sky: 0xb8c8ec, ground: 0x2a3340, sun: 0xffc596, strength: 1 }).position.set(-400, 300, 500);

		this.scene.add(this.ground(), this.city(), this.ghost());
		for (const key of ['komtar', 'menarakl', 'petronas']) {
			const group = this.landmark(key);
			this.landmarks.set(key, group);
			this.scene.add(group);
		}

		this.glass = this.instanced(512, 0xffffff);
		this.bands = this.instanced(512, 0xffffff);
		this.capacity = 512;

		this.lower = new Mesh(new CylinderGeometry(1, 1, 1, 8).rotateY(Math.PI / 8).translate(0, 0.5, 0), new ToonMaterial({ color: 0x6fb6b7, flatShading: true }));
		this.lower.visible = false;
		this.scene.add(this.lower);

		this.sliderBand = new ToonMaterial({ color: 0xffb627, flatShading: true });
		this.slider = new Group();
		const slab = new Mesh(
			new CylinderGeometry(1, 1, 1, 8).rotateY(Math.PI / 8).translate(0, 0.5, 0),
			new ToonMaterial({ color: 0xbff3ee, emissive: 0x2a6b68, flatShading: true })
		);
		const band = new Mesh(new CylinderGeometry(1.03, 1.03, 0.22, 8).rotateY(Math.PI / 8).translate(0, 0.11, 0), this.sliderBand);
		this.slider.add(slab, band);
		this.slider.visible = false;
		this.scene.add(this.slider);

		this.flash = new LineSegments(new EdgesGeometry(new CylinderGeometry(1, 1, 0.01, 8).rotateY(Math.PI / 8)), new LineBasicMaterial({ color: 0xffe08a, transparent: true, opacity: 0 }));
		this.target = new LineSegments(new EdgesGeometry(new CylinderGeometry(1, 1, 0.01, 8).rotateY(Math.PI / 8)), new LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.85 }));
		this.target.visible = false;
		this.scene.add(this.flash, this.target);
		if (view === 'phone') this.camera.fov = 46;
	}

	// ------------------------------------------------------------------ state from the server

	update(state: { height: number; blocks: Block[]; block?: number; landmarks: Landmark[] }, colours: Map<string, string | undefined>): void {
		for (const [id, colour] of colours) this.colours.set(id, hex(colour));
		const grew = state.height > this.height;
		this.height = state.height;
		this.blocks = state.blocks;
		if (state.block) this.block = state.block;
		if (grew && this.falling) this.falling = null;
		for (const mark of state.landmarks) {
			const group = this.landmarks.get(mark.key);
			if (group) group.userData.passed = mark.passed;
		}
		this.paint();
		this.wake?.();
	}

	/** Phone: the player's block appears above the tower and slides until it is dropped. */
	slide(on: boolean, colour?: string): void {
		if (on && !this.sliding) this.slideStart = this.time;
		this.sliding = on;
		if (colour) this.sliderBand.color.setHex(hex(colour));
		this.slider.visible = on || !!this.falling;
		this.wake?.();
	}

	/** Phone: where the sliding block is now, as a share of the tower's width (what the server takes). */
	drop(): number {
		const offset = this.offset();
		this.falling = { from: this.slider.position.y, t: 0 };
		this.sliding = false;
		this.wake?.();
		return offset;
	}

	/** A ring of light round the top: the block landed dead centre. */
	perfect(): void {
		this.flashT = 0;
		this.wake?.();
	}

	private offset(): number {
		// A triangle wave: steady speed, turning at each edge (slower when motion is reduced).
		const period = this.still ? 4.4 : 2.8;
		const phase = (((this.time - this.slideStart) / period) % 1 + 1) % 1;
		const wave = phase < 0.5 ? phase * 4 - 1 : 3 - phase * 4;
		return wave * MAX_OFFSET;
	}

	// ------------------------------------------------------------------ the tower

	private instanced(capacity: number, color: number): InstancedMesh {
		const geometry = new CylinderGeometry(1, 1, 1, 8).rotateY(Math.PI / 8).translate(0, 0.5, 0);
		const mesh = new InstancedMesh(geometry, new ToonMaterial({ color, flatShading: true }), capacity);
		mesh.instanceMatrix.setUsage(DynamicDrawUsage);
		mesh.count = 0;
		mesh.frustumCulled = false;
		this.scene.add(mesh);
		return mesh;
	}

	private grow(count: number): void {
		if (count <= this.capacity) return;
		this.capacity = Math.max(count, this.capacity * 2);
		for (const old of [this.glass, this.bands]) {
			this.scene.remove(old);
			old.geometry.dispose();
			(old.material as ToonMaterial).dispose();
			old.dispose();
		}
		this.glass = this.instanced(this.capacity, 0xffffff);
		this.bands = this.instanced(this.capacity, 0xffffff);
	}

	/** Every block as a glass slab, offset where it landed, with a band in its builder's colour. */
	private paint(): void {
		this.grow(this.blocks.length);
		this.blocks.forEach((block, i) => {
			const r = radius(block.base + block.m / 2);
			const x = block.x * 2 * r;
			this.matrix.compose(this.at.set(x, block.base, 0), this.quat, this.scale.set(r, block.m, r));
			this.glass.setMatrixAt(i, this.matrix);
			this.glass.setColorAt(i, this.tint.setHex(i % 2 ? 0x7cc3c1 : 0x8ed1cc));
			const band = Math.min(block.m * 0.3, 3);
			this.matrix.compose(this.at.set(x, block.base, 0), this.quat, this.scale.set(r * 1.02, band, r * 1.02));
			this.bands.setMatrixAt(i, this.matrix);
			this.bands.setColorAt(i, this.tint.setHex(this.colours.get(block.who) ?? 0xffb627));
		});
		this.glass.count = this.bands.count = this.blocks.length;
		for (const mesh of [this.glass, this.bands]) {
			mesh.instanceMatrix.needsUpdate = true;
			if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;
		}
		// A phone only has the top blocks: the rest of the tower is one plain column below them.
		const bottom = this.blocks.length ? this.blocks[0].base : this.height;
		this.lower.visible = this.view === 'phone' && bottom > 0.5;
		if (this.lower.visible) {
			const r = radius(bottom / 2);
			this.lower.scale.set(r, bottom, r);
		}
	}

	// ------------------------------------------------------------------ frames

	resize(width: number, height: number): void {
		this.camera.aspect = width / height;
		this.camera.updateProjectionMatrix();
	}

	tick(dt: number): boolean {
		this.time += dt;
		let moving = false;
		this.shownHeight = damp(this.shownHeight, this.height, this.still ? 60 : 4, dt);
		if (Math.abs(this.shownHeight - this.height) > 0.05) moving = true;

		// Landmarks the tower has passed glow warm.
		for (const group of this.landmarks.values()) {
			const target = group.userData.passed ? 1 : 0;
			const glow = (group.userData.glow ?? 0) as number;
			const next = damp(glow, target, 3, dt);
			group.userData.glow = next;
			const material = (group.children[0] as Mesh).material as ToonMaterial;
			material.emissive.setRGB(0.55 * next, 0.33 * next, 0.08 * next);
			if (Math.abs(next - target) > 0.01) moving = true;
		}

		const top = this.height;
		if (this.sliding || this.falling) {
			const r = radius(top + this.block / 2);
			const lift = Math.max(this.block * 0.8, 6);
			let y = top + lift;
			let x = this.offset() * 2 * r;
			if (this.falling) {
				this.falling.t += dt / 0.28;
				y = top + lift * (1 - ease.inOutCubic(clamp01(this.falling.t)));
				x = this.slider.position.x;
				if (this.falling.t > 3) this.falling = null;
			}
			this.slider.visible = true;
			this.slider.position.set(x, y, 0);
			this.slider.scale.set(r, this.block, r);
			this.target.visible = this.sliding;
			this.target.position.set(0, top + 0.3, 0);
			this.target.scale.set(r, 1, r);
			moving = true;
		} else {
			this.slider.visible = false;
			this.target.visible = false;
		}

		if (this.flashT < 1) {
			this.flashT += dt / 0.8;
			const t = clamp01(this.flashT);
			const r = radius(top) * (1 + t * 0.9);
			this.flash.position.set(0, top + 0.2, 0);
			this.flash.scale.set(r, 1, r);
			(this.flash.material as LineBasicMaterial).opacity = 1 - t;
			moving = true;
		}

		this.aim(dt);
		return moving || (this.view === 'host' && !this.still);
	}

	afterRender(width: number, height: number): void {
		this.tags.place(this.camera, width, height, (id, out) => {
			if (id === 'kita') {
				out.set(0, this.shownHeight + 8, 0);
				return true;
			}
			const spot = LANDMARKS[id];
			const peak = { komtar: 249, menarakl: 421, petronas: 452 }[id as 'komtar'];
			if (!spot || !peak) return false;
			out.set(spot.x + (id === 'petronas' ? 32 : 0), peak + 12, spot.z);
			return true;
		});
	}

	private aim(dt: number): void {
		if (this.view === 'host') {
			// The whole skyline, turning very slowly.
			const swing = this.still ? 0 : Math.sin(this.time * 0.04) * 0.12;
			const d = this.camera.aspect < 1.25 ? 1500 : 1180;
			this.camera.position.set(Math.sin(swing) * d, 300, Math.cos(swing) * d);
			this.camera.lookAt(0, 330, 0);
			return;
		}
		// A phone: at the top of the tower, close enough to see the block land.
		const target = this.shownHeight + Math.max(this.block * 1.2, 12);
		this.camY = this.camY ? damp(this.camY, target, 3, dt) : target;
		const back = Math.max(radius(this.height) * 6.5, 110);
		this.camera.position.set(back * 0.18, this.camY + back * 0.22, back);
		this.camera.lookAt(0, this.camY - back * 0.06, 0);
	}

	// ------------------------------------------------------------------ the city

	private ground(): Mesh {
		const mesh = new Mesh(new PlaneGeometry(9000, 9000), new ToonMaterial({ color: 0x24333d }));
		mesh.rotation.x = -Math.PI / 2;
		return mesh;
	}

	/** Merdeka 118 as a faint outline: the height the class is building to. */
	private ghost(): Object3D {
		const profile = [new Vector2(30, 0), new Vector2(12, BODY), new Vector2(1.2, GOAL)];
		const lathe = new LatheGeometry(profile, 8);
		lathe.rotateY(Math.PI / 8);
		const edges = new LineSegments(new EdgesGeometry(lathe, 10), new LineBasicMaterial({ color: 0xbfeeea, transparent: true, opacity: 0.4 }));
		lathe.dispose();
		return edges;
	}

	/** Lower buildings with lit windows, merged into one mesh, kept clear of the towers. */
	private city(): Object3D {
		const windows = drawnTexture(64, 64, (ctx) => {
			ctx.fillStyle = '#2b3a4a';
			ctx.fillRect(0, 0, 64, 64);
			let seed = 5;
			const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
			for (let y = 4; y < 64; y += 8)
				for (let x = 4; x < 64; x += 8) {
					ctx.fillStyle = rand() < 0.45 ? '#ffd58a' : '#3a4c5e';
					ctx.fillRect(x, y, 4, 5);
				}
		});
		windows.wrapS = windows.wrapT = RepeatWrapping;
		// Seen from far away a window must still cover a few pixels of the small picture, so one cell of
		// the texture is about twelve metres: bigger windows, fewer of them, and no speckle.
		windows.magFilter = NearestFilter;
		const boxes: BufferGeometry[] = [];
		let seed = 21;
		const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
		for (let i = 0; i < 160; i++) {
			const x = (rand() - 0.5) * 1500;
			const z = -120 - rand() * 900 + (rand() < 0.3 ? 700 : 0);
			const clear = Object.values(LANDMARKS).every((p) => Math.hypot(p.x - x, p.z - z) > 110) && Math.hypot(x, z) > 120;
			if (!clear) continue;
			const w = 30 + rand() * 40;
			const h = 25 + Math.pow(rand(), 2) * 170;
			const box = new BoxGeometry(w, h, w * (0.7 + rand() * 0.6));
			const uv = box.getAttribute('uv');
			for (let k = 0; k < uv.count; k++) uv.setXY(k, uv.getX(k) * (w / 96), uv.getY(k) * (h / 96));
			box.translate(x, h / 2, z);
			boxes.push(box);
		}
		const merged = mergeGeometries(boxes, false)!;
		boxes.forEach((b) => b.dispose());
		return new Mesh(merged, new ToonMaterial({ map: windows, emissive: 0xffffff, emissiveMap: windows, emissiveIntensity: 0.55 }));
	}

	/** Komtar, Menara Kuala Lumpur and the Petronas Twin Towers, simplified, at their real heights. */
	private landmark(key: string): Group {
		const group = new Group();
		const parts: Part[] = [];
		const add = (g: BufferGeometry, x: number, y: number, z: number, color: number) => {
			g.translate(x, y, z);
			parts.push({ geometry: g, color });
		};
		const steel = 0xc5cdd4;
		if (key === 'komtar') {
			add(new CylinderGeometry(17, 18, 236, 12), 0, 118, 0, 0xd9d6cc);
			add(new CylinderGeometry(15, 17, 13, 12), 0, 242.5, 0, 0x9aa5ad);
			add(new SphereGeometry(30, 10, 6, 0, Math.PI * 2, 0, Math.PI / 2), 60, 0, 30, 0xd9d6cc);
		} else if (key === 'menarakl') {
			add(new CylinderGeometry(5, 9, 276, 10), 0, 138, 0, 0xd9d6cc);
			const pod = new SphereGeometry(19, 12, 8);
			pod.scale(1, 0.75, 1);
			add(pod, 0, 300, 0, 0xb9c3cb);
			add(new CylinderGeometry(13, 16, 14, 12), 0, 322, 0, 0xd9d6cc);
			add(new CylinderGeometry(1.6, 2.6, 86, 6), 0, 378, 0, 0xd9d6cc);
		} else {
			for (const dx of [0, 64]) {
				let y = 0;
				for (const [r, h] of [[23, 240], [20, 70], [16, 45], [12, 30]]) {
					add(new CylinderGeometry(r, r, h, 8).rotateY(Math.PI / 8), dx, y + h / 2, 0, steel);
					y += h;
				}
				add(new ConeGeometry(6, 40, 8), dx, y + 20, 0, steel);
				add(new CylinderGeometry(1.2, 1.6, 452 - y - 40, 6), dx, y + 40 + (452 - y - 40) / 2, 0, 0xe6ebee);
			}
			add(new BoxGeometry(40, 6, 6), 32, 172, 0, 0x8d98a1);
		}
		group.add(new Mesh(merge(parts), new ToonMaterial({ vertexColors: true, flatShading: true, emissive: 0x000000 })));
		const spot = LANDMARKS[key];
		group.position.set(spot.x, 0, spot.z);
		return group;
	}

	dispose(): void {
		disposeTree(this.scene);
		(this.scene.background as { dispose?: () => void } | null)?.dispose?.();
	}
}
