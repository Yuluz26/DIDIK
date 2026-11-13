<!--
	A picture from the subject games' library (assets.ts), by its key. It keeps its room while it loads
	(its size is known), loads only when near the screen unless `eager`, cannot be dragged out, and if it
	is not in the library or fails to load, the `fallback` is shown instead (a sticker, a label) so a game
	never has a hole in it. Decorative unless given `alt`.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { asset } from './assets';

	let {
		name,
		alt = '',
		eager = false,
		fit = 'contain',
		class: klass = '',
		fallback
	}: {
		name: string | null | undefined;
		alt?: string;
		eager?: boolean;
		fit?: 'contain' | 'cover';
		class?: string;
		fallback?: Snippet;
	} = $props();

	const a = $derived(asset(name));
	let failed = $state<string | null>(null);
</script>

{#if a && failed !== a.key}
	<img
		class="g-img {klass}"
		src={a.src}
		width={a.w}
		height={a.h}
		{alt}
		loading={eager ? 'eager' : 'lazy'}
		decoding="async"
		draggable="false"
		style:object-fit={fit}
		onerror={() => (failed = a.key)}
	/>
{:else if fallback}
	{@render fallback()}
{/if}

<style>
	.g-img {
		display: block;
		max-width: 100%;
		height: auto;
		user-select: none;
		-webkit-user-drag: none;
		-webkit-touch-callout: none;
		pointer-events: none;
	}
</style>
