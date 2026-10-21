<!--
	A raised bed in Kebun Ajaib, in the worlds' 3/4 view: a wooden frame with its soil seen from above,
	the crop growing on it, and along the front one drop for each watering the crop needs (filled once
	given). Land not bought yet is grass behind a dashed line. The foot is the middle of the front edge.
-->
<script lang="ts">
	import Crop from './Crop.svelte';

	let {
		crop = null,
		stage = 0,
		need = 0,
		locked = false,
		tile = 44
	}: { crop?: string | null; stage?: number; need?: number; locked?: boolean; tile?: number } = $props();

	const ready = $derived(!!crop && stage >= need);
	const grow = $derived(need ? stage / need : 0);
	// Small crops grow three to a bed; a watermelon or a durian tree takes the whole bed.
	const spots = $derived(crop === 'tembikai' || crop === 'durian' ? [[140, 150]] : [[78, 146], [202, 146], [140, 158]]);
</script>

<svg class="bed" class:ready viewBox="0 0 280 240" width={2.8 * tile} height={2.4 * tile} aria-hidden="true" focusable="false">
	<ellipse cx="140" cy="228" rx="132" ry="10" fill="#000" opacity=".15" />
	{#if locked}
		<rect x="14" y="128" width="252" height="92" rx="16" fill="#7fc152" />
		<path d="M50 170 l6 -14 l6 14 M200 150 l5 -12 l5 12 M120 196 l6 -14 l6 14" stroke="#5f9e3a" stroke-width="4" fill="none" stroke-linecap="round" />
		<rect x="14" y="128" width="252" height="92" rx="16" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="14 10" opacity=".85" />
		<rect x="116" y="150" width="48" height="40" rx="8" fill="#fff4e6" stroke="#8e5a2e" stroke-width="4" />
		<path d="M140 160 v20 M130 170 h20" stroke="#8e5a2e" stroke-width="5" stroke-linecap="round" />
	{:else}
		<rect x="14" y="168" width="252" height="56" rx="10" fill="#a46a37" />
		<path d="M18 196 H262" stroke="#8e5a2e" stroke-width="4" />
		<rect x="14" y="120" width="252" height="64" rx="14" fill="#c98a54" />
		<rect x="24" y="128" width="232" height="48" rx="10" fill="#8e5a36" />
		<path d="M40 142 H240 M40 156 H240 M40 170 H240" stroke="#6f4326" stroke-width="4" stroke-linecap="round" />
		{#if crop}
			{#each spots as [x, y] (`${x}-${y}`)}
				<Crop {crop} {x} {y} {grow} {ready} scale={spots.length > 1 ? 1.25 : 1.35} />
			{/each}
			{#if need}
				{#each Array.from({ length: need }, (_, i) => i) as i (i)}
					{@const dx = 140 + (i - (need - 1) / 2) * 26}
					<path d="M{dx} 200 q9 11 0 17 q-9 -6 0 -17z" fill={i < stage ? '#4fc3f7' : '#fff'} stroke="#2f7fcf" stroke-width="2.5" opacity={i < stage ? 1 : 0.75} />
				{/each}
			{/if}
		{/if}
		{#if ready}
			<path class="spark" d="M236 70 l5 12 12 5 -12 5 -5 12 -5 -12 -12 -5 12 -5z" fill="#fff6b0" />
			<path class="spark late" d="M44 92 l4 9 9 4 -9 4 -4 9 -4 -9 -9 -4 9 -4z" fill="#fff6b0" />
		{/if}
	{/if}
</svg>

<style>
	.bed {
		display: block;
		overflow: visible;
	}
	.spark {
		transform-box: fill-box;
		transform-origin: center;
		animation: twinkle 1.4s ease-in-out infinite;
	}
	.spark.late {
		animation-delay: 0.7s;
	}
	@keyframes twinkle {
		0%,
		100% {
			opacity: 0.2;
			transform: scale(0.6);
		}
		50% {
			opacity: 1;
			transform: scale(1.1);
		}
	}
</style>
