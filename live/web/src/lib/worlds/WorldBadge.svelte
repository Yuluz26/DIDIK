<!-- A small round window into each game's world, in pixels, used wherever a game is named. Legenda uses
	its own painted emblem, Kuiz Interaktif a 3D sticker. -->
<script lang="ts">
	import { storyArt } from '$lib/games/legenda/data';
	import { snapScale } from '$lib/pixel/cache';
	import { badge } from '$lib/pixel/badges';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Sticker from '$ui/Sticker.svelte';

	let { world, size = 72 }: { world: string; size?: number } = $props();

	const sheet = $derived(badge(world));
	const s = $derived(snapScale(size / 40, 1));
</script>

<span class="badge" style:width="{size}px" style:height="{size}px" aria-hidden="true">
	{#if world === 'legenda'}<img src={storyArt(`ui/symbol_chini.webp`)} alt="" width={size} height={size} />{:else if world === 'interaktif'}<Sticker key="bintang-bersinar" size={Math.round(size * 0.9)} alt="" />{:else}<Sprite {sheet} {s} />{/if}
</span>

<style>
	.badge {
		display: inline-grid;
		place-items: center;
		flex: none;
		line-height: 0;
	}
</style>
