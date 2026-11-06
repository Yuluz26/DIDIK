<!--
	Lentera Tugas: a row of unlit lanterns at night, each with a name (the left-hand things). Hang the right
	card under each lantern and it lights up warm and gold. Only words and lanterns: no figure is drawn.
-->
<script lang="ts">
	import MatchCard from '../MatchCard.svelte';
	import MatchPlay, { type MatchView } from '../MatchPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();
</script>

<MatchPlay {p} pool="Tugas">
	{#snippet board(v: MatchView)}
		<div class="night">
			<span class="string" aria-hidden="true"></span>
			{#each v.left as l (l.id)}
				{@const on = !!v.placed(l.id)}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div class="hang" data-zone={v.zone(l.id)} onclick={() => v.tapLeft(l.id)}>
					<span class="cord" aria-hidden="true"></span>
					<span class="lantern" class:on aria-hidden="true"><i class="cap"></i><i class="glass"></i><i class="foot"></i></span>
					<p class="name">{l.text}</p>
					<div class="tag"><MatchCard {v} left={l.id} empty="Gantung tugas" dark /></div>
				</div>
			{/each}
		</div>
	{/snippet}
</MatchPlay>

<style>
	.night {
		position: relative;
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(7rem, 1fr));
		gap: 0.6rem;
		padding: 1.4rem 0.6rem 0.8rem;
		border-radius: var(--r-lg);
		background:
			radial-gradient(1px 1px at 15% 20%, #fff, transparent),
			radial-gradient(1px 1px at 80% 12%, #fff, transparent),
			radial-gradient(1.5px 1.5px at 55% 8%, #fff, transparent),
			linear-gradient(180deg, #0f1638, #23205a);
		box-shadow: inset 0 0 0 3px #0a0f28;
	}
	.string {
		position: absolute;
		left: 4%;
		right: 4%;
		top: 0.6rem;
		height: 1.2rem;
		border-bottom: 2px solid rgb(220 200 150 / 0.6);
		border-radius: 0 0 50% 50%;
	}
	.hang {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		padding-bottom: 0.3rem;
		border-radius: 12px;
	}
	.hang:global(.zone-hover) {
		background: rgb(255 210 120 / 0.15);
	}
	.cord {
		width: 2px;
		height: 0.8rem;
		background: rgb(220 200 150 / 0.7);
	}
	.lantern {
		display: grid;
		justify-items: center;
		filter: drop-shadow(0 4px 4px rgb(0 0 0 / 0.4));
	}
	.lantern i {
		display: block;
	}
	.cap,
	.foot {
		width: 2.2rem;
		height: 0.45rem;
		border-radius: 3px;
		background: #8a6418;
	}
	.glass {
		width: 3rem;
		height: 3.6rem;
		border-radius: 1.4rem;
		background: repeating-linear-gradient(90deg, #6e5a3a 0 2px, #4a3f37 2px 8px);
		box-shadow: inset 0 0 0 2px #8a6418;
		transition:
			background 0.5s,
			box-shadow 0.5s;
	}
	.on .glass {
		background: repeating-linear-gradient(90deg, #c08a1a 0 2px, #ffd56b 2px 8px);
		box-shadow:
			inset 0 0 0 2px #c08a1a,
			0 0 26px 10px rgb(255 200 80 / 0.55);
	}
	.name {
		color: #ffe9b0;
		font: 700 1.05rem var(--font-display);
		text-align: center;
	}
	.tag {
		display: grid;
		place-items: center;
		min-height: 2.4rem;
		width: 100%;
		padding: 0.2rem;
		border-radius: 8px;
		background: rgb(255 255 255 / 0.1);
	}
</style>
