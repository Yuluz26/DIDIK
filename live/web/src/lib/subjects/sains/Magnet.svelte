<!--
	Magnet Ajaib: a big horseshoe magnet with field lines curving off its poles. Things for the first group
	stick to the magnet; things for the other groups go in the trays below.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import SortPlay, { type SortView } from '../SortPlay.svelte';
	import SortedThing from '../SortedThing.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();
</script>

<SortPlay {p} pool="Benda" tip="Bawa setiap benda ke magnet atau ke dulang.">
	{#snippet board(v: SortView)}
		{@const [pull, ...rest] = v.groups}
		<div class="lab">
			{#if pull}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div class="field" data-zone={v.zone(pull.id)} onclick={() => v.tapGroup(pull.id)}>
					<svg class="lines" viewBox="0 0 200 120" aria-hidden="true">
						{#each [20, 34, 48] as r (r)}
							<path d="M {70 - r * 0.2} 110 C {70 - r} {40 - r * 0.6}, {130 + r} {40 - r * 0.6}, {130 + r * 0.2} 110" />
						{/each}
					</svg>
					<div class="horseshoe" class:buzz={v.allRight} aria-hidden="true">
						<span class="arm l"><b>U</b></span>
						<span class="arm r"><b>S</b></span>
					</div>
					<h4>{pull.name}</h4>
					<div class="stuck">
						{#each v.inside(pull.id) as item (item.id)}<SortedThing {v} {item} group={pull.id} />{/each}
					</div>
				</div>
			{/if}
			<div class="trays">
				{#each rest as g (g.id)}
					<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
					<div class="tray" data-zone={v.zone(g.id)} onclick={() => v.tapGroup(g.id)}>
						<h4>{#if g.sticker}<Sticker key={g.sticker} size={26} alt="" />{/if}{g.name}</h4>
						<div class="stuck">
							{#each v.inside(g.id) as item (item.id)}<SortedThing {v} {item} group={g.id} />{/each}
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/snippet}
</SortPlay>

<style>
	.lab {
		display: grid;
		gap: 0.6rem;
		padding: 0.7rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #eef3f8, #dfe7ef);
		box-shadow: inset 0 0 0 3px #c4d2df;
	}
	.field {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		min-height: 11rem;
		padding: 0.4rem;
		border: 2px dashed #9fb3c7;
		border-radius: var(--r-lg);
		background: radial-gradient(circle at 50% 30%, #ffffff, #e9f0f6 70%);
	}
	.field:global(.zone-hover) {
		border-color: #d33a2c;
		box-shadow: 0 0 0 4px rgb(211 58 44 / 0.15);
	}
	.lines {
		position: absolute;
		inset: 0 10% auto;
		height: 7rem;
		width: 80%;
		pointer-events: none;
	}
	.lines path {
		fill: none;
		stroke: rgb(120 140 170 / 0.45);
		stroke-width: 1.5;
		stroke-dasharray: 4 4;
		animation: flow 2s linear infinite;
	}
	.horseshoe {
		position: relative;
		width: 7.5rem;
		height: 5.6rem;
		margin-top: 0.4rem;
		border: 1.6rem solid #d33a2c;
		border-top: 0;
		border-radius: 0 0 4rem 4rem;
		rotate: 180deg;
		filter: drop-shadow(0 6px 6px rgb(0 0 0 / 0.2));
		box-shadow: inset 0 -6px 0 rgb(0 0 0 / 0.12);
	}
	.horseshoe.buzz {
		animation: buzz 0.18s linear infinite;
	}
	.arm {
		position: absolute;
		top: -1px;
		width: 1.6rem;
		height: 1.4rem;
		background: linear-gradient(180deg, #e8edf2, #aeb8c4);
		display: grid;
		place-items: center;
	}
	.arm b {
		rotate: 180deg;
		color: #2a3340;
		font: 700 0.8rem var(--font-display);
	}
	.arm.l {
		left: -1.6rem;
	}
	.arm.r {
		right: -1.6rem;
	}
	h4 {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		color: #2a3340;
		font: 700 1rem var(--font-display);
	}
	.stuck {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.35rem;
		min-height: 2.6rem;
	}
	.trays {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
		gap: 0.5rem;
	}
	.tray {
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		min-height: 6rem;
		padding: 0.5rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #c9b08a, #a88a5c);
		box-shadow:
			inset 0 6px 10px rgb(0 0 0 / 0.2),
			0 3px 0 #7c6236;
	}
	.tray h4 {
		color: #fff;
		text-shadow: 0 1px 2px rgb(0 0 0 / 0.35);
	}
	.tray:global(.zone-hover) {
		outline: 3px solid #f0a400;
	}
	@keyframes flow {
		to {
			stroke-dashoffset: -16;
		}
	}
	@keyframes buzz {
		50% {
			translate: 1px 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.lines path,
		.horseshoe.buzz {
			animation: none;
		}
	}
</style>
