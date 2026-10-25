// Litar Kart in 3D: a small circuit at dusk (a long straight past the grandstand, a hairpin, an S),
// karts in each player's colour, the nitro flame, and two cameras: the big screen's broadcast view
// of the whole circuit and a phone's chase view behind the player's own kart.
//
// Every kart is drawn by three instanced meshes (frame, paint, flame), so 60 karts cost the same
// few draw calls as one.

import {
	BoxGeometry,
	CatmullRomCurve3,
	Color,
	ConeGeometry,
	CylinderGeometry,
	DoubleSide,
	DynamicDrawUsage,
	Float32BufferAttribute,
	BufferGeometry,
	Fog,
	IcosahedronGeometry,
	InstancedMesh,
	Matrix4,
	Mesh,
	MeshBasicMaterial,
	Object3D,
	PerspectiveCamera,
	PlaneGeometry,
	Quaternion,
	RepeatWrapping,
	Scene,
	SphereGeometry,
	Vector3
} from 'three';
import { Tags, reducedMotion, type World3D } from '$lib/three/stage';
import { C, ToonMaterial, blobShadow, clamp01, damp, disposeTree, drawnTexture, ease, hex, light, merge, painted, skyTexture, type Part } from '$lib/three/kit';

export interface Kart {
	id: string;
	m: number;
	colour?: string;
}

export interface CircuitState {
	length: number;
	laps: number;
	karts: Kart[];
	nitro: string[];
}

const TRACK_WIDTH = 9;
const ELEVATION = 0.92; // the host camera's angle above the ground, in radians
const SAMPLES = 800;
const DRIVE_SECONDS = 2.8;
const MAX_KARTS = 100;

interface Racer {
	id: string;
	colour: number;
	from: number;
	to: number;
	shown: number;
	lane: number;
	row: number;
	nitro: boolean;
}

const ONE = new Vector3(1, 1, 1);
const FORWARD = new Vector3(0, 0, 1);

export class CircuitWorld implements World3D {
	readonly scene = new Scene();
	readonly camera = new PerspectiveCamera(45, 16 / 9, 0.5, 900);
	readonly tags = new Tags();
	wake?: () => void;

	private readonly points: Vector3[];
	private readonly tangents: Vector3[];
	private readonly lap: number;
	private readonly racers = new Map<string, Racer>();
	private readonly frame: InstancedMesh;
	private readonly paint: InstancedMesh;
	private readonly flame: InstancedMesh;
	private readonly shadows: InstancedMesh;
	private readonly matrix = new Matrix4();
	private readonly quat = new Quaternion();
	private readonly tmp = new Vector3();
	private readonly side = new Vector3();
	private readonly look = new Vector3();
	private readonly tint = new Color();
	private readonly shot = new Vector3();
	private readonly focus = new Vector3();
	private readonly heading = new Vector3();
	private readonly still = reducedMotion();
	private state: CircuitState = { length: 1, laps: 3, karts: [], nitro: [] };
	private driving = 0; // seconds into the current drive
	private time = 0;
	private camPos = new Vector3();
	private camLook = new Vector3();
	private camReady = false;
	private fit = 180; // the host camera's distance that shows the whole circuit

	constructor(private readonly view: 'host' | 'phone', private readonly me: string | null = null) {
		const curve = new CatmullRomCurve3(
			[
				new Vector3(-62, 0, 26),
				new Vector3(-12, 0, 32),
				new Vector3(38, 0, 30),
				new Vector3(66, 0, 14),
				new Vector3(68, 0, -10),
				new Vector3(48, 0, -26),
				new Vector3(22, 0, -18),
				new Vector3(4, 0, -34),
				new Vector3(-24, 0, -36),
				new Vector3(-50, 0, -22),
				new Vector3(-70, 0, 0)
			],
			true,
			'centripetal'
		);
		this.points = curve.getSpacedPoints(SAMPLES);
		this.tangents = this.points.map((_, i) => curve.getTangentAt(i / SAMPLES));
		this.lap = curve.getLength();

		this.scene.background = skyTexture([
			[0, '#22405f'],
			[0.55, '#5f7fa0'],
			[0.8, '#f0b57a'],
			[1, '#f6c98f']
		]);
		this.scene.fog = new Fog(0xe9b98a, 150, 420);
		const sun = light(this.scene, { sky: 0xb9cdea, ground: 0x46553a, sun: 0xffcf9a, strength: 0.92 });
		sun.position.set(-60, 38, -40);

		this.scene.add(this.ground(), this.track(), this.kerbs(), this.startLine(), this.scenery());

		this.frame = new InstancedMesh(this.kartFrame(), painted(), MAX_KARTS);
		this.paint = new InstancedMesh(this.kartPaint(), painted(), MAX_KARTS);
		this.flame = new InstancedMesh(
			new ConeGeometry(0.45, 2.2, 6).rotateX(-Math.PI / 2).translate(0, 0.75, -2.7),
			new MeshBasicMaterial({ color: 0xffc04a, transparent: true, opacity: 0.9 }),
			MAX_KARTS
		);
		const blob = blobShadow(3.2, 4.4, 0.35);
		this.shadows = new InstancedMesh(blob.geometry, blob.material, MAX_KARTS);
		for (const mesh of [this.frame, this.paint, this.flame, this.shadows]) {
			mesh.instanceMatrix.setUsage(DynamicDrawUsage);
			mesh.count = 0;
			mesh.frustumCulled = false;
			this.scene.add(mesh);
		}

		this.camera.fov = view === 'host' ? 40 : 58;
	}

	// ------------------------------------------------------------------ state from the server

	/** New distances: karts drive from where they are shown now to where the server says. */
	update(state: CircuitState, colours: Map<string, string | undefined>): void {
		this.state = state;
		const seen = new Set<string>();
		let moved = false;
		state.karts.forEach((kart, index) => {
			seen.add(kart.id);
			const racer = this.racers.get(kart.id);
			if (!racer) {
				this.racers.set(kart.id, {
					id: kart.id,
					colour: hex(colours.get(kart.id)),
					from: kart.m,
					to: kart.m,
					shown: kart.m,
					lane: ((index % 4) - 1.5) * 1.9,
					row: Math.floor(index / 4),
					nitro: false
				});
				moved = true;
				return;
			}
			racer.colour = hex(colours.get(kart.id), racer.colour);
			racer.nitro = state.nitro.includes(kart.id);
			if (racer.to !== kart.m) {
				racer.from = racer.shown;
				racer.to = kart.m;
				moved = true;
			}
		});
		for (const id of this.racers.keys()) if (!seen.has(id)) this.racers.delete(id);
		if (moved) this.driving = this.still ? DRIVE_SECONDS : 0;
		this.wake?.();
	}

	/** Lap (1-based, capped at the last) and whether this kart has finished. */
	progress(m: number): { lap: number; finished: boolean } {
		const laps = this.state.laps;
		const run = (Math.min(m, this.state.length) / Math.max(1, this.state.length)) * laps;
		return { lap: Math.min(laps, Math.floor(run) + 1), finished: m >= this.state.length };
	}

	// ------------------------------------------------------------------ frames

	resize(width: number, height: number): void {
		this.camera.aspect = width / height;
		this.camera.updateProjectionMatrix();
		// The circuit is about 150 x 80 on the ground; seen from 52 degrees up, find the distance
		// at which both its width and its (foreshortened) depth fit, with a margin.
		const half = (this.camera.fov * Math.PI) / 360;
		const across = 82 / (Math.tan(half) * this.camera.aspect);
		const deep = (44 * Math.sin(ELEVATION)) / Math.tan(half);
		this.fit = Math.max(across, deep);
		if (this.view === 'host' && this.scene.fog instanceof Fog) {
			this.scene.fog.near = this.fit + 40;
			this.scene.fog.far = this.fit + 420;
		}
	}

	tick(dt: number): boolean {
		this.time += dt;
		const driving = this.driving < DRIVE_SECONDS;
		if (driving) this.driving = Math.min(DRIVE_SECONDS, this.driving + dt);
		const t = ease.inOutCubic(clamp01(this.driving / DRIVE_SECONDS));

		const racers = [...this.racers.values()];
		this.frame.count = this.paint.count = this.shadows.count = racers.length;
		let flames = 0;
		racers.forEach((racer, i) => {
			racer.shown = racer.from + (racer.to - racer.from) * t;
			this.place(racer, i);
			this.paint.setColorAt(i, this.tint.setHex(racer.colour));
			if (racer.nitro && driving) this.flame.setMatrixAt(flames++, this.matrix);
		});
		this.flame.count = flames;
		for (const mesh of [this.frame, this.paint, this.flame, this.shadows]) mesh.instanceMatrix.needsUpdate = true;
		if (this.paint.instanceColor) this.paint.instanceColor.needsUpdate = true;

		const settling = this.aim(dt);
		// The host's camera drifts slowly round the circuit; phones only move when their kart does.
		return driving || settling || (this.view === 'host' && !this.still);
	}

	afterRender(width: number, height: number): void {
		this.tags.place(this.camera, width, height, (id, out) => {
			const racer = this.racers.get(id);
			if (!racer) return false;
			this.where(racer, out);
			out.y += 3.4;
			return true;
		});
	}

	/** Where a kart is drawn: along the circuit by distance, in its own lane. */
	private where(racer: Racer, out: Vector3, heading?: Vector3): Vector3 {
		const finished = racer.shown >= this.state.length;
		const metres = finished ? this.state.length : racer.shown;
		// Server metres map to whole laps of this circuit, so lap 3 ends exactly at the line.
		const run = (metres / Math.max(1, this.state.length)) * this.state.laps;
		const u = ((run % 1) + 1) % 1;
		const at = u * SAMPLES;
		const i = Math.floor(at) % SAMPLES;
		const f = at - Math.floor(at);
		out.lerpVectors(this.points[i], this.points[(i + 1) % SAMPLES], f);
		const tangent = this.tangents[i];
		this.side.set(-tangent.z, 0, tangent.x).normalize();
		out.addScaledVector(this.side, racer.lane);
		// On the grid before the first answer, rows of four behind the line; finished karts park
		// in a row just past it.
		if (racer.shown <= 0.5) out.addScaledVector(tangent, -3 - racer.row * 4.8);
		else if (finished) out.addScaledVector(tangent, 6 + Math.abs(racer.lane) * 2);
		if (heading) heading.copy(tangent);
		return out;
	}

	/** Sets the kart's instances; leaves its matrix in `this.matrix` for the flame. */
	private place(racer: Racer, index: number): void {
		this.where(racer, this.tmp, this.look);
		this.quat.setFromUnitVectors(FORWARD, this.look.setY(0).normalize());
		this.matrix.compose(this.tmp.setY(0.03), this.quat, ONE);
		this.shadows.setMatrixAt(index, this.matrix);
		const bob = this.still ? 0 : Math.sin(this.time * 18 + index) * 0.04;
		this.matrix.compose(this.tmp.setY(bob), this.quat, ONE);
		this.frame.setMatrixAt(index, this.matrix);
		this.paint.setMatrixAt(index, this.matrix);
	}

	/** Moves the camera toward its shot; returns true while it is still travelling. */
	private aim(dt: number): boolean {
		const target = this.shot;
		const focus = this.focus;
		const mine = this.view === 'phone' && this.me ? this.racers.get(this.me) : undefined;
		if (mine) {
			this.where(mine, focus, this.heading);
			target.copy(focus).addScaledVector(this.heading, -9).setY(4.2);
			focus.addScaledVector(this.heading, 7).setY(0.8);
		} else {
			// The whole circuit from the grandstand side, swaying slowly.
			const turn = this.still ? 0.12 : 0.12 + Math.sin(this.time * 0.05) * 0.12;
			const flat = Math.cos(ELEVATION) * this.fit;
			focus.set(0, 0, 0);
			target.set(Math.sin(turn) * flat, Math.sin(ELEVATION) * this.fit, Math.cos(turn) * flat + 6);
		}
		if (!this.camReady) {
			this.camPos.copy(target);
			this.camLook.copy(focus);
			this.camReady = true;
		}
		const k = this.still ? 50 : 4;
		this.camPos.set(damp(this.camPos.x, target.x, k, dt), damp(this.camPos.y, target.y, k, dt), damp(this.camPos.z, target.z, k, dt));
		this.camLook.set(damp(this.camLook.x, focus.x, k, dt), damp(this.camLook.y, focus.y, k, dt), damp(this.camLook.z, focus.z, k, dt));
		this.camera.position.copy(this.camPos);
		this.camera.lookAt(this.camLook);
		return this.camPos.distanceToSquared(target) > 0.01 || this.camLook.distanceToSquared(focus) > 0.01;
	}

	// ------------------------------------------------------------------ the circuit

	/** Mown grass: wide stripes in two greens, the way circuit infields are cut. */
	private ground(): Mesh {
		const stripes = drawnTexture(64, 64, (ctx) => {
			ctx.fillStyle = '#4c8743';
			ctx.fillRect(0, 0, 64, 64);
			ctx.fillStyle = '#57944b';
			ctx.fillRect(0, 0, 64, 32);
		});
		stripes.wrapS = stripes.wrapT = RepeatWrapping;
		stripes.repeat.set(1, 36);
		const mesh = new Mesh(new PlaneGeometry(900, 900), new ToonMaterial({ map: stripes }));
		mesh.rotation.x = -Math.PI / 2;
		mesh.rotation.z = 0.32;
		mesh.position.y = -0.05;
		return mesh;
	}

	/** A ribbon along the sampled curve, `width` wide, `offset` from the centre line. */
	private ribbon(width: number, offset: number, y: number, colour: (i: number) => number): BufferGeometry {
		const positions: number[] = [];
		const colours: number[] = [];
		const c = new Color();
		const edge = (i: number, s: number) => {
			const p = this.points[i % SAMPLES];
			const t = this.tangents[i % SAMPLES];
			const side = new Vector3(-t.z, 0, t.x).normalize();
			return p.clone().addScaledVector(side, offset + s * width * 0.5);
		};
		for (let i = 0; i < SAMPLES; i++) {
			const a = edge(i, -1);
			const b = edge(i, 1);
			const d = edge(i + 1, -1);
			const e = edge(i + 1, 1);
			positions.push(a.x, y, a.z, d.x, y, d.z, b.x, y, b.z, b.x, y, b.z, d.x, y, d.z, e.x, y, e.z);
			c.setHex(colour(i));
			for (let k = 0; k < 6; k++) colours.push(c.r, c.g, c.b);
		}
		const geometry = new BufferGeometry();
		geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
		geometry.setAttribute('color', new Float32BufferAttribute(colours, 3));
		geometry.computeVertexNormals();
		return geometry;
	}

	private track(): Mesh {
		return new Mesh(this.ribbon(TRACK_WIDTH, 0, 0.02, () => 0x4b5359), new ToonMaterial({ vertexColors: true, side: DoubleSide }));
	}

	/** Red and white kerbs where the circuit bends, a white edge line along the rest. */
	private kerbs(): Mesh {
		const bend = (i: number) => 1 - this.tangents[i % SAMPLES].dot(this.tangents[(i + 6) % SAMPLES]);
		const kerb = (i: number) => (bend(i) > 0.004 ? (Math.floor(i / 3) % 2 ? 0xf2efe6 : C.coral) : 0x4f8a45);
		const geometry = mergeRibbons([
			this.ribbon(1.2, -TRACK_WIDTH / 2 - 0.6, 0.06, kerb),
			this.ribbon(1.2, TRACK_WIDTH / 2 + 0.6, 0.06, kerb),
			this.ribbon(0.3, -TRACK_WIDTH / 2 + 0.45, 0.08, () => 0xe9e5da),
			this.ribbon(0.3, TRACK_WIDTH / 2 - 0.45, 0.08, () => 0xe9e5da)
		]);
		return new Mesh(geometry, new ToonMaterial({ vertexColors: true, side: DoubleSide }));
	}

	private startLine(): Object3D {
		const group = new Object3D();
		const checker = drawnTexture(64, 16, (ctx) => {
			for (let x = 0; x < 16; x++)
				for (let y = 0; y < 4; y++) {
					ctx.fillStyle = (x + y) % 2 ? '#1f2d27' : '#f4f1ea';
					ctx.fillRect(x * 4, y * 4, 4, 4);
				}
		});
		const line = new Mesh(new PlaneGeometry(TRACK_WIDTH, 2.2), new MeshBasicMaterial({ map: checker }));
		line.rotation.x = -Math.PI / 2;
		const p = this.points[0];
		const t = this.tangents[0];
		line.position.set(p.x, 0.06, p.z);
		line.rotation.z = Math.atan2(t.x, t.z);
		group.add(line);

		// The gantry over the line, with its five lights.
		const side = new Vector3(-t.z, 0, t.x).normalize();
		const parts: Part[] = [];
		for (const s of [-1, 1]) {
			const post = new BoxGeometry(0.4, 8, 0.4);
			const at = p.clone().addScaledVector(side, s * (TRACK_WIDTH / 2 + 1.6));
			post.translate(at.x, 4, at.z);
			parts.push({ geometry: post, color: 0xb9c1c7 });
		}
		const beam = new BoxGeometry(TRACK_WIDTH + 4, 1.2, 0.6);
		beam.rotateY(Math.atan2(side.x, side.z) + Math.PI / 2);
		beam.translate(p.x, 8.4, p.z);
		parts.push({ geometry: beam, color: 0xe9e4d8 });
		for (let k = -2; k <= 2; k++) {
			const lamp = new SphereGeometry(0.34, 8, 6);
			const at = p.clone().addScaledVector(side, k * 1.3).addScaledVector(t, -0.45);
			lamp.translate(at.x, 8.4, at.z);
			parts.push({ geometry: lamp, color: 0xffd34d });
		}
		group.add(new Mesh(merge(parts), painted()));
		return group;
	}

	/** Grandstand, pit garages, palms, trees, tyre walls and far hills, merged into one mesh. */
	private scenery(): Object3D {
		const group = new Object3D();
		const parts: Part[] = [];
		const box = (w: number, h: number, d: number, x: number, y: number, z: number, color: number, turn = 0) => {
			const g = new BoxGeometry(w, h, d);
			if (turn) g.rotateY(turn);
			g.translate(x, y + h / 2, z);
			parts.push({ geometry: g, color });
		};

		// Grandstand along the main straight, outside the circuit, facing the track.
		for (let step = 0; step < 5; step++) box(64, 1.2, 2.2, -10, step * 1.2, 46 + step * 2.2, step % 2 ? 0x8fa3b3 : 0xa9bac6);
		box(66, 0.4, 6, -10, 9.5, 54, 0xe9e4d8);
		for (const x of [-40, -20, 0, 20]) box(0.5, 9.5, 0.5, x, 0, 56.4, 0x5b6770);

		// Pit garages inside the straight: pale walls, dark doors, a coral band along the roof.
		box(52, 4.2, 7, -12, 0, 18, 0xe9e4d8);
		for (let k = 0; k < 8; k++) box(4.2, 3, 0.2, -35 + k * 6.4, 0, 21.55, 0x2c3a44);
		box(53, 0.4, 7.6, -12, 4.2, 18, 0xcfd3cf);
		box(53, 0.9, 0.5, -12, 3.6, 21.9, C.coral);

		// Oil palms and round trees, kept off the track.
		const rand = mulberry(7);
		const clear = (x: number, z: number) => this.points.every((p) => (p.x - x) ** 2 + (p.z - z) ** 2 > 14 ** 2);
		let placed = 0;
		for (let tries = 0; tries < 900 && placed < 90; tries++) {
			const x = (rand() - 0.5) * 300;
			const z = (rand() - 0.5) * 240;
			if (!clear(x, z) || (z > 38 && z < 64 && x > -46 && x < 26) || (z > 12 && z < 26 && x > -40 && x < 16)) continue;
			placed++;
			const s = 0.8 + rand() * 0.7;
			if (rand() < 0.55) {
				const trunk = new CylinderGeometry(0.35 * s, 0.5 * s, 7 * s, 5);
				trunk.translate(x, 3.5 * s, z);
				parts.push({ geometry: trunk, color: 0x7a5a3a });
				for (let k = 0; k < 6; k++) {
					const frond = new ConeGeometry(0.9 * s, 5.2 * s, 4);
					frond.rotateZ(Math.PI / 2.6);
					frond.rotateY((k / 6) * Math.PI * 2 + rand());
					frond.translate(x, 7 * s, z);
					parts.push({ geometry: frond, color: k % 2 ? 0x3f7a3a : 0x4f9142 });
				}
			} else {
				const crown = new IcosahedronGeometry(2.6 * s, 0);
				crown.translate(x, 4.2 * s, z);
				parts.push({ geometry: crown, color: rand() < 0.5 ? 0x3b7744 : 0x56924a });
				const trunk = new CylinderGeometry(0.3 * s, 0.4 * s, 2.5 * s, 5);
				trunk.translate(x, 1.25 * s, z);
				parts.push({ geometry: trunk, color: 0x6e4c30 });
			}
		}

		// A gravel trap and tyre wall on the outside of the hairpin.
		const gravel = new CylinderGeometry(17, 17, 0.1, 18, 1, false, -1.1, 2.1);
		gravel.translate(63, 0, -4);
		parts.push({ geometry: gravel, color: 0xd8c39a });
		// Tyre walls on the outside of the hairpin.
		for (let k = 0; k < 14; k++) {
			const a = -0.9 + k * 0.13;
			const tyre = new CylinderGeometry(0.75, 0.75, 1.5, 8);
			tyre.translate(Math.cos(a) * 18 + 63, 0.75, Math.sin(a) * 18 - 4);
			parts.push({ geometry: tyre, color: k % 3 ? 0x24282c : C.coral });
		}

		// Far hills, rounded and softened by the fog.
		for (let k = 0; k < 18; k++) {
			const a = (k / 18) * Math.PI * 2;
			const r = 300 + rand() * 80;
			const hill = new SphereGeometry(1, 9, 5, 0, Math.PI * 2, 0, Math.PI / 2);
			hill.scale(70 + rand() * 50, 26 + rand() * 30, 70 + rand() * 50);
			hill.translate(Math.cos(a) * r, -2, Math.sin(a) * r);
			parts.push({ geometry: hill, color: k % 2 ? 0x56785f : 0x678a6c });
		}

		group.add(new Mesh(merge(parts), painted()));

		// The crowd: dots of colour on a slope, one textured plane.
		const crowd = drawnTexture(512, 64, (ctx) => {
			ctx.fillStyle = '#6f8494';
			ctx.fillRect(0, 0, 512, 64);
			const colours = ['#f28c28', '#f5c518', '#3daa5c', '#2f7fcf', '#e2483d', '#ec6ca5', '#14958a', '#fff8ec'];
			const r = mulberry(3);
			for (let i = 0; i < 1400; i++) {
				ctx.fillStyle = colours[Math.floor(r() * colours.length)];
				ctx.fillRect(Math.floor(r() * 128) * 4, Math.floor(r() * 16) * 4, 3, 3);
			}
		});
		const stand = new Mesh(new PlaneGeometry(62, 11), new ToonMaterial({ map: crowd }));
		stand.rotation.x = -Math.PI / 2 + 0.42;
		stand.position.set(-10, 3.4, 50.2);
		group.add(stand);
		return group;
	}

	// ------------------------------------------------------------------ the kart

	/** Everything that stays the same colour: chassis, wheels, bumpers, seat, driver, engine. */
	private kartFrame(): BufferGeometry {
		const parts: Part[] = [];
		const add = (g: BufferGeometry, x: number, y: number, z: number, color: number) => {
			g.translate(x, y, z);
			parts.push({ geometry: g, color });
		};
		add(new BoxGeometry(1.9, 0.18, 3.4), 0, 0.38, 0, 0x24282c);
		for (const [x, z, r, w] of [[-1.15, 1.2, 0.42, 0.38], [1.15, 1.2, 0.42, 0.38], [-1.2, -1.15, 0.48, 0.5], [1.2, -1.15, 0.48, 0.5]]) {
			add(new CylinderGeometry(r, r, w, 12).rotateZ(Math.PI / 2), x, r, z, 0x17191b);
			add(new CylinderGeometry(r * 0.45, r * 0.45, w + 0.04, 8).rotateZ(Math.PI / 2), x, r, z, 0xa0a8ae);
		}
		add(new BoxGeometry(2.2, 0.16, 0.25), 0, 0.42, 2.05, 0x3a4148);
		add(new BoxGeometry(2.4, 0.3, 0.3), 0, 0.55, -1.95, 0x3a4148);
		add(new BoxGeometry(0.8, 0.7, 0.18), 0, 0.95, -0.8, 0x1b1e21);
		add(new BoxGeometry(0.7, 0.62, 0.5), 0, 1.08, -0.42, 0x30363b);
		add(new BoxGeometry(0.86, 0.14, 0.46), 0, 1.16, 0.02, 0x30363b);
		add(new CylinderGeometry(0.2, 0.2, 0.06, 10).rotateX(Math.PI / 2.6), 0, 1.2, 0.32, 0x111315);
		add(new BoxGeometry(0.52, 0.16, 0.1), 0, 1.66, 0.3, 0x1f2d27);
		add(new BoxGeometry(0.7, 0.45, 0.5), 0, 0.75, -1.35, 0x5a6168);
		add(new CylinderGeometry(0.08, 0.08, 0.6, 6).rotateX(Math.PI / 2), 0.38, 0.78, -1.75, 0x9aa3ab);
		for (const x of [-0.8, 0.8]) add(new BoxGeometry(0.08, 0.5, 0.08), x, 1.0, -2.0, 0x3a4148);
		add(new BoxGeometry(0.56, 0.3, 0.04), 0, 0.66, 2.01, 0xf4f1ea);
		return merge(parts);
	}

	/** The player's colour: nose, side pods, rear wing and helmet (white, tinted per kart). */
	private kartPaint(): BufferGeometry {
		const parts: Part[] = [];
		const add = (g: BufferGeometry, x: number, y: number, z: number) => {
			g.translate(x, y, z);
			parts.push({ geometry: g, color: 0xffffff });
		};
		add(new BoxGeometry(1.4, 0.3, 1.05), 0, 0.6, 1.45);
		add(new BoxGeometry(0.9, 0.26, 0.85), 0, 0.82, 0.95);
		add(new BoxGeometry(0.45, 0.38, 1.6), -0.95, 0.6, -0.25);
		add(new BoxGeometry(0.45, 0.38, 1.6), 0.95, 0.6, -0.25);
		add(new BoxGeometry(2.1, 0.08, 0.5), 0, 1.28, -2.0);
		add(new SphereGeometry(0.36, 12, 10), 0, 1.62, 0.02);
		return merge(parts);
	}

	dispose(): void {
		disposeTree(this.scene);
		(this.scene.background as { dispose?: () => void } | null)?.dispose?.();
	}
}

function mergeRibbons(ribbons: BufferGeometry[]): BufferGeometry {
	const positions: number[] = [];
	const colours: number[] = [];
	for (const r of ribbons) {
		positions.push(...(r.getAttribute('position').array as Float32Array));
		colours.push(...(r.getAttribute('color').array as Float32Array));
		r.dispose();
	}
	const geometry = new BufferGeometry();
	geometry.setAttribute('position', new Float32BufferAttribute(positions, 3));
	geometry.setAttribute('color', new Float32BufferAttribute(colours, 3));
	geometry.computeVertexNormals();
	return geometry;
}

/** A small seeded random generator, so the scenery is the same on every screen. */
function mulberry(seed: number): () => number {
	let a = seed;
	return () => {
		a |= 0;
		a = (a + 0x6d2b79f5) | 0;
		let t = Math.imul(a ^ (a >>> 15), 1 | a);
		t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}
