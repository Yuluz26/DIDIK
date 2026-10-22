// Sepakan Penalti in 3D: a floodlit stadium seen from behind the penalty spot, a kicker in the
// shooting team's kit and a keeper in the other's. The server decides where every ball goes and
// where every keeper dives, so the big screen and every phone show the same kick.

import {
	BoxGeometry,
	BufferGeometry,
	CylinderGeometry,
	DoubleSide,
	Float32BufferAttribute,
	Fog,
	Group,
	IcosahedronGeometry,
	Mesh,
	MeshBasicMaterial,
	MeshLambertMaterial,
	PerspectiveCamera,
	PlaneGeometry,
	RepeatWrapping,
	Scene,
	SphereGeometry,
	Vector3,
	type Object3D
} from 'three';
import { reducedMotion, type World3D } from '$lib/three/stage';
import { blobShadow, clamp01, disposeTree, drawnTexture, ease, hex, light, merge, painted, skyTexture, type Part } from '$lib/three/kit';

export interface Kick {
	team: string;
	share: number;
	result: 'gol' | 'selamat' | 'tiang' | 'luar';
	aim: 'kiri' | 'tengah' | 'kanan';
	dive: 'kiri' | 'tengah' | 'kanan';
}

export interface Kit {
	shirt: string;
	keeper: string;
}

const KICK_SECONDS = 3.1;
const CONTACT = 0.9;
const ARRIVE = 1.45;
const GOAL_Z = -11;
const SIDE = { kiri: -1, tengah: 0, kanan: 1 } as const;
const SPOT = new Vector3(0, 0.11, 0);

interface Figure {
	root: Group;
	kit: MeshLambertMaterial;
	leg: Group;
}

export class StadiumWorld implements World3D {
	readonly scene = new Scene();
	readonly camera = new PerspectiveCamera(40, 16 / 9, 0.3, 400);
	wake?: () => void;
	/** Called when a ball reaches the goal (or the keeper, the post, the stand). */
	onresult?: (kick: Kick, index: number) => void;

	private readonly kicker: Figure;
	private readonly keeper: Figure;
	private readonly ball: Mesh;
	private readonly ballShadow: Mesh;
	private readonly net: Group;
	private readonly still = reducedMotion();
	private queue: Kick[] = [];
	private round = 0;
	private clock = 0;
	private told = -1;
	private current = -1;
	private holding = false; // the last kick's end, kept on screen until the next question
	private next = 'harimau';
	private time = 0;
	private readonly from = new Vector3();
	private readonly to = new Vector3();
	private readonly bend = new Vector3();
	private readonly after = new Vector3();

	constructor(
		private readonly view: 'host' | 'phone',
		private kits: Record<string, Kit>
	) {
		this.scene.background = skyTexture([
			[0, '#0b1d2c'],
			[0.6, '#173a4f'],
			[1, '#2a5a63']
		]);
		this.scene.fog = new Fog(0x173a4f, 60, 160);
		light(this.scene, { sky: 0xd6e6ff, ground: 0x24452f, sun: 0xfff6e2, strength: 1.05 }).position.set(10, 40, 30);

		this.scene.add(this.pitch(), this.goal(), this.stands(), this.boards());
		this.net = this.scene.getObjectByName('net') as Group;

		this.kicker = this.figure(false);
		this.keeper = this.figure(true);
		this.keeper.root.position.set(0, 0, GOAL_Z + 0.3);
		this.scene.add(this.kicker.root, this.keeper.root);

		this.ball = new Mesh(this.ballGeometry(), painted());
		this.ball.position.copy(SPOT);
		this.ballShadow = blobShadow(0.45, 0.45, 0.45);
		this.scene.add(this.ball, this.ballShadow);

		// From behind the penalty spot; the big screen sits further back so the goal stays large
		// next to the kicker.
		if (view === 'host') this.camera.position.set(0, 2.7, 13.2);
		else this.camera.position.set(0, 2.3, 9.8);
		this.camera.lookAt(0, 1.3, GOAL_Z);
		this.ready();
	}

	// ------------------------------------------------------------------ state from the server

	/** Between rounds: who takes the next kick. Cuts a round short if the host moved on. */
	idle(nextTeam: string): void {
		this.queue = [];
		this.holding = false;
		this.next = nextTeam;
		this.dress();
		this.ready();
		this.wake?.();
	}

	/** A round's two kicks, played one after the other. */
	play(kicks: Kick[], round: number): void {
		this.queue = kicks;
		this.round = round;
		this.clock = 0;
		this.told = -1;
		this.current = -1;
		this.holding = false;
		this.wake?.();
	}

	// ------------------------------------------------------------------ frames

	resize(width: number, height: number): void {
		this.camera.aspect = width / height;
		// Keep the whole goal in view on a narrow phone.
		this.camera.fov = (this.view === 'host' ? 33 : 50) * (this.camera.aspect < 1.1 ? 1.25 : 1);
		this.camera.updateProjectionMatrix();
	}

	tick(dt: number): boolean {
		this.time += dt;
		if (!this.queue.length) {
			// The keeper waits on the line, shifting from foot to foot (on the big screen only:
			// phones draw nothing between kicks, to save battery).
			if (this.holding || this.still || this.view !== 'host') return false;
			this.keeper.root.position.y = Math.abs(Math.sin(this.time * 3.2)) * 0.08;
			return true;
		}
		this.clock += dt;
		const index = Math.floor(this.clock / KICK_SECONDS);
		if (index >= this.queue.length) {
			this.queue = [];
			this.holding = true;
			return false;
		}
		const kick = this.queue[index];
		if (index !== this.current) {
			this.current = index;
			this.next = kick.team;
			this.dress();
			this.ready();
		}
		this.animate(kick, index, this.clock - index * KICK_SECONDS);
		return true;
	}

	// ------------------------------------------------------------------ one kick

	private animate(kick: Kick, index: number, t: number): void {
		const side = SIDE[kick.aim];
		const dive = SIDE[kick.dive];

		// Run-up from behind and to the right, then the swing of the kicking leg.
		const run = ease.inOutCubic(clamp01(t / 0.78));
		this.kicker.root.position.set(0.95 - 0.6 * run, this.still ? 0 : Math.abs(Math.sin(t * 14)) * 0.06 * (1 - run), 3.4 - 2.85 * run);
		const swing = clamp01((t - 0.72) / 0.28);
		this.kicker.leg.rotation.x = swing < 0.5 ? -1.1 * (swing / 0.5) : -1.1 + 2.4 * ((swing - 0.5) / 0.5);

		// The keeper waits, then goes the way the server chose.
		const k = ease.outCubic(clamp01((t - 0.86) / 0.45));
		this.keeper.root.position.set(dive * 2.1 * k, dive === 0 ? Math.sin(Math.min(k, 1) * Math.PI) * 0.7 : Math.sin(k * Math.PI) * 0.45, GOAL_Z + 0.3);
		this.keeper.root.rotation.z = -dive * 1.25 * k;

		// The ball: still on the spot, then in flight to where it was aimed, then what happens next.
		const height = 0.55 + ((this.round * 7 + index * 3) % 5) * 0.27;
		this.from.copy(SPOT);
		if (kick.result === 'tiang') this.to.set(side * 3.6, 1.25, GOAL_Z);
		else if (kick.result === 'luar') this.to.set(side * 2.2, 3.3, GOAL_Z - 0.5);
		else if (kick.result === 'selamat') this.to.set(dive * 1.75, dive === 0 ? 1.55 : 1.0, GOAL_Z + 0.55);
		else this.to.set(side * 2.55, height, GOAL_Z - 0.4);
		this.bend.set((this.from.x + this.to.x) / 2, Math.max(this.from.y, this.to.y) + 0.6, (this.from.z + this.to.z) / 2);

		if (t < CONTACT) {
			this.ball.position.copy(SPOT);
		} else if (t < ARRIVE) {
			const f = (t - CONTACT) / (ARRIVE - CONTACT);
			bezier(this.from, this.bend, this.to, f, this.ball.position);
			this.ball.rotation.x -= 0.4;
		} else {
			if (this.told < index) {
				this.told = index;
				this.onresult?.(kick, index);
			}
			const f = ease.outCubic(clamp01((t - ARRIVE) / 0.6));
			if (kick.result === 'gol') this.after.set(this.to.x * 1.05, Math.max(0.12, this.to.y - 0.9), GOAL_Z - 1.7);
			else if (kick.result === 'selamat') this.after.set(dive * 3.2 + (dive === 0 ? 1.4 : 0), 0.12, GOAL_Z + 5.5);
			else if (kick.result === 'tiang') this.after.set(side * 6, 0.12, GOAL_Z + 6);
			else this.after.set(side * 3.5, 6.5, GOAL_Z - 16);
			this.ball.position.lerpVectors(this.to, this.after, f);
			// The net bulges where the ball hits it.
			this.net.scale.z = kick.result === 'gol' ? 1 + Math.sin(clamp01((t - ARRIVE) / 0.5) * Math.PI) * 0.35 : 1;
		}
		this.ballShadow.position.set(this.ball.position.x, 0.02, this.ball.position.z);
		this.ballShadow.scale.setScalar(1 / (1 + this.ball.position.y * 0.6));
	}

	/** Everyone back in place for the next kick. */
	private ready(): void {
		this.kicker.root.position.set(0.95, 0, 3.4);
		this.kicker.root.rotation.set(0, Math.PI - 0.25, 0);
		this.kicker.leg.rotation.x = 0;
		this.keeper.root.position.set(0, 0, GOAL_Z + 0.3);
		this.keeper.root.rotation.set(0, 0, 0);
		this.ball.position.copy(SPOT);
		this.ballShadow.position.set(0, 0.02, 0);
		this.ballShadow.scale.setScalar(1);
		this.net.scale.z = 1;
	}

	/** The shooting team's shirt on the kicker, the other team's keeper kit on the keeper. */
	private dress(): void {
		const shooting = this.kits[this.next];
		const defending = this.kits[this.next === 'harimau' ? 'penyu' : 'harimau'];
		if (shooting) this.kicker.kit.color.setHex(hex(shooting.shirt));
		if (defending) this.keeper.kit.color.setHex(hex(defending.keeper));
	}

	// ------------------------------------------------------------------ the stadium

	private pitch(): Object3D {
		const group = new Group();
		// 80 x 60 m around the goal, drawn at 16 px a metre: mown bands and the white lines.
		const W = 80;
		const D = 60;
		const Z0 = -38;
		const px = 16;
		const grass = drawnTexture(W * px, D * px, (ctx) => {
			for (let band = 0; band < D / 5; band++) {
				ctx.fillStyle = band % 2 ? '#2f8a4e' : '#36975a';
				ctx.fillRect(0, band * 5 * px, W * px, 5 * px);
			}
			const u = (x: number) => (x + W / 2) * px;
			const v = (z: number) => (z - Z0) * px;
			ctx.strokeStyle = 'rgba(255,255,255,0.92)';
			ctx.lineWidth = 0.14 * px;
			ctx.strokeRect(u(-20.16), v(GOAL_Z), 40.32 * px, 16.5 * px);
			ctx.strokeRect(u(-9.16), v(GOAL_Z), 18.32 * px, 5.5 * px);
			ctx.beginPath();
			ctx.moveTo(0, v(GOAL_Z));
			ctx.lineTo(W * px, v(GOAL_Z));
			ctx.stroke();
			ctx.beginPath();
			ctx.arc(u(0), v(0), 9.15 * px, 0.93, Math.PI - 0.93);
			ctx.stroke();
			ctx.fillStyle = '#fff';
			ctx.beginPath();
			ctx.arc(u(0), v(0), 0.16 * px, 0, Math.PI * 2);
			ctx.fill();
		});
		const field = new Mesh(new PlaneGeometry(W, D), new MeshLambertMaterial({ map: grass }));
		field.rotation.x = -Math.PI / 2;
		field.position.set(0, 0, Z0 + D / 2);
		const outer = new Mesh(new PlaneGeometry(400, 400), new MeshLambertMaterial({ color: 0x1f5f3a }));
		outer.rotation.x = -Math.PI / 2;
		outer.position.y = -0.02;
		group.add(outer, field);
		return group;
	}

	private goal(): Object3D {
		const group = new Group();
		const parts: Part[] = [];
		const white = 0xf4f4ef;
		for (const x of [-3.66, 3.66]) {
			const post = new CylinderGeometry(0.06, 0.06, 2.44, 10);
			post.translate(x, 1.22, GOAL_Z);
			parts.push({ geometry: post, color: white });
			const stay = new CylinderGeometry(0.035, 0.035, 2.9, 6);
			stay.rotateX(-0.68);
			stay.translate(x, 1.2, GOAL_Z - 0.9);
			parts.push({ geometry: stay, color: 0xb9c1c7 });
		}
		const bar = new CylinderGeometry(0.06, 0.06, 7.44, 10);
		bar.rotateZ(Math.PI / 2);
		bar.translate(0, 2.44, GOAL_Z);
		parts.push({ geometry: bar, color: white });
		group.add(new Mesh(merge(parts), painted()));

		// The net: a mesh texture on the back, top and sides, a little see-through.
		const mesh = drawnTexture(64, 64, (ctx) => {
			ctx.strokeStyle = 'rgba(240,244,240,0.85)';
			ctx.lineWidth = 3;
			ctx.strokeRect(0, 0, 64, 64);
		});
		mesh.wrapS = mesh.wrapT = RepeatWrapping;
		const material = (w: number, h: number) => {
			const map = mesh.clone();
			map.repeat.set(w * 5, h * 5);
			map.needsUpdate = true;
			return new MeshBasicMaterial({ map, transparent: true, side: DoubleSide, depthWrite: false });
		};
		const net = new Group();
		net.name = 'net';
		net.position.z = GOAL_Z;
		const back = new Mesh(new PlaneGeometry(7.32, 2.44), material(7.32, 2.44));
		back.position.set(0, 1.22, -1.9);
		const top = new Mesh(new PlaneGeometry(7.32, 1.9), material(7.32, 1.9));
		top.rotation.x = Math.PI / 2;
		top.position.set(0, 2.44, -0.95);
		net.add(back, top);
		for (const x of [-3.66, 3.66]) {
			const side = new Mesh(new PlaneGeometry(1.9, 2.44), material(1.9, 2.44));
			side.rotation.y = Math.PI / 2;
			side.position.set(x, 1.22, -0.95);
			net.add(side);
		}
		group.add(net);
		return group;
	}

	/** Stands round the pitch with a crowd in both teams' colours, and four floodlight towers. */
	private stands(): Object3D {
		const group = new Group();
		// The crowd: fine dots in both teams' colours on dark rows, quieter toward the back.
		const crowd = drawnTexture(1024, 256, (ctx) => {
			ctx.fillStyle = '#122129';
			ctx.fillRect(0, 0, 1024, 256);
			for (let row = 0; row < 256; row += 8) {
				ctx.fillStyle = 'rgba(255,255,255,0.03)';
				ctx.fillRect(0, row, 1024, 1);
			}
			const colours = ['#f28c28', '#14958a', '#f4efe6', '#ffb627', '#d0452f'];
			let seed = 11;
			const rand = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
			for (let i = 0; i < 9000; i++) {
				const y = Math.floor(rand() * 128) * 2;
				ctx.fillStyle = colours[Math.floor(rand() * colours.length)];
				ctx.globalAlpha = (0.25 + rand() * 0.4) * (0.55 + (y / 256) * 0.45);
				ctx.fillRect(Math.floor(rand() * 512) * 2, y, 2, 2);
			}
			ctx.globalAlpha = 1;
		});
		const stand = (width: number, x: number, z: number, turn: number) => {
			const block = new Group();
			const rows = new Mesh(new PlaneGeometry(width, 16), new MeshLambertMaterial({ map: crowd }));
			rows.rotation.x = -0.62;
			rows.position.set(0, 6.5, 0);
			const roof = new Mesh(new BoxGeometry(width + 2, 0.6, 8), new MeshLambertMaterial({ color: 0x24394a }));
			roof.position.set(0, 15.5, -4);
			const wall = new Mesh(new BoxGeometry(width, 1.4, 0.4), new MeshLambertMaterial({ color: 0x2a4152 }));
			wall.position.set(0, 0.7, 6.3);
			block.add(rows, roof, wall);
			block.position.set(x, 0, z);
			block.rotation.y = turn;
			group.add(block);
		};
		stand(84, 0, GOAL_Z - 26, 0);
		stand(70, -46, -6, Math.PI / 2);
		stand(70, 46, -6, -Math.PI / 2);

		const parts: Part[] = [];
		for (const [x, z] of [[-40, GOAL_Z - 24], [40, GOAL_Z - 24], [-44, 26], [44, 26]]) {
			const mast = new CylinderGeometry(0.35, 0.6, 30, 6);
			mast.translate(x, 15, z);
			parts.push({ geometry: mast, color: 0x55646f });
			const frame = new BoxGeometry(6, 3.4, 0.6);
			frame.lookAt(new Vector3(-x, -10, -z));
			frame.translate(x, 31, z);
			parts.push({ geometry: frame, color: 0x3a4652 });
		}
		group.add(new Mesh(merge(parts), painted()));
		for (const [x, z] of [[-40, GOAL_Z - 24], [40, GOAL_Z - 24], [-44, 26], [44, 26]]) {
			const lamp = new Mesh(new PlaneGeometry(5.4, 2.8), new MeshBasicMaterial({ color: 0xfff6d8 }));
			lamp.position.set(x, 31, z);
			lamp.lookAt(0, 0, -4);
			lamp.translateZ(0.35);
			group.add(lamp);
		}
		return group;
	}

	/** Advertising boards behind the goal line, in the app's colours. */
	private boards(): Object3D {
		// Ten panels of 6.4 x 0.9 m. The texture is drawn ten times taller than the board's shape
		// (sharp letters), so the words are squeezed sideways by the same factor.
		const words = ['DIDIK', 'MAIN BERSAMA', 'KUIZ', 'PENALTI'];
		const fills = ['#d0452f', '#12847a', '#1f2d27', '#2d78c4', '#ffb627'];
		const texture = drawnTexture(2560, 360, (ctx) => {
			for (let i = 0; i < 10; i++) {
				ctx.fillStyle = fills[i % fills.length];
				ctx.fillRect(i * 256, 0, 256, 360);
			}
			ctx.textAlign = 'center';
			ctx.textBaseline = 'middle';
			ctx.font = '700 112px sans-serif';
			for (let i = 0; i < 10; i++) {
				ctx.save();
				ctx.translate(i * 256 + 128, 185);
				ctx.scale(0.1, 1);
				ctx.fillStyle = i % 5 === 4 ? '#1f2d27' : '#ffffff';
				ctx.fillText(words[i % words.length], 0, 0);
				ctx.restore();
			}
		});
		const board = new Mesh(new PlaneGeometry(64, 0.9), new MeshBasicMaterial({ map: texture }));
		board.position.set(0, 0.45, GOAL_Z - 5);
		return board;
	}

	// ------------------------------------------------------------------ people and the ball

	private figure(keeper: boolean): Figure {
		const root = new Group();
		const fixed: Part[] = [];
		const add = (g: BufferGeometry, x: number, y: number, z: number, color: number, list: Part[] = fixed) => {
			g.translate(x, y, z);
			list.push({ geometry: g, color });
		};
		const skin = 0xc8946a;
		add(new BoxGeometry(0.44, 0.26, 0.27), 0, 0.97, 0, 0x1d2b3a);
		add(new SphereGeometry(0.15, 10, 8), 0, 1.76, 0, skin);
		add(new SphereGeometry(0.155, 10, 6, 0, Math.PI * 2, 0, Math.PI / 2), 0, 1.79, -0.01, 0x241b14);
		add(new BoxGeometry(0.14, 0.12, 0.28), -0.12, 0.06, 0.03, 0x1a1a1a);
		add(new BoxGeometry(0.15, 0.42, 0.17), -0.12, 0.33, 0, 0xf2f2ea);
		add(new BoxGeometry(0.15, 0.32, 0.17), -0.12, 0.7, 0, skin);
		const kitParts: Part[] = [];
		add(new BoxGeometry(0.48, 0.56, 0.28), 0, 1.36, 0, 0xffffff, kitParts);
		if (keeper) {
			add(new BoxGeometry(0.13, 0.6, 0.14).rotateZ(2.5), -0.42, 1.62, 0.04, 0xffffff, kitParts);
			add(new BoxGeometry(0.13, 0.6, 0.14).rotateZ(-2.5), 0.42, 1.62, 0.04, 0xffffff, kitParts);
			add(new BoxGeometry(0.17, 0.17, 0.17), -0.6, 1.88, 0.05, 0xffb627);
			add(new BoxGeometry(0.17, 0.17, 0.17), 0.6, 1.88, 0.05, 0xffb627);
		} else {
			add(new BoxGeometry(0.13, 0.56, 0.14), -0.32, 1.32, 0, 0xffffff, kitParts);
			add(new BoxGeometry(0.13, 0.56, 0.14), 0.32, 1.32, 0, 0xffffff, kitParts);
		}
		const kit = new MeshLambertMaterial({ vertexColors: true, flatShading: true });
		root.add(new Mesh(merge(fixed), painted()), new Mesh(merge(kitParts), kit));

		// The right leg turns at the hip, for the kick.
		const leg = new Group();
		leg.position.set(0.12, 0.86, 0);
		const legParts: Part[] = [];
		add(new BoxGeometry(0.15, 0.32, 0.17), 0, -0.16, 0, skin, legParts);
		add(new BoxGeometry(0.15, 0.42, 0.17), 0, -0.53, 0, 0xf2f2ea, legParts);
		add(new BoxGeometry(0.14, 0.12, 0.28), 0, -0.8, 0.03, 0x1a1a1a, legParts);
		leg.add(new Mesh(merge(legParts), painted()));
		root.add(leg);

		const shadow = blobShadow(0.9, 0.6, 0.38);
		shadow.position.y = 0.015;
		root.add(shadow);
		return { root, kit, leg };
	}

	private ballGeometry(): BufferGeometry {
		const geometry = new IcosahedronGeometry(0.11, 1);
		const count = geometry.getAttribute('position').count;
		const colours: number[] = [];
		for (let face = 0; face < count / 3; face++) {
			const dark = face % 5 === 0;
			for (let k = 0; k < 3; k++) colours.push(dark ? 0.04 : 0.92, dark ? 0.05 : 0.92, dark ? 0.06 : 0.9);
		}
		geometry.setAttribute('color', new Float32BufferAttribute(colours, 3));
		geometry.computeVertexNormals();
		return geometry;
	}

	dispose(): void {
		disposeTree(this.scene);
		(this.scene.background as { dispose?: () => void } | null)?.dispose?.();
	}
}

function bezier(a: Vector3, b: Vector3, c: Vector3, t: number, out: Vector3): Vector3 {
	const u = 1 - t;
	return out.set(u * u * a.x + 2 * u * t * b.x + t * t * c.x, u * u * a.y + 2 * u * t * b.y + t * t * c.y, u * u * a.z + 2 * u * t * b.z + t * t * c.z);
}
