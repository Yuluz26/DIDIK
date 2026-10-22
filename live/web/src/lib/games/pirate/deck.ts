// Peti Lanun on a phone: the player's own deck at sunset with three chests. The chosen chest opens
// first, then the other two, so the player sees what they missed; gold spills out as coins.

import {
	AdditiveBlending,
	BoxGeometry,
	CylinderGeometry,
	DynamicDrawUsage,
	Fog,
	InstancedMesh,
	Matrix4,
	Mesh,
	MeshBasicMaterial,
	MeshLambertMaterial,
	Object3D,
	PerspectiveCamera,
	PlaneGeometry,
	Quaternion,
	Scene,
	Vector3,
	Euler,
	type BufferGeometry
} from 'three';
import { reducedMotion, type World3D } from '$lib/three/stage';
import { blobShadow, clamp01, disposeTree, drawnTexture, ease, light, merge, painted, type Part } from '$lib/three/kit';
import { GOLD, chest, sunset, type Chest } from './models';

export interface Found {
	kind: string;
	amount?: number;
}

const SPOTS = [-1.8, 0, 1.8];
const GLOW: Record<string, number> = { emas: 0xffc94a, besar: 0xffd760, ganda: 0xfff0a0, curi: 0xff7a5c, tukar: 0x7cc4ff, ribut: 0x9fb2c8 };
const COINS = 60;

interface Coin {
	p: Vector3;
	v: Vector3;
	spin: number;
	alive: boolean;
}

export class DeckWorld implements World3D {
	readonly scene = new Scene();
	readonly camera = new PerspectiveCamera(50, 4 / 3, 0.1, 700);
	wake?: () => void;

	private readonly chests: Chest[] = [];
	private readonly glows: Mesh[] = [];
	private readonly coins: InstancedMesh;
	private readonly flying: Coin[] = [];
	private readonly still = reducedMotion();
	private readonly matrix = new Matrix4();
	private readonly quat = new Quaternion();
	private readonly euler = new Euler();
	private readonly one = new Vector3(1, 1, 1);
	private opened: number | null = null;
	private items: Found[] | null = null;
	private picking = false;
	private since = 0; // seconds since the chosen chest opened
	private time = 0;

	constructor() {
		this.scene.add(sunset(this.scene));
		this.scene.fog = new Fog(0xf0a06a, 40, 260);
		light(this.scene, { sky: 0xffd9b8, ground: 0x6b4a3a, sun: 0xffc48a, strength: 1 }).position.set(-20, 18, -40);

		this.scene.add(this.deck());
		SPOTS.forEach((x) => {
			const c = chest();
			c.root.position.set(x, 0.12, 0);
			const shadow = blobShadow(1.5, 1.0, 0.3);
			shadow.position.set(x, 0.13, 0);
			const glow = new Mesh(new PlaneGeometry(1.6, 1.6), new MeshBasicMaterial({ map: glowTexture(), transparent: true, blending: AdditiveBlending, depthWrite: false, opacity: 0 }));
			glow.position.set(x, 1.05, 0.05);
			this.chests.push(c);
			this.glows.push(glow);
			this.scene.add(shadow, c.root, glow);
		});

		this.coins = new InstancedMesh(new CylinderGeometry(0.075, 0.075, 0.025, 10), new MeshLambertMaterial({ color: GOLD }), COINS);
		this.coins.instanceMatrix.setUsage(DynamicDrawUsage);
		this.coins.count = 0;
		this.coins.frustumCulled = false;
		this.scene.add(this.coins);

		this.camera.position.set(0, 2.5, 4.4);
		this.camera.lookAt(0, 0.55, -0.2);
	}

	/** The chests for this answer: still shut (`opened` null) or opened, with what each held. */
	set(opened: number | null, items: Found[] | null, picking: boolean): void {
		this.picking = picking;
		if (opened === null) {
			if (this.opened !== null) this.reset();
		} else if (this.opened !== opened || this.items !== items) {
			const first = this.opened === null;
			this.opened = opened;
			this.items = items;
			if (first) {
				this.since = this.still ? 2 : 0;
				const found = items?.[opened];
				if (found && ['emas', 'besar', 'ganda'].includes(found.kind)) this.spill(SPOTS[opened], found.kind === 'emas' ? 18 : 34);
			}
		}
		this.wake?.();
	}

	private reset(): void {
		this.opened = null;
		this.items = null;
		this.flying.length = 0;
		this.coins.count = 0;
		for (const c of this.chests) c.lid.rotation.x = 0;
		for (const g of this.glows) (g.material as MeshBasicMaterial).opacity = 0;
	}

	private spill(x: number, count: number): void {
		for (let i = 0; i < count && this.flying.length < COINS; i++) {
			const a = Math.random() * Math.PI * 2;
			const speed = 1.2 + Math.random() * 1.6;
			this.flying.push({
				p: new Vector3(x + (Math.random() - 0.5) * 0.4, 0.7, (Math.random() - 0.5) * 0.3),
				v: new Vector3(Math.cos(a) * speed * 0.5, 3.2 + Math.random() * 2, Math.sin(a) * speed * 0.3 + 0.6),
				spin: Math.random() * 10,
				alive: true
			});
		}
	}

	resize(width: number, height: number): void {
		this.camera.aspect = width / height;
		// Three chests side by side need the width: on a tall screen, step back.
		this.camera.position.z = this.camera.aspect < 1.2 ? 5.6 : 4.4;
		this.camera.lookAt(0, 0.55, -0.2);
		this.camera.updateProjectionMatrix();
	}

	tick(dt: number): boolean {
		this.time += dt;
		let moving = false;
		if (this.opened !== null) {
			this.since += dt;
			this.chests.forEach((c, i) => {
				// The chosen chest at once, the other two half a second later.
				const delay = i === this.opened ? 0 : 0.55;
				const t = clamp01((this.since - delay) / 0.5);
				c.lid.rotation.x = -1.95 * ease.outBack(t);
				const found = this.items?.[i];
				const material = this.glows[i].material as MeshBasicMaterial;
				material.color.setHex(GLOW[found?.kind ?? 'emas'] ?? 0xffffff);
				material.opacity = t * (i === this.opened ? 1 : 0.45);
				this.glows[i].scale.setScalar(0.8 + 0.25 * t);
			});
			moving = this.since < 1.2;
		} else {
			this.chests.forEach((c, i) => {
				// Waiting to be chosen: the lids lift a little, one after another.
				const lift = this.picking && !this.still ? Math.max(0, Math.sin(this.time * 3 - i * 0.9)) * 0.08 : 0;
				c.lid.rotation.x = -lift;
			});
			moving = this.picking && !this.still;
		}

		// Coins: thrown up, falling, coming to rest on the deck.
		let live = 0;
		for (const coin of this.flying) {
			if (coin.alive) {
				coin.v.y -= 9.8 * dt;
				coin.p.addScaledVector(coin.v, dt);
				coin.spin += dt * 12;
				if (coin.p.y <= 0.14) {
					coin.p.y = 0.14;
					coin.v.set(0, 0, 0);
					coin.alive = false;
				}
			}
			this.euler.set(coin.alive ? coin.spin : Math.PI / 2 - 0.05, 0, coin.alive ? coin.spin * 0.6 : 0);
			this.quat.setFromEuler(this.euler);
			this.matrix.compose(coin.p, this.quat, this.one);
			this.coins.setMatrixAt(live++, this.matrix);
			if (coin.alive) moving = true;
		}
		this.coins.count = live;
		this.coins.instanceMatrix.needsUpdate = true;
		return moving;
	}

	/** Planks, a rail at the stern, the foot of the mast and a coil of rope. */
	private deck(): Object3D {
		const planks = drawnTexture(256, 256, (ctx) => {
			for (let i = 0; i < 8; i++) {
				ctx.fillStyle = i % 2 ? '#8a5a33' : '#9a6a3f';
				ctx.fillRect(0, i * 32, 256, 32);
				ctx.fillStyle = 'rgba(40,20,8,0.5)';
				ctx.fillRect(0, i * 32, 256, 2);
				ctx.fillRect(((i * 97) % 200) + 20, i * 32, 2, 32);
			}
		});
		const floor = new Mesh(new BoxGeometry(12, 0.24, 9), [
			new MeshLambertMaterial({ color: 0x6e4122 }),
			new MeshLambertMaterial({ color: 0x6e4122 }),
			new MeshLambertMaterial({ map: planks }),
			new MeshLambertMaterial({ color: 0x6e4122 }),
			new MeshLambertMaterial({ color: 0x6e4122 }),
			new MeshLambertMaterial({ color: 0x6e4122 })
		]);
		floor.position.set(0, 0, -1.6);
		const parts: Part[] = [];
		const add = (g: BufferGeometry, x: number, y: number, z: number, color: number) => {
			g.translate(x, y, z);
			parts.push({ geometry: g, color });
		};
		for (let x = -5.6; x <= 5.6; x += 1.4) add(new BoxGeometry(0.16, 0.9, 0.16), x, 0.57, -4.2, 0x6e4122);
		add(new BoxGeometry(11.6, 0.14, 0.24), 0, 1.06, -4.2, 0x5f361a);
		add(new BoxGeometry(11.6, 0.1, 0.18), 0, 0.62, -4.2, 0x5f361a);
		add(new CylinderGeometry(0.26, 0.32, 6, 8), -3.9, 3.1, -2.8, 0x5f361a);
		add(new CylinderGeometry(0.42, 0.42, 0.22, 12), 3.9, 0.23, -2.6, 0xc9a66b);
		add(new CylinderGeometry(0.3, 0.3, 0.24, 12), 3.9, 0.45, -2.6, 0xb8955c);
		const group = new Object3D();
		group.add(floor, new Mesh(merge(parts), painted()));
		return group;
	}

	dispose(): void {
		disposeTree(this.scene);
		(this.scene.background as { dispose?: () => void } | null)?.dispose?.();
	}
}

let glowMap: ReturnType<typeof drawnTexture> | null = null;
function glowTexture() {
	glowMap ??= drawnTexture(64, 64, (ctx) => {
		const g = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
		g.addColorStop(0, 'rgba(255,255,255,1)');
		g.addColorStop(0.35, 'rgba(255,255,255,0.55)');
		g.addColorStop(1, 'rgba(255,255,255,0)');
		ctx.fillStyle = g;
		ctx.fillRect(0, 0, 64, 64);
	});
	return glowMap;
}
