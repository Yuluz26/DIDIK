<!--
	Lumba Wau's sky: every child's wau bulan flying at the height their answers have lifted it, highest
	at the top, with clouds drifting past. The child's own wau has a ring and "Kamu". On a phone it is
	compact; on the host's screen it fills the stage. A strong wind (the race's rapids) is announced.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import { kite } from './art';

	interface Race {
		length: number;
		rapids: boolean;
		boats: { id: string; m: number }[];
	}
	let { race, people, me = null, compact = false }: { race: Race; people: Map<string, Person>; me?: string | null; compact?: boolean } = $props();

	const top = $derived(Math.max(race.length, ...race.boats.map((b) => b.m), 1));
	const flying = $derived(race.boats.filter((b) => people.has(b.id)));
	// spread across the sky in join order; the child's own wau is never hidden behind another
	const lanes = $derived(flying.map((b, i) => ({ ...b, x: flying.length > 1 ? 6 + (i / (flying.length - 1)) * 82 : 46, i })));
</script>

<figure class="sky" class:compact class:windy={race.rapids} aria-label="Ketinggian wau">
	{#each [12, 38, 64] as y, i (y)}<span class="cloud" style:top="{y}%" style:--d="{38 + i * 9}s" style:--delay="{-i * 11}s" aria-hidden="true"></span>{/each}
	<span class="goal" aria-hidden="true">{top} m</span>
	{#each lanes as b (b.id)}
		{@const person = people.get(b.id)!}
		{@const h = Math.min(1, b.m / top)}
		<span class="wau" class:mine={b.id === me} style:left="{b.x}%" style:bottom="{8 + h * 78}%">
			<Sprite sheet={kite(b.i)} s={compact ? 2 : 3} />
			<span class="tag">{b.id === me ? 'Kamu' : person.name}</span>
			<span class="string" style:height="{8 + h * 78}cqh" aria-hidden="true"></span>
		</span>
	{/each}
	{#if race.rapids}<p class="wind" role="status">Angin kencang! Semua wau naik.</p>{/if}
	<figcaption class="visually-hidden">
		{#each lanes as b (b.id)}{people.get(b.id)?.name}: {b.m} m. {/each}
	</figcaption>
</figure>

<style>
	.sky {
		position: relative;
		margin: 0;
		height: clamp(18rem, 52vh, 34rem);
		overflow: hidden;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #2f7fcf 0%, #77c3ef 55%, #cdeefc 88%, #9fd472 88%);
		box-shadow: var(--card-shadow);
		container-type: size;
		image-rendering: pixelated;
	}
	.compact {
		height: clamp(14rem, 38vh, 22rem);
	}
	.cloud {
		position: absolute;
		left: -20%;
		width: 7rem;
		height: 2rem;
		border-radius: 999px;
		background: rgb(255 255 255 / 0.85);
		box-shadow:
			1.6rem -0.8rem 0 0.2rem rgb(255 255 255 / 0.85),
			3.4rem 0 0 -0.1rem rgb(255 255 255 / 0.85);
		animation: drift var(--d) linear var(--delay) infinite;
	}
	.windy .cloud {
		animation-duration: 6s;
	}
	.goal {
		position: absolute;
		right: 0.6rem;
		top: 0.4rem;
		padding: 0.15rem 0.6rem;
		border-radius: 999px;
		background: rgb(255 255 255 / 0.85);
		font: 700 0.85rem var(--font-display);
	}
	.wau {
		position: absolute;
		display: grid;
		justify-items: center;
		translate: -50% 0;
		transition: bottom 1.2s cubic-bezier(0.3, 1.2, 0.5, 1);
		animation: sway 2.6s ease-in-out infinite;
	}
	.wau.mine {
		z-index: 2;
		filter: drop-shadow(0 0 0.4rem #fff) drop-shadow(0 0 0.2rem #ffcf5a);
	}
	.tag {
		padding: 0.05rem 0.45rem;
		border-radius: 999px;
		background: rgb(255 255 255 / 0.9);
		font: 700 0.72rem var(--font-display);
		white-space: nowrap;
	}
	.mine .tag {
		background: #ffcf5a;
	}
	.string {
		position: absolute;
		top: 100%;
		left: 50%;
		width: 1px;
		background: rgb(255 255 255 / 0.7);
	}
	.wind {
		position: absolute;
		left: 50%;
		top: 40%;
		translate: -50% 0;
		padding: 0.5rem 1rem;
		border-radius: var(--r-lg);
		background: var(--paper);
		box-shadow: var(--card-shadow);
		font: 700 1.1rem var(--font-display);
	}
	@keyframes drift {
		to {
			left: 110%;
		}
	}
	@keyframes sway {
		50% {
			transform: rotate(4deg) translateY(-3px);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.cloud,
		.wau {
			animation: none;
		}
		.wau {
			transition: none;
		}
	}
</style>
