<!--
	Langit Waktu Solat: a row of windows onto the sky, one for each left-hand thing. A prayer's name paints
	its window with its own sky (Subuh's dawn, Zohor's noon sun, Asar's afternoon, Maghrib's sunset,
	Isyak's stars); anything else gets a day sky. Drop the matching card under each window.
-->
<script lang="ts">
	import MatchCard from '../MatchCard.svelte';
	import MatchPlay, { type MatchView } from '../MatchPlay.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	const SKIES: [RegExp, string, string, number][] = [
		[/subuh|fajar/i, 'linear-gradient(180deg, #2b2f6b, #8a6bb8 60%, #ffb38a)', '#ffd9a8', 92],
		[/syuruk/i, 'linear-gradient(180deg, #8fc7ff, #ffd7a0)', '#ffe08a', 80],
		[/dhuha|duha/i, 'linear-gradient(180deg, #5fb2f2, #ffe7b8)', '#ffe9a0', 58],
		[/zohor|zuhur/i, 'linear-gradient(180deg, #2f8fe8, #9fd6ff)', '#fff3a0', 14],
		[/asar|asr/i, 'linear-gradient(180deg, #4a9fe0, #f7d58f)', '#ffe08a', 46],
		[/maghrib/i, 'linear-gradient(180deg, #5a3a8a, #f0715a 55%, #ffb347)', '#ff7a3a', 86],
		[/isyak|isya|tahajud|witir|malam/i, 'radial-gradient(1px 1px at 20% 30%, #fff, transparent), radial-gradient(1px 1px at 70% 20%, #fff, transparent), radial-gradient(1px 1px at 50% 60%, #fff, transparent), linear-gradient(180deg, #0b1030, #1f2a5a)', '#f3f0d8', 22]
	];
	const NIGHT = /isyak|isya|tahajud|witir|malam/i;
	const sky = (text: string) => SKIES.find(([re]) => re.test(text)) ?? [null, 'linear-gradient(180deg, #7fc4f5, #d6efff)', '#fff3a0', 30];
</script>

<MatchPlay {p} pool="Kad">
	{#snippet board(v: MatchView)}
		<div class="wall">
			{#each v.left as l (l.id)}
				{@const [, bg, orb, y] = sky(l.text)}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div class="window" data-zone={v.zone(l.id)} onclick={() => v.tapLeft(l.id)}>
					<div class="pane" style:background={bg}>
						<span class="orb" class:moon={NIGHT.test(l.text)} style:background={orb} style:top="{y}%" aria-hidden="true"></span>
						<span class="dome" aria-hidden="true"></span>
					</div>
					<p class="name">{l.text}</p>
					<div class="sill"><MatchCard {v} left={l.id} empty="?" /></div>
				</div>
			{/each}
		</div>
	{/snippet}
</MatchPlay>

<style>
	.wall {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(6.4rem, 1fr));
		gap: 0.6rem;
		padding: 0.7rem;
		border-radius: var(--r-lg);
		background:
			repeating-linear-gradient(0deg, rgb(0 0 0 / 0.04) 0 2px, transparent 2px 24px),
			linear-gradient(180deg, #f6ecd9, #ead9b9);
		box-shadow: inset 0 0 0 3px #d6bf92;
	}
	.window {
		display: grid;
		gap: 0.3rem;
		justify-items: center;
		padding: 0.35rem;
		border-radius: 3.2rem 3.2rem 0.6rem 0.6rem;
		background: #fffaf0;
		box-shadow: 0 4px 0 #cdb588;
	}
	.window:global(.zone-hover) {
		box-shadow:
			0 4px 0 #cdb588,
			0 0 0 3px #e0a21a;
	}
	.pane {
		position: relative;
		width: 100%;
		aspect-ratio: 3 / 3.2;
		overflow: hidden;
		border-radius: 3rem 3rem 0.3rem 0.3rem;
		box-shadow: inset 0 0 0 3px #8a6a3a;
	}
	.orb {
		position: absolute;
		left: 55%;
		width: 1.5rem;
		height: 1.5rem;
		border-radius: 50%;
		box-shadow: 0 0 16px 4px rgb(255 230 150 / 0.7);
	}
	.orb.moon {
		box-shadow: inset -6px 2px 0 0 #1f2a5a;
		background: #f3f0d8 !important;
	}
	.dome {
		position: absolute;
		left: 50%;
		bottom: 0;
		width: 70%;
		height: 32%;
		translate: -50% 0;
		background:
			radial-gradient(circle at 50% 100%, rgb(20 20 40 / 0.85) 0 45%, transparent 46%) 50% 100% / 60% 100% no-repeat,
			linear-gradient(180deg, transparent 55%, rgb(20 20 40 / 0.85) 55%);
	}
	.name {
		color: #3b2a14;
		font: 700 1.05rem var(--font-display);
	}
	.sill {
		display: grid;
		place-items: center;
		width: 100%;
		min-height: 2.4rem;
		border-radius: 8px;
		background: #f1e3c6;
	}
</style>
