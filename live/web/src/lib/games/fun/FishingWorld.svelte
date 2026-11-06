<!--
	A child's Pancing Ikan, as one pixel scene: the lake with fish swimming under the surface, the far
	bank mirrored in the water, and the child at the end of a wooden jetty holding a rod, the line
	running from its tip to a float. A right answer is bait. Tapping the lake (or the button) casts:
	the rod swings back and over, the float flies to where the lake was tapped and lands with a splash,
	a fish comes to nibble, the float is pulled under, and what bit leaps out of the water into the
	bucket on the jetty. Then a card shows what it was.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { confetti } from '$lib/confetti';
	import { play } from '$lib/sound';
	import { CW, HANDS, holdingSheet } from '$lib/pixel/chibi';
	import Scene from '$lib/pixel/Scene.svelte';
	import { type G, cell, dot, ease, hash, hex, line, put, ring, sagLine, stillWanted, underwater } from '$lib/pixel/scene';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Icon from '$ui/Icon.svelte';
	import { fish } from './art';
	import { LAKE, WATER_DEEP, alert, bobber, bucket, lakeBack, lakeFront } from './lake';
	import { bird, cloud } from './scenery';

	interface Fish {
		name: string;
		value: number;
	}
	interface Catch {
		fish: string;
		value: number;
		gold: boolean;
	}
	let {
		client,
		world,
		me
	}: { client: RoomClient; world: { fish: Record<string, Fish>; bait: number; gold: number; net: string[]; caught: number; best: string | null }; me: Person } = $props();

	const { w: W, h: H, deck: DECK, angler: AX, shore: SHORE } = LAKE;
	const AY = DECK - 30; // the top of the child's cell: their shoes stand on the planks
	const HAND: [number, number] = [AX + CW - 1 - HANDS.x, AY + HANDS.y];
	const ROD = 36;
	const BUCKET: [number, number] = [26, DECK - 11];

	// a cast, in milliseconds from the tap
	const LET_GO = 250;
	const LAND = 770;
	const NIBBLES = [LAND + 650, LAND + 980];
	const STRIKE = LAND + 1500;
	const LEAP = LAND + 1850;
	const IN = LAND + 2500;
	const DONE = LAND + 2700;
	const GIVE_UP = LAND + 3600;

	interface Cast {
		key: number;
		t0: number;
		to: [number, number];
		gold: boolean;
		got: Catch | null;
		/** How many were caught before this cast. */
		before: number;
	}
	let cast = $state<Cast | null>(null);
	let rest = $state<[number, number] | null>(null);
	let card = $state<(Catch & { key: number }) | null>(null);
	const still = stillWanted();
	let n = 0;
	const timers = new Set<ReturnType<typeof setTimeout>>();
	const later = (ms: number, fn: () => void) => {
		const id = setTimeout(() => (timers.delete(id), fn()), ms);
		timers.add(id);
	};
	$effect(() => () => timers.forEach(clearTimeout));

	const busy = $derived(!!cast);
	// While a catch is still on its way up, the bucket and the count do not give it away.
	const hiding = $derived(cast && !card ? Math.max(0, world.caught - cast.before) : 0);
	const net = $derived(hiding ? world.net.slice(0, Math.max(0, world.net.length - hiding)) : world.net);
	const caught = $derived(world.caught - hiding);

	const clampTarget = (x: number, y: number): [number, number] => [Math.max(LAKE.end + 10, Math.min(W - 16, Math.round(x))), Math.max(SHORE + 12, Math.min(H - 14, Math.round(y)))];

	function throwLine(gold: boolean, to?: [number, number]) {
		if (busy || (gold ? world.gold < 1 : world.bait < 1)) return;
		const key = ++n;
		const target = to ? clampTarget(...to) : clampTarget(100 + Math.random() * 50, SHORE + 20 + Math.random() * 36);
		cast = { key, t0: performance.now(), to: target, gold, got: null, before: world.caught };
		rest = null;
		play('whoosh');
		client.send({ t: 'cast', gold });
		if (!still) later(LAND, () => cast?.key === key && play('splash'));
		// nothing came back: reel the empty line in
		later(still ? 1500 : GIVE_UP + 600, () => cast?.key === key && !cast.got && (cast = null));
	}

	function tapLake(e: MouseEvent) {
		const box = (e.currentTarget as HTMLElement).getBoundingClientRect();
		const at: [number, number] | undefined = e.detail ? [((e.clientX - box.left) / box.width) * W, ((e.clientY - box.top) / box.height) * H] : undefined;
		throwLine(false, at);
	}

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind !== 'catch' || !cast || cast.got) return;
			const c = cast;
			c.got = { fish: fx.fish, value: fx.value, gold: fx.gold };
			cast = { ...c };
			const reveal = still ? 0 : Math.max(0, c.t0 + IN - performance.now());
			later(reveal, () => {
				card = { ...c.got!, key: c.key };
				play(fx.value ? 'coin' : 'almost');
				if (fx.fish === 'arowana' || fx.fish === 'kelah') confetti({ count: 60 });
			});
			later(still ? 0 : Math.max(0, c.t0 + DONE - performance.now()), () => {
				if (cast?.key !== c.key) return;
				rest = still ? c.to : null;
				cast = null;
			});
			later(reveal + 2400, () => card?.key === c.key && (card = null));
		})
	);

	// ------------------------------------------------------------------ the picture

	const SWIMMERS = ['bilis', 'puyu', 'keli', 'patin', 'kelah', 'bilis', 'puyu', 'bilis'];
	const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
	const span = (ms: number, from: number, to: number) => ease((ms - from) / (to - from));
	const LINE = hex('#f2f6f2', 210);
	const FOAM = hex('#ffffff', 230);

	/** The rod's angle (degrees above the water, pointing out over the lake) and how far its tip bends. */
	function rodAt(ms: number | null, got: Catch | null): { a: number; bend: number } {
		if (ms === null) return { a: 52, bend: 0 };
		if (ms < 170) return { a: lerp(52, 105, span(ms, 0, 170)), bend: 0 };
		if (ms < 320) return { a: lerp(105, 22, span(ms, 170, 320)), bend: -2 };
		if (ms < LAND) return { a: lerp(22, 38, span(ms, 320, LAND)), bend: 0 };
		if (!got) {
			if (ms < GIVE_UP) return { a: 38, bend: 0 };
			return { a: lerp(38, 52, span(ms, GIVE_UP, GIVE_UP + 500)), bend: 0 };
		}
		if (ms < STRIKE) return { a: 38, bend: 0 };
		if (ms < LEAP) return { a: lerp(38, 64, span(ms, STRIKE, STRIKE + 160)), bend: 9 + ((ms / 90) | 0) % 2 };
		if (ms < IN) return { a: lerp(64, 76, span(ms, LEAP, IN)), bend: lerp(9, 2, span(ms, LEAP, IN)) };
		return { a: lerp(76, 52, span(ms, IN, DONE)), bend: 0 };
	}

	function tipOf(a: number, bend: number): [number, number] {
		const r = (a * Math.PI) / 180;
		return [HAND[0] + Math.cos(r) * ROD, HAND[1] - Math.sin(r) * ROD + bend];
	}

	function drawRod(g: G, a: number, bend: number) {
		const r = (a * Math.PI) / 180;
		const ux = Math.cos(r);
		const uy = -Math.sin(r);
		const at = (s: number): [number, number] => [HAND[0] + ux * s, HAND[1] + uy * s + bend * Math.max(0, s / ROD) ** 2];
		// the cork grip behind the hands, and the reel under the rod just in front of them
		const butt = at(-7);
		line(g, butt[0], butt[1], HAND[0], HAND[1], hex('#c08a52'));
		line(g, butt[0], butt[1] + 1, HAND[0], HAND[1] + 1, hex('#8a5a32'));
		const reel = at(2);
		g.fillStyle = '#3a3a46';
		g.fillRect(Math.round(reel[0]) - 1, Math.round(reel[1]) + 1, 3, 3);
		dot(g, reel[0], reel[1] + 2, hex('#aeb2c4'));
		// the blank: thick and dark near the hands, thin towards the tip, the tip itself red
		let prev = at(0);
		for (let s = 3; s <= ROD; s += 3) {
			const p = at(s);
			const c = s > ROD - 4 ? hex('#e2483d') : s < 15 ? hex('#3b2a2c') : hex('#5a3b30');
			line(g, prev[0], prev[1], p[0], p[1], c);
			if (s < 15) line(g, prev[0], prev[1] + 1, p[0], p[1] + 1, hex('#6a4331'));
			prev = p;
		}
		// two little rings the line runs through
		for (const s of [13, 25]) {
			const p = at(s);
			dot(g, p[0], p[1] + 1, hex('#c6c9d6'));
		}
	}

	function drawFloat(g: G, x: number, y: number, gold: boolean, sunk: number) {
		// `sunk` rows of the float are under the surface; a pale line rings it where it meets the water
		const pix = bobber(gold);
		const visible = Math.max(0, pix.h - sunk);
		if (visible > 0) {
			g.save();
			g.beginPath();
			g.rect(Math.round(x) - 1, Math.round(y) - 1, 5, visible + 1);
			g.clip();
			put(g, pix, x - 1, y);
			g.restore();
		}
		if (sunk) {
			const wy = Math.round(y) + visible;
			dot(g, x - 2, wy, FOAM);
			dot(g, x + 2, wy, FOAM);
		}
	}

	function paint(g: G, t: number) {
		const now = still ? 0 : t;
		put(g, lakeBack(), 0, 0);

		// a cloud drifting over, and two birds
		const cx = ((now * 0.003) % (W + 60)) - 40;
		put(g, cloud(1), cx, 3);
		for (let i = 0; i < 2; i++) {
			const bx = ((now * 0.008 + i * 37 + 60) % (W + 20)) - 10;
			put(g, bird(((now / 260 + i) | 0) % 2), bx, 16 + i * 5);
		}

		// light glinting on the water, drifting slowly and coming and going
		for (let i = 0; i < 26; i++) {
			const y = SHORE + 4 + Math.round(hash(i, 1) * (H - SHORE - 8));
			const len = 2 + Math.round(hash(i, 2) * 3) + (y > 80 ? 1 : 0);
			const x = Math.round((hash(i, 3) * (W + 20) + now * 0.002 * (1 + hash(i, 4))) % (W + 20)) - 10;
			if ((((now / 700) | 0) + i) % 4 === 0) continue;
			g.fillStyle = `rgba(216,246,242,${y < 60 ? 0.55 : 0.75})`;
			g.fillRect(x, y, len, 1);
		}

		// fish below the surface, each back and forth across the lake at its own depth and pace
		SWIMMERS.forEach((kind, i) => {
			const pix = fish(kind, true).pix;
			const depth = SHORE + 16 + Math.round(hash(i, 5) * (H - SHORE - 30));
			const speed = 5 + hash(i, 6) * 7;
			const run = W + pix.w + 30;
			const pos = (now * 0.001 * speed + hash(i, 7) * run * 2) % (run * 2);
			const right = pos < run;
			const x = right ? pos - pix.w - 15 : W + 15 - (pos - run);
			const y = depth + (((now / 600 + i) | 0) % 2);
			put(g, underwater(pix, WATER_DEEP, depth > 80 ? 0.62 : 0.52, depth > 80 ? 150 : 175), x, y, right);
		});

		const c = cast;
		const ms = c ? now - c.t0 : null;
		const got = c?.got ?? null;
		const rod = rodAt(still ? (c ? LAND : null) : ms, got);
		const tip = tipOf(rod.a, rod.bend);

		// the fish that bites, swimming in under the float
		if (c && got && got.fish !== 'kasut' && ms !== null && ms > LAND + 150 && ms < LEAP && !still) {
			const pix = fish(got.fish, true).pix;
			const fromRight = c.to[0] < W - 40;
			const u = ease((ms - LAND - 150) / (NIBBLES[0] - LAND - 150));
			const endX = fromRight ? c.to[0] - 1 : c.to[0] + 2 - pix.w;
			const x = lerp(endX + (fromRight ? 34 : -34), endX, u) + (ms > STRIKE ? (((ms / 70) | 0) % 2) * 2 - 1 : 0);
			const y = c.to[1] + 3 + (ms > STRIKE ? -1 : 0);
			put(g, underwater(pix, WATER_DEEP, 0.4, 200), x, y, !fromRight);
		}

		// the float, its ripples and the splash it lands with
		let float: [number, number] | null = null;
		let sunk = 2;
		let sag = 5;
		if (!c) {
			if (rest) float = rest;
		} else if (still) {
			float = c.to;
		} else if (ms! < LET_GO) {
			float = null;
		} else if (ms! < LAND) {
			const swing = rodAt(LET_GO, null);
			const from = tipOf(swing.a, swing.bend);
			const u = (ms! - LET_GO) / (LAND - LET_GO);
			float = [lerp(from[0], c.to[0], u), lerp(from[1] + 8, c.to[1], u) - 30 * 4 * u * (1 - u)];
			sunk = 0;
			sag = 2;
		} else if (!got && ms! > GIVE_UP) {
			const u = Math.min(1, (ms! - GIVE_UP) / 500);
			float = [lerp(c.to[0], tip[0], u), lerp(c.to[1], tip[1] + 8, u) - 16 * 4 * u * (1 - u)];
			sunk = 0;
			sag = 1;
		} else if (got && ms! >= STRIKE) {
			float = ms! < LEAP ? [c.to[0], c.to[1] + 3] : null;
			sunk = 5;
			sag = 0;
		} else {
			float = c.to;
			const bob = (((ms! / 500) | 0) % 2) as 0 | 1;
			const nib = got && NIBBLES.some((at) => ms! > at && ms! < at + 130) ? 2 : 0;
			sunk = 2 + bob + nib;
		}

		if (float && sunk > 0) {
			// rings spreading on the water: one now and then, more when something tugs
			const fast = c && got && ms! > STRIKE;
			const every = fast ? 380 : 1500;
			const life = fast ? 600 : 1100;
			for (let k = 0; k < 2; k++) {
				const age = (now + k * (every / 2)) % every;
				if (age > life) continue;
				const u = age / life;
				const r = 2 + u * (fast ? 9 : 7);
				g.globalAlpha = 0.75 * (1 - u);
				ring(g, float[0] + 1, float[1] + 5, r, r * 0.32, FOAM);
				g.globalAlpha = 1;
			}
		}
		if (float && sunk > 0) drawFloat(g, float[0], float[1], c?.gold ?? false, sunk);

		put(g, lakeFront(), 0, 0);

		// the jetty: the bucket of what was caught, and the child with the rod
		put(g, bucket(caught > 0), BUCKET[0], BUCKET[1]);
		const lift = c && got && ms! > STRIKE && ms! < IN && ((ms! / 120) | 0) % 2 ? 1 : 0;
		cell(g, holdingSheet(me.avatar, me.colour, me.skin ?? 's2'), 0, 0, AX, AY - lift, true);
		drawRod(g, rod.a, rod.bend);

		// the line, from the rod's tip to the float (or straight down to it while it hangs there)
		const hang: [number, number] = [tip[0], tip[1] + 8];
		const end = float ?? (c && got && ms! >= LEAP && ms! < IN ? null : hang);
		if (end) sagLine(g, [tip[0], tip[1]], [end[0] + 1, end[1]], sag, LINE);
		if (!float && end === hang) drawFloat(g, hang[0], hang[1], c?.gold ?? false, 0);
		if (float && sunk === 0) drawFloat(g, float[0], float[1], c?.gold ?? false, 0);

		// golden bait sparkles
		if (c?.gold && float && !still) {
			for (let k = 0; k < 3; k++) {
				const a = now / 300 + k * 2.1;
				if (((now / 150 + k) | 0) % 3) dot(g, float[0] + 1 + Math.cos(a) * 4, float[1] + 1 + Math.sin(a) * 3, hex('#fff6b0'));
			}
		}

		if (c && !still && ms !== null) {
			// the splash where the float lands, and a bigger one where the catch leaps out
			for (const [at, size] of [[LAND, 1], ...(got ? [[LEAP, 1.6]] : [])] as [number, number][]) {
				const s = (ms - at) / 1000;
				if (s < 0 || s > 0.7) continue;
				for (let k = 0; k < 8 * size; k++) {
					const vx = (hash(k, 11) - 0.5) * 40 * size;
					const vy = -(28 + hash(k, 12) * 30) * size;
					const x = c.to[0] + 1 + vx * s;
					const y = c.to[1] + 3 + vy * s + 90 * s * s;
					if (y <= c.to[1] + 4) dot(g, x, y, k % 3 ? FOAM : hex('#9fe6ea'));
				}
			}
			// what bit: out of the water, over the line and into the bucket
			if (got && ms >= LEAP && ms < IN) {
				const u = (ms - LEAP) / (IN - LEAP);
				const pix = fish(got.fish, true).pix;
				const x = lerp(c.to[0] - pix.w / 2, BUCKET[0] + 5 - pix.w / 2, u);
				const y = lerp(c.to[1] - 2, BUCKET[1] - pix.h + 4, u) - 40 * 4 * u * (1 - u);
				put(g, pix, x, y);
				sagLine(g, [tip[0], tip[1]], [x + 2, y + pix.h / 2], 0, LINE);
			}
			// "!": something is on the line
			if (got && ms > STRIKE - 60 && ms < STRIKE + 500) put(g, alert(), AX + 3, AY - 12);
		}
	}

	const sceneLabel = $derived(`Tasik. Kamu berdiri di hujung jeti memegang joran. ${caught} ekor dalam baldi.`);
</script>

<div class="fun pancing">
	<ul class="stats" aria-label="Simpanan kamu">
		<li><Icon name="drop" size={20} /><strong>{world.bait}</strong> umpan</li>
		<li class="gold"><Icon name="star" size={20} /><strong>{world.gold}</strong> umpan emas</li>
		<li><strong>{caught}</strong> ekor ditangkap</li>
	</ul>

	<div class="frame">
		<Scene w={W} h={H} {paint} fps={20} label={sceneLabel}>
			<button type="button" class="water" onclick={tapLake} disabled={world.bait < 1 || busy} aria-label="Lempar joran ke tasik"></button>
			{#if card}
				{#key card.key}
					<div class="catch" class:gold={card.gold} class:boot={!card.value} role="status">
						<Sprite sheet={fish(card.fish)} s={4} />
						<p><strong>{world.fish[card.fish]?.name}</strong> <span>{card.value ? `+${card.value} mata` : 'Alamak! Bukan ikan.'}</span></p>
					</div>
				{/key}
			{/if}
		</Scene>
	</div>

	<div class="acts">
		<button type="button" class="btn btn--sea btn--big" onclick={() => throwLine(false)} disabled={world.bait < 1 || busy}>Lempar joran</button>
		{#if world.gold > 0}
			<button type="button" class="btn btn--sun btn--big" onclick={() => throwLine(true)} disabled={busy}>Guna umpan emas</button>
		{/if}
	</div>
	<p class="hint" aria-live="polite">
		{busy ? 'Sabar... tunggu ikan menyambar!' : world.bait || world.gold ? 'Ketik tasik di tempat kamu mahu memancing!' : 'Jawab soalan untuk dapat umpan.'}
	</p>

	{#if net.length}
		<section class="bucket" aria-label="Tangkapan terkini">
			{#each net as kind, i (i)}<span title={world.fish[kind]?.name}><Sprite sheet={fish(kind)} s={2} /></span>{/each}
		</section>
	{/if}
</div>

<style>
	.fun {
		display: grid;
		gap: 0.7rem;
	}
	.stats {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.stats li {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0.35rem 0.8rem;
		border-radius: var(--r-pill);
		background: var(--card);
		box-shadow: var(--card-shadow);
		font-weight: 800;
	}
	.stats .gold {
		background: #fff3cf;
	}
	.frame {
		overflow: hidden;
		border: 3px solid #2a1f2d;
		border-radius: 6px;
		box-shadow: 0 4px 0 #2a1f2d;
		background: #6fbde6;
	}
	.water {
		position: absolute;
		inset: 38% 0 0 38%;
		border: 0;
		padding: 0;
		background: transparent;
		cursor: crosshair;
	}
	.water:disabled {
		cursor: default;
	}
	.water:focus-visible {
		outline: 3px dashed #fff;
		outline-offset: -6px;
	}
	.catch {
		position: absolute;
		left: 50%;
		top: 8%;
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		translate: -50% 0;
		padding: 0.6rem 1rem;
		border: 3px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		box-shadow: 0 4px 0 #2a1f2d;
		font-weight: 800;
		line-height: 1.25;
		text-align: center;
		animation: splash 2.4s steps(12) both;
		pointer-events: none;
	}
	.catch p {
		display: grid;
		font-size: 0.95rem;
	}
	.catch span {
		color: #1f7a4a;
	}
	.catch.boot span {
		color: #b0442a;
	}
	.catch.gold {
		background: #fff3cf;
	}
	.acts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.6rem;
	}
	.acts .btn {
		flex: 1 1 12rem;
	}
	.hint {
		color: var(--ink-2);
		font-weight: 800;
		text-align: center;
	}
	.bucket {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem;
		padding: 0.6rem;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	@keyframes splash {
		0% {
			opacity: 0;
			transform: translateY(30%);
		}
		12%,
		85% {
			opacity: 1;
			transform: translateY(0);
		}
		100% {
			opacity: 0;
			transform: translateY(-10%);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.catch {
			animation: none;
		}
	}
</style>
