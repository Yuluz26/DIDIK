// Peti Lanun on the big screen: the leading ships in a bay at sunset, each carrying a heap of gold
// as high as its captain's share of the leader's gold. Ships glide to their new places as the order
// changes, and a raid sends a cannonball arcing from one ship to another.

import {
	Fog,
	Group,
	InstancedMesh,
	Matrix4,
	Mesh,
	MeshLambertMaterial,
	PerspectiveCamera,
	Scene,
	SphereGeometry,
	Vector3
} from 'three';
import { Tags, reducedMotion, type World3D } from '$lib/three/stage';
import { blobShadow, clamp01, damp, disposeTree, hex, light } from '$lib/three/kit';
import { heap, ship, sunset } from './models';

export interface Captain {
	id: string;
	gold: number;
	colour?: string;
}

const SHIPS = 8;
// Places in the bay, best first: the leader in front, the rest fanned out behind.
const SLOTS: [number, number][] = [
	[0, 6],
	[-9, 1],
	[9, 1],
	[-17, -5],
	[17, -5],
	[-5, -10],
	[5, -10],
	[0, -18]
];

interface Berth {
	group: Group;
	sail: MeshLambertMaterial;
	pile: Mesh;
	id: string | null;
	x: number;
	z: number;
	height: number;
	target: number;
}

export class BayWorld implements World3D {
	readonly scene = new Scene();
	readonly camera = new PerspectiveCamera(36, 16 / 9, 0.5, 900);
	readonly tags = new Tags();
	wake?: () => void;

	private readonly berths: Berth[] = [];
	private readonly ball: InstancedMesh;
	private readonly matrix = new Matrix4();
	private readonly still = reducedMotion();
	private shot: { from: Vector3; to: Vector3; t: number } | null = null;
	private time = 0;

	constructor() {
		this.scene.add(sunset(this.scene));
		this.scene.fog = new Fog(0xf0a06a, 90, 330);
		light(this.scene, { sky: 0xffd9b8, ground: 0x2c4a5c, sun: 0xffc48a, strength: 1.05 }).position.set(-30, 25, -60);

		const pile = heap();
		for (let i = 0; i < SHIPS; i++) {
			const sail = new MeshLambertMaterial({ color: 0xffffff, side: 2 });
			const group = ship(sail);
			const gold = new Mesh(pile, new MeshLambertMaterial({ color: 0xffffff, vertexColors: true, flatShading: true }));
			gold.position.set(0, 1.1, 0.9);
			group.add(gold);
			const shadow = blobShadow(4, 7, 0.25);
			shadow.position.y = 0.05;
			group.add(shadow);
			group.rotation.y = Math.PI * 0.08;
			group.visible = false;
			this.scene.add(group);
			this.berths.push({ group, sail, pile: gold, id: null, x: SLOTS[i][0], z: SLOTS[i][1], height: 0.05, target: 0.05 });
		}

		this.ball = new InstancedMesh(new SphereGeometry(0.35, 8, 6), new MeshLambertMaterial({ color: 0x22262a }), 1);
		this.ball.count = 0;
		this.scene.add(this.ball);

		this.camera.position.set(0, 11, 36);
		this.camera.lookAt(0, 2.5, -6);
	}

	/** The leaders, best first. A ship keeps its captain while they stay in the top eight. */
	update(captains: Captain[]): void {
		const top = captains.slice(0, SHIPS);
		const most = Math.max(1, ...top.map((c) => c.gold));
		const free = this.berths.filter((b) => !top.some((c) => c.id === b.id));
		top.forEach((captain, rank) => {
			let berth = this.berths.find((b) => b.id === captain.id);
			if (!berth) {
				berth = free.shift()!;
				berth.id = captain.id;
				[berth.x, berth.z] = SLOTS[rank];
				berth.group.position.set(berth.x, 0, berth.z);
			}
			berth.sail.color.setHex(hex(captain.colour));
			berth.target = 0.05 + 1.9 * (captain.gold / most);
			berth.group.visible = true;
			berth.group.userData.slot = rank;
		});
		for (const berth of free) {
			berth.id = null;
			berth.group.visible = false;
		}
		this.wake?.();
	}

	/** A raid: a cannonball from the raider's ship to the other. */
	fire(from: string, to: string): void {
		const a = this.berths.find((b) => b.id === from);
		const b = this.berths.find((b) => b.id === to);
		if (!a || !b || this.still) return;
		this.shot = { from: a.group.position.clone().setY(3), to: b.group.position.clone().setY(1.5), t: 0 };
		this.wake?.();
	}

	resize(width: number, height: number): void {
		this.camera.aspect = width / height;
		this.camera.position.set(0, 11, this.camera.aspect < 1.3 ? 46 : 36);
		this.camera.lookAt(0, 2.5, -6);
		this.camera.updateProjectionMatrix();
	}

	tick(dt: number): boolean {
		this.time += dt;
		let moving = false;
		const k = this.still ? 60 : 3;
		for (const berth of this.berths) {
			if (!berth.group.visible) continue;
			const [x, z] = SLOTS[berth.group.userData.slot ?? 0];
			berth.x = damp(berth.x, x, k, dt);
			berth.z = damp(berth.z, z, k, dt);
			berth.height = damp(berth.height, berth.target, k, dt);
			if (Math.abs(berth.x - x) + Math.abs(berth.z - z) + Math.abs(berth.height - berth.target) > 0.01) moving = true;
			const bob = this.still ? 0 : Math.sin(this.time * 1.4 + x) * 0.12;
			berth.group.position.set(berth.x, bob, berth.z);
			berth.group.rotation.z = this.still ? 0 : Math.sin(this.time * 1.1 + z) * 0.03;
			berth.pile.scale.set(1, berth.height, 1);
		}
		if (this.shot) {
			this.shot.t += dt / 1.1;
			const t = clamp01(this.shot.t);
			const p = new Vector3().lerpVectors(this.shot.from, this.shot.to, t);
			p.y += Math.sin(t * Math.PI) * 9;
			this.matrix.setPosition(p);
			this.ball.setMatrixAt(0, this.matrix);
			this.ball.count = 1;
			this.ball.instanceMatrix.needsUpdate = true;
			if (t >= 1) {
				this.shot = null;
				this.ball.count = 0;
			}
			moving = true;
		}
		// Ships rock on the swell while the big screen is showing.
		return moving || !this.still;
	}

	afterRender(width: number, height: number): void {
		this.tags.place(this.camera, width, height, (id, out) => {
			const berth = this.berths.find((b) => b.id === id && b.group.visible);
			if (!berth) return false;
			out.set(berth.x, 7.2, berth.z);
			return true;
		});
	}

	dispose(): void {
		disposeTree(this.scene);
		(this.scene.background as { dispose?: () => void } | null)?.dispose?.();
	}
}
