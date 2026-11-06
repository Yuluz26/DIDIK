<!--
	Peta Hijrah: the land between Makkah and Madinah on the map of Arabia, the road marked out stop by stop
	from Makkah in the south to Madinah in the north. Put each place on its stop in the order of the
	journey; a camel walks to the furthest stop filled.
-->
<script lang="ts">
	import { diagramUrl } from '$lib/diagrams';
	import Sticker from '$ui/Sticker.svelte';
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	// The road on the zoomed map, in percent: Makkah, south to Gua Thur, out to the coast, north along it,
	// inland to Quba and Madinah.
	const ROAD: [number, number][] = [
		[58, 80],
		[60, 87],
		[46, 74],
		[31, 48],
		[40, 26],
		[43, 17]
	];
	const lengths = ROAD.slice(1).map((pt, i) => Math.hypot(pt[0] - ROAD[i][0], pt[1] - ROAD[i][1]));
	const total = lengths.reduce((a, b) => a + b, 0);

	/** A point a fraction of the way along the road. */
	function along(t: number): [number, number] {
		let d = t * total;
		for (let i = 0; i < lengths.length; i++) {
			if (d <= lengths[i] || i === lengths.length - 1) {
				const u = Math.min(1, d / lengths[i]);
				return [ROAD[i][0] + (ROAD[i + 1][0] - ROAD[i][0]) * u, ROAD[i][1] + (ROAD[i + 1][1] - ROAD[i][1]) * u];
			}
			d -= lengths[i];
		}
		return ROAD[ROAD.length - 1];
	}
	const stops = (n: number) => Array.from({ length: n }, (_, i) => along(n === 1 ? 0 : i / (n - 1)));
</script>

<OrderPlay {p} pic={() => 'pin-peta'} pool="Tempat" tip="Mula di Makkah (bawah). Ikut jalan ke utara.">
	{#snippet board(v: OrderView)}
		{@const pts = stops(v.slots.length)}
		{@const reach = v.slots.reduce((last, s, i) => (s ? i : last), -1)}
		<div class="map" style:background-image="url({diagramUrl('rajah-arab')})">
			<span class="sea" aria-hidden="true">Laut Merah</span>
			<svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
				<polyline points={ROAD.map((pt) => pt.join(',')).join(' ')} class="road" />
			</svg>
			{#each pts as [x, y], i (i)}
				{@const ok = v.ok(i)}
				<span class="stop" class:filled={!!v.slots[i]} class:ok={ok === true} class:off={ok === false} style:left="{x}%" style:top="{y}%" data-zone={v.zone(i)}>{i + 1}</span>
			{/each}
			{#if reach >= 0}
				<span class="camel" style:left="{pts[reach][0]}%" style:top="{pts[reach][1]}%" aria-hidden="true"><Sticker key="unta" size={40} alt="" /></span>
			{/if}
			<span class="north" aria-hidden="true">U ↑</span>
		</div>
		<ol class="legs">
			{#each v.slots as id, i (i)}
				{@const ok = v.ok(i)}
				<li class="leg" data-zone={v.zone(i)}>
					<span class="n">{i + 1}</span>
					{#if id}
						<button type="button" class="place" disabled={v.locked} {@attach v.grab(i)} aria-label="{v.text(id)}, hentian {i + 1}">
							{v.text(id)}
							{#if ok !== null}<Mark {ok} />{/if}
						</button>
						{#if v.should(i)}<span class="should">→ {v.should(i)}</span>{/if}
					{:else}
						<span class="empty">{i === 0 ? 'Bermula di sini' : i === v.slots.length - 1 ? 'Tiba di sini' : 'Singgah'}</span>
					{/if}
				</li>
			{/each}
		</ol>
	{/snippet}
</OrderPlay>

<style>
	.map {
		position: relative;
		aspect-ratio: 4 / 3;
		border-radius: var(--r-lg);
		background-color: #a3d6ee;
		background-repeat: no-repeat;
		background-size: 360% auto;
		background-position: 18% 50%;
		box-shadow:
			inset 0 0 0 3px #c49a52,
			inset 0 0 40px rgb(120 80 20 / 0.25);
		overflow: hidden;
	}
	svg {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
	}
	.road {
		fill: none;
		stroke: #8a4b14;
		stroke-dasharray: 2.2 1.6;
		stroke-linecap: round;
		stroke-linejoin: round;
		vector-effect: non-scaling-stroke;
		stroke-width: 3;
	}
	.sea {
		position: absolute;
		left: 6%;
		top: 52%;
		rotate: -60deg;
		color: #2e6f93;
		font: 700 0.8rem var(--font-display);
		letter-spacing: 0.1em;
		opacity: 0.8;
	}
	.north {
		position: absolute;
		right: 0.6rem;
		top: 0.5rem;
		padding: 0.1rem 0.4rem;
		border-radius: 6px;
		background: rgb(255 255 255 / 0.75);
		color: #6b4a1a;
		font: 700 0.8rem var(--font-display);
	}
	.stop {
		position: absolute;
		z-index: 1;
		display: grid;
		place-items: center;
		width: 1.9rem;
		height: 1.9rem;
		translate: -50% -50%;
		border: 3px solid #fff8e8;
		border-radius: 50%;
		background: #b8322a;
		color: #fff;
		font: 700 0.85rem var(--font-display);
		box-shadow: 0 3px 6px rgb(0 0 0 / 0.3);
	}
	.stop.filled {
		background: #2c6e8f;
	}
	.stop.ok {
		background: var(--good);
	}
	.stop.off {
		background: var(--almost);
	}
	.stop:global(.zone-hover) {
		transform: scale(1.2);
	}
	.camel {
		position: absolute;
		z-index: 2;
		translate: -10% -95%;
		transition:
			left 0.7s var(--ease-out, ease-out),
			top 0.7s var(--ease-out, ease-out);
		filter: drop-shadow(0 3px 3px rgb(0 0 0 / 0.3));
	}
	.legs {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
		gap: 0.45rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.leg {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.4rem;
		min-height: 3rem;
		padding: 0.3rem 0.5rem;
		border: 2px dashed #d3b07a;
		border-radius: 10px;
		background: #fffaf0;
	}
	.leg:global(.zone-hover) {
		border-color: #b8322a;
	}
	.n {
		display: grid;
		place-items: center;
		width: 1.6rem;
		height: 1.6rem;
		border-radius: 50%;
		background: #6b4a1a;
		color: #fff;
		font: 700 0.8rem var(--font-display);
	}
	.place {
		position: relative;
		padding: 0.3rem 0.6rem;
		border: 0;
		border-radius: 8px;
		background: #f3e2bd;
		color: #3b2a14;
		font: 700 0.95rem/1.15 var(--font-body);
		cursor: grab;
		touch-action: none;
	}
	.place:disabled {
		cursor: default;
	}
	.empty {
		color: #a2875b;
		font-weight: 700;
		font-size: 0.85rem;
	}
	.should {
		color: #8a2a00;
		font-weight: 800;
		font-size: 0.82rem;
	}
</style>
