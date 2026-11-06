<!--
	Lumba Wau's sky, as one pixel scene: every child stands in the padi field holding the string of
	their own wau bulan, which flies as high as their answers have lifted it; the string sags from their
	hand up to the kite. Clouds drift past (fast in a strong wind, with streaks of wind). The child's own
	wau blinks with a white rim and is tagged "Kamu". On a phone it is compact; on the host's screen it
	is wider. A strong wind (the race's rapids) is announced.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import { CW, ROW, chibiSheet } from '$lib/pixel/chibi';
	import Scene from '$lib/pixel/Scene.svelte';
	import { type G, cell, dot, hash, hex, put, sagLine, stillWanted } from '$lib/pixel/scene';
	import { memo } from '$lib/pixel/cache';
	import { Pix } from '$lib/pixel/pix';
	import { kite } from './art';
	import { DAY, M, bands, cloud, grassland, noise, rgba, sun, treeline } from './scenery';

	interface Race {
		length: number;
		rapids: boolean;
		boats: { id: string; m: number }[];
	}
	let { race, people, me = null, compact = false }: { race: Race; people: Map<string, Person>; me?: string | null; compact?: boolean } = $props();

	const W = $derived(compact ? 176 : 256);
	const H = $derived(compact ? 150 : 132);
	const GROUND = $derived(H - 26);
	const still = stillWanted();

	const top = $derived(Math.max(race.length, ...race.boats.map((b) => b.m), 1));
	const flying = $derived(race.boats.filter((b) => people.has(b.id)));
	// spread across the sky in join order, each child under their own kite
	const lanes = $derived(
		flying.map((b, i) => ({ ...b, i, x: flying.length > 1 ? 16 + (i / (flying.length - 1)) * (W - 32) : W / 2, h: Math.min(1, b.m / top) }))
	);
	const kiteY = (h: number) => GROUND - 62 + (4 - (GROUND - 62)) * h;

	/** Sky, far trees and the padi field the children stand in, for one size of scene. */
	function field(w: number, h: number, ground: number): Pix {
		return memo(`kites:field:${w}:${h}`, () => {
			const p = new Pix(w, h);
			bands(p, 0, ground, DAY, 4);
			sun(p, w - 22, 14, 6);
			treeline(p, -4, w + 4, ground - 1, M.pine, 17);
			grassland(p, ground, h, 31);
			// rows of padi in the field
			for (let y = ground + 3; y < h; y += 3) {
				for (let x = (y >> 1) % 4; x < w; x += 4) if (noise(x, y, 5) < 0.7) p.set(x, y, M.grass.c[4]).set(x, y + 1, M.grass.c[1]);
			}
			return p;
		});
	}

	const shown = new Map<string, number>();
	const STRING = hex('#ffffff', 190);

	function paint(g: G, t: number) {
		const now = still ? 0 : t;
		const w = W;
		const ground = GROUND;
		put(g, field(w, H, ground), 0, 0);
		const speed = race.rapids ? 0.03 : 0.004;
		for (let i = 0; i < 3; i++) {
			const span = w + 60;
			const x = ((now * speed * (1 + i * 0.3) + hash(i, 1) * span) % span) - 40;
			put(g, cloud(i), x, 8 + i * 22);
		}
		if (race.rapids && !still) {
			// streaks of wind
			for (let k = 0; k < 14; k++) {
				const y = 6 + hash(k, 2) * (ground - 20);
				const x = ((now * 0.12 + hash(k, 3) * (w + 40)) % (w + 40)) - 20;
				g.fillStyle = 'rgba(255,255,255,0.7)';
				g.fillRect(Math.round(x), Math.round(y), 6 + Math.round(hash(k, 4) * 6), 1);
			}
		}

		// each child, then their string, then their kite; the child's own drawn last, on top
		const order = [...lanes].sort((a, b) => (a.id === me ? 1 : 0) - (b.id === me ? 1 : 0));
		for (const lane of order) {
			const person = people.get(lane.id);
			if (!person) continue;
			const cur = shown.get(lane.id) ?? lane.h;
			const h = still ? lane.h : cur + (lane.h - cur) * 0.08;
			shown.set(lane.id, h);
			const feet = ground + 18 - (lane.i % 2) * 4;
			const cx = Math.round(lane.x);
			const sway = race.rapids ? Math.round(Math.sin(now / 160 + lane.i) * 2) : (((now / 700 + lane.i) | 0) % 2);
			const kx = cx - 12 + sway + 6;
			const ky = Math.round(kiteY(h) + (((now / 900 + lane.i) | 0) % 2));
			const child = chibiSheet(person.avatar, person.colour, person.skin ?? 's2');
			const hand: [number, number] = [cx - CW / 2 + 15, feet - 30 + 26];
			cell(g, child, 0, ROW.front, cx - CW / 2, feet - 30);
			const len = Math.hypot(kx + 12 - hand[0], ky + 20 - hand[1]);
			sagLine(g, hand, [kx + 12, ky + 20], Math.min(10, len * 0.06), STRING);
			put(g, kite(lane.i).pix, kx, ky);
			if (lane.id === me && ((now / 400) | 0) % 2 === 0) {
				// a blinking rim round the child's own kite
				for (const [dx, dy] of [[12, -1], [24, 9], [12, 14], [0, 9]]) dot(g, kx + dx, ky + dy, rgba('#ffffff'));
			}
		}
	}

	const label = $derived(`Ketinggian wau. ${lanes.map((b) => `${people.get(b.id)?.name}: ${b.m} m`).join('. ')}`);
</script>

<figure class="sky" class:compact class:windy={race.rapids}>
	<Scene w={W} h={H} {paint} fps={15} {label}>
		<span class="goal" aria-hidden="true">{top} m</span>
		{#each lanes as b (b.id)}
			{@const person = people.get(b.id)!}
			<span
				class="tag"
				class:mine={b.id === me}
				style:left="{((b.x + 6) / W) * 100}%"
				style:top="{((kiteY(b.h) + 31) / H) * 100}%"
				aria-hidden="true">{b.id === me ? 'Kamu' : person.name}</span
			>
		{/each}
		{#if race.rapids}<p class="wind" role="status">Angin kencang! Semua wau naik.</p>{/if}
	</Scene>
</figure>

<style>
	.sky {
		margin: 0;
		overflow: hidden;
		border: 3px solid #2a1f2d;
		border-radius: 6px;
		box-shadow: 0 4px 0 #2a1f2d;
		background: #8fcdee;
	}
	.goal {
		position: absolute;
		right: 0.5rem;
		top: 0.4rem;
		padding: 0.1rem 0.5rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		font: 700 0.8rem/1.3 var(--font-display);
	}
	.tag {
		position: absolute;
		translate: -50% 0;
		padding: 0 0.35rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		color: #2a1f2d;
		font: 600 clamp(0.55rem, 2.6cqw, 0.8rem) / 1.35 var(--font-pixel);
		white-space: nowrap;
		transition: top 1.2s cubic-bezier(0.2, 0.8, 0.3, 1);
	}
	.tag.mine {
		z-index: 2;
		background: var(--sun);
	}
	.wind {
		position: absolute;
		left: 50%;
		top: 38%;
		translate: -50% 0;
		padding: 0.4rem 0.9rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #fff6e6;
		box-shadow: 0 3px 0 #2a1f2d;
		font: 700 1rem/1.3 var(--font-display);
		white-space: nowrap;
	}
	@media (prefers-reduced-motion: reduce) {
		.tag {
			transition: none;
		}
	}
</style>
