<!-- A small round window into each game's world, in pixels, used wherever a game is named. -->
<script lang="ts">
	import { snapScale } from '$lib/pixel/cache';
	import { badge } from '$lib/pixel/badges';
	import Sprite from '$lib/pixel/Sprite.svelte';

	let { world, size = 72 }: { world: string; size?: number } = $props();

	const sheet = $derived(badge(world));
	const s = $derived(snapScale(size / 40, 1));
</script>

<span class="badge" style:width="{size}px" style:height="{size}px" aria-hidden="true"><Sprite {sheet} {s} /></span>

<style>
	.badge {
		display: inline-grid;
		place-items: center;
		flex: none;
		line-height: 0;
	}
</style>
