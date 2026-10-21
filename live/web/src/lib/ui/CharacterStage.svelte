<!--
	A child's character standing on a small patch of grass, as it will in the game worlds. Used where a
	child first meets their character: joining, and waiting in the lobby.
-->
<script lang="ts">
	import Chibi from './Chibi.svelte';

	let {
		animal,
		colour,
		skin,
		size = 96,
		mood = 'cheer'
	}: { animal: string; colour: string; skin?: string; size?: number; mood?: 'happy' | 'cheer' | 'oops' | 'sleep' } = $props();
</script>

<div class="stage" style:--size="{size}px" aria-hidden="true">
	<svg class="ground" viewBox="0 0 200 60" preserveAspectRatio="none">
		<ellipse cx="100" cy="34" rx="96" ry="24" fill="#bfe3a0" />
		<path d="M40 30 l3 -8 l3 8 M150 38 l3 -8 l3 8 M120 22 l2 -6 l2 6" stroke="#8fc46a" stroke-width="2.5" fill="none" stroke-linecap="round" />
	</svg>
	{#key animal + colour + skin}
		<span class="me"><Chibi {animal} {colour} {skin} {size} {mood} /></span>
	{/key}
</div>

<style>
	.stage {
		position: relative;
		display: grid;
		place-items: end center;
		width: calc(var(--size) * 2);
		height: calc(var(--size) * 1.6);
	}
	.ground {
		position: absolute;
		inset: auto 0 0;
		width: 100%;
		height: calc(var(--size) * 0.6);
	}
	.me {
		position: relative;
		display: inline-block;
		margin-bottom: calc(var(--size) * 0.18);
		animation: pop-in 480ms var(--spring);
	}
</style>
