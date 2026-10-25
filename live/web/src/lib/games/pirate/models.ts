// Peti Lanun's low-poly pieces, shared by the phone's deck and the big screen's bay: a treasure chest
// with a lid that opens, a ship with a sail in its captain's colour, and the sunset sea.

import {
	AdditiveBlending,
	BoxGeometry,
	ConeGeometry,
	CylinderGeometry,
	Group,
	Mesh,
	MeshBasicMaterial,
	PlaneGeometry,
	Scene,
	SphereGeometry,
	type BufferGeometry
} from 'three';
import { ToonMaterial, drawnTexture, merge, painted, skyTexture, type Part } from '$lib/three/kit';

export const GOLD = 0xffb627;
const WOOD = 0x8a5229;
const WOOD_DARK = 0x5f361a;

export interface Chest {
	root: Group;
	lid: Group;
}

/** A chest 1.2 m wide, sitting on y = 0, its lid hinged at the back. */
export function chest(): Chest {
	const root = new Group();
	const body: Part[] = [];
	const add = (g: BufferGeometry, x: number, y: number, z: number, color: number, list = body) => {
		g.translate(x, y, z);
		list.push({ geometry: g, color });
	};
	add(new BoxGeometry(1.2, 0.62, 0.78), 0, 0.31, 0, WOOD);
	for (const x of [-0.42, 0.42]) add(new BoxGeometry(0.1, 0.64, 0.8), x, 0.32, 0, GOLD);
	add(new BoxGeometry(1.22, 0.08, 0.8), 0, 0.04, 0, WOOD_DARK);
	add(new BoxGeometry(0.2, 0.24, 0.06), 0, 0.5, 0.41, GOLD);
	add(new BoxGeometry(0.08, 0.1, 0.02), 0, 0.47, 0.445, WOOD_DARK);
	root.add(new Mesh(merge(body), painted()));

	const lid = new Group();
	lid.position.set(0, 0.62, -0.39);
	const top: Part[] = [];
	const curve = new CylinderGeometry(0.39, 0.39, 1.2, 10, 1, false, 0, Math.PI);
	curve.rotateZ(Math.PI / 2);
	curve.rotateX(Math.PI / 2);
	add(curve, 0, 0, 0.39, WOOD, top);
	for (const x of [-0.42, 0.42]) {
		const band = new CylinderGeometry(0.405, 0.405, 0.1, 10, 1, false, 0, Math.PI);
		band.rotateZ(Math.PI / 2);
		band.rotateX(Math.PI / 2);
		add(band, x, 0, 0.39, GOLD, top);
	}
	lid.add(new Mesh(merge(top), painted()));
	root.add(lid);
	return { root, lid };
}

/** A small ship, bow toward +z, about 6 m long; the sail and pennant take `colour`. */
export function ship(colour: ToonMaterial): Group {
	const root = new Group();
	const parts: Part[] = [];
	const add = (g: BufferGeometry, x: number, y: number, z: number, color: number) => {
		g.translate(x, y, z);
		parts.push({ geometry: g, color });
	};
	add(new BoxGeometry(2.2, 1.0, 4.4), 0, 0.5, 0, WOOD);
	add(new BoxGeometry(2.3, 0.18, 4.5), 0, 1.05, 0, WOOD_DARK);
	const bow = new ConeGeometry(1.12, 1.8, 4, 1);
	bow.rotateY(Math.PI / 4);
	bow.scale(1, 1, 0.55);
	bow.rotateX(Math.PI / 2);
	add(bow, 0, 0.62, 3.0, WOOD);
	add(new BoxGeometry(2.2, 0.9, 1.1), 0, 1.4, -1.7, WOOD);
	add(new CylinderGeometry(0.09, 0.12, 5.2, 6), 0, 3.5, 0.2, WOOD_DARK);
	add(new BoxGeometry(2.6, 0.1, 0.1), 0, 4.9, 0.2, WOOD_DARK);
	root.add(new Mesh(merge(parts), painted()));

	// The sail, bellied forward, and a pennant at the top of the mast.
	const sail = new PlaneGeometry(2.4, 2.6, 4, 2);
	const position = sail.getAttribute('position');
	for (let i = 0; i < position.count; i++) {
		const x = position.getX(i);
		position.setZ(i, 0.45 * Math.cos((x / 2.4) * Math.PI));
	}
	sail.computeVertexNormals();
	const cloth = new Mesh(sail, new ToonMaterial({ color: 0xf3e9d2, side: 2 }));
	cloth.position.set(0, 3.55, 0.32);
	const pennant = new Mesh(new ConeGeometry(0.3, 1.2, 3).rotateZ(-Math.PI / 2), colour);
	pennant.position.set(0.6, 6.0, 0.2);
	const stripe = new Mesh(new PlaneGeometry(2.42, 0.5), colour);
	stripe.position.set(0, 3.0, 0.78);
	root.add(cloth, pennant, stripe);
	return root;
}

/** A gold heap; scale y with the amount. */
export function heap(): BufferGeometry {
	const parts: Part[] = [];
	const pile = new ConeGeometry(0.75, 1, 7);
	pile.translate(0, 0.5, 0);
	parts.push({ geometry: pile, color: GOLD });
	const top = new SphereGeometry(0.22, 6, 4);
	top.translate(0.1, 0.92, 0.05);
	parts.push({ geometry: top, color: 0xffd34d });
	return merge(parts);
}

/** Sunset sky, a calm sea, and a path of light on the water toward the sun at the horizon. */
export function sunset(scene: Scene): Group {
	scene.background = skyTexture([
		[0, '#203a5a'],
		[0.45, '#7c5f7d'],
		[0.75, '#f0965a'],
		[1, '#ffc46e']
	]);
	const group = new Group();
	const sea = new Mesh(new PlaneGeometry(900, 900), new ToonMaterial({ color: 0x1f5577 }));
	sea.rotation.x = -Math.PI / 2;
	const shine = drawnTexture(64, 256, (ctx) => {
		const across = ctx.createLinearGradient(0, 0, 64, 0);
		across.addColorStop(0, 'rgba(255,200,130,0)');
		across.addColorStop(0.5, 'rgba(255,214,150,0.9)');
		across.addColorStop(1, 'rgba(255,200,130,0)');
		ctx.fillStyle = across;
		ctx.fillRect(0, 0, 64, 256);
		// Broken into short glints, and more broken the nearer the viewer.
		ctx.globalCompositeOperation = 'destination-out';
		let seed = 7;
		const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
		ctx.fillStyle = '#000';
		for (let y = 0; y < 256; y += 2) {
			const broken = 0.3 + 0.5 * (y / 256);
			for (let x = 0; x < 64; ) {
				const run = 2 + Math.floor(rand() * 7);
				if (rand() < broken) ctx.fillRect(x, y, run, 2);
				x += run;
			}
		}
	});
	const path = new Mesh(new PlaneGeometry(70, 380), new MeshBasicMaterial({ map: shine, transparent: true, blending: AdditiveBlending, depthWrite: false }));
	path.rotation.x = -Math.PI / 2;
	path.position.set(0, 0.04, -200);
	group.add(sea, path);
	return group;
}
