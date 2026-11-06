<!--
	Pelabuhan Melaka: ships at their berths along a wooden wharf on a busy sea, each flying its traders'
	name (the left-hand things); load each ship with the cargo card that is its.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import MatchCard from '../MatchCard.svelte';
	import MatchPlay, { type MatchView } from '../MatchPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();
	const SAILS = ['#e2483d', '#2f7fcf', '#f5c518', '#2bb0a6', '#8a5cd1'];
</script>

<MatchPlay {p} pool="Muatan di gudang">
	{#snippet board(v: MatchView)}
		<div class="harbour">
			{#each v.left as l, i (l.id)}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div class="berth" data-zone={v.zone(l.id)} onclick={() => v.tapLeft(l.id)}>
					<span class="ship" class:sail={v.allRight} style:--sail={SAILS[i % SAILS.length]} aria-hidden="true">
						<i class="mast"></i><i class="canvas"></i><i class="hull"></i>
					</span>
					<div class="manifest">
						<span class="flag">{#if l.sticker}<Sticker key={l.sticker} size={22} alt="" />{/if}{l.text}</span>
						<span class="cargo"><MatchCard {v} left={l.id} empty="Muatkan kargo" /></span>
					</div>
				</div>
			{/each}
			<span class="wharf" aria-hidden="true"></span>
		</div>
	{/snippet}
</MatchPlay>

<style>
	.harbour {
		position: relative;
		display: grid;
		gap: 0.5rem;
		padding: 0.7rem 0.6rem 1.4rem;
		border-radius: var(--r-lg);
		background:
			repeating-linear-gradient(170deg, rgb(255 255 255 / 0.12) 0 2px, transparent 2px 22px),
			linear-gradient(180deg, #4aa6c9, #2b7ea6);
		box-shadow: inset 0 0 0 3px #1f5f80;
		overflow: hidden;
	}
	.berth {
		position: relative;
		z-index: 1;
		display: grid;
		grid-template-columns: 4.6rem 1fr;
		align-items: center;
		gap: 0.5rem;
		min-height: 4.6rem;
		padding: 0.3rem 0.4rem;
		border-radius: 12px;
		background: rgb(255 255 255 / 0.12);
	}
	.berth:global(.zone-hover) {
		background: rgb(255 230 150 / 0.35);
	}
	.ship {
		position: relative;
		width: 4.4rem;
		height: 4rem;
		animation: bob 2.4s ease-in-out infinite;
	}
	.ship i {
		position: absolute;
		display: block;
	}
	.mast {
		left: 48%;
		top: 0.1rem;
		width: 3px;
		height: 2.8rem;
		background: #5a3a1a;
	}
	.canvas {
		left: 52%;
		top: 0.3rem;
		width: 1.8rem;
		height: 2rem;
		background: var(--sail);
		clip-path: polygon(0 0, 100% 100%, 0 100%);
		transform-origin: left center;
		transition: transform 0.6s;
	}
	.sail .canvas {
		transform: scaleX(1.25);
	}
	.hull {
		left: 0;
		bottom: 0.2rem;
		width: 100%;
		height: 1.1rem;
		border-radius: 0 0 50% 50% / 0 0 100% 100%;
		background: linear-gradient(180deg, #8c5a2c, #5e3a18);
	}
	.manifest {
		display: grid;
		gap: 0.25rem;
		justify-items: start;
	}
	.flag {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.15rem 0.5rem;
		border-radius: 4px;
		background: #fff7e0;
		color: #3b2a14;
		font: 700 0.92rem/1.15 var(--font-display);
		box-shadow: 0 2px 0 #b98a44;
	}
	.cargo {
		display: inline-grid;
		min-height: 2.2rem;
		align-items: center;
		padding: 0.15rem 0.4rem;
		border: 2px dashed rgb(255 255 255 / 0.7);
		border-radius: 8px;
	}
	.cargo :global(.empty) {
		color: #e6f6ff;
	}
	.wharf {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		height: 1rem;
		background: repeating-linear-gradient(90deg, #a77a46 0 26px, #8a6235 26px 28px);
	}
	@keyframes bob {
		50% {
			transform: translateY(3px) rotate(-1.5deg);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.ship {
			animation: none;
		}
	}
</style>
