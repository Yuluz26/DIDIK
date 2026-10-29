<!--
	A transition text banner ("Jawapan Betul!", "Boss Akan Menyerang!"...): the supplied vector-authored
	art, over the scene and never in the way (no pointer events). Six of them are 12-frame animations,
	played over the time the banner stays; the rest are one picture that drops in. Each fades out over its
	last moments, so one banner gives way smoothly to the next. With reduced motion
	every banner is a still picture. The words are also in the page for screen readers, since the picture
	cannot be read aloud.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { BANNERS } from './banners';
	import { reducedMotion, storyArt } from './data';

	let { id, ms = 1100 }: { id: string; ms?: number } = $props();

	const banner = $derived(BANNERS[id]);
	let frame = $state(0);
	let still = $state(false);

	onMount(() => {
		still = reducedMotion();
		if (still || !BANNERS[id]?.animated) return;
		// The frames play out over the banner's time, the last one held.
		const every = Math.max(40, (ms * 0.8) / 12);
		const timer = setInterval(() => {
			if (frame < 11) frame += 1;
			else clearInterval(timer);
		}, every);
		return () => clearInterval(timer);
	});
</script>

{#if banner}
	<div class="banner" role="status" aria-live="assertive" style:--ms="{ms}ms">
		{#if banner.animated && !still}
			<div
				class="sheet"
				aria-hidden="true"
				style:background-image="url({storyArt(`banners/${id}_sheet.webp`)})"
				style:background-position="{(frame % 4) * 33.3333}% {Math.floor(frame / 4) * 50}%"
			></div>
		{:else}
			<img class="still" src={storyArt(`banners/${id}.webp`)} alt="" draggable="false" />
		{/if}
		<span class="visually-hidden">{banner.text}</span>
	</div>
{/if}

<style>
	.banner {
		position: absolute;
		left: 50%;
		top: 13%;
		z-index: 35;
		width: min(88%, 58rem);
		transform: translateX(-50%);
		pointer-events: none;
		filter: drop-shadow(0 0.6rem 1rem rgb(0 0 0 / 0.45));
		/* in with a small bounce, held long enough to enjoy, then gently out before it is removed */
		animation:
			drop-in 480ms cubic-bezier(0.2, 0.9, 0.3, 1.15) both,
			fade-out 420ms ease-in calc(var(--ms) - 420ms) forwards;
	}
	.sheet,
	.still {
		display: block;
		width: 100%;
		aspect-ratio: 4 / 1;
	}
	.sheet {
		background-size: 400% 300%;
		background-repeat: no-repeat;
	}
	@keyframes drop-in {
		from {
			opacity: 0;
			transform: translateX(-50%) translateY(-1.2rem) scale(0.94);
		}
	}
	@keyframes fade-out {
		to {
			opacity: 0;
			transform: translateX(-50%) translateY(-0.6rem) scale(0.98);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.banner {
			animation: none;
		}
	}
</style>
