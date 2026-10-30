<script lang="ts">
	import '@fontsource-variable/fredoka';
	import '@fontsource-variable/nunito';
	import '../app.css';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { unlock } from '$lib/sound';
	import PageLoader from '$lib/ui/PageLoader.svelte';
	import { hidePreloader, isGamePath } from '$lib/ui/preloader';
	import { guardContent } from '$lib/ui/guard';

	let { children } = $props();

	// The app is up: the page's preloader (app.html) can go. From now on the art cannot be saved or
	// dragged out and the page cannot be copied, except what is typed into a field.
	onMount(() => {
		void hidePreloader();
		return guardContent();
	});

	// A game's own screens, and the front page that leads to them, get the pixel look (app.css).
	$effect(() => {
		const path = page.url.pathname;
		if (path === '/' || /^\/(hos|m)(\/|$)/.test(path)) document.documentElement.dataset.ui = 'pixel';
		else delete document.documentElement.dataset.ui;
		return () => delete document.documentElement.dataset.ui;
	});
</script>

<!-- Browsers only allow sound after a first tap; any tap anywhere unlocks it. -->
<svelte:window onpointerdown={unlock} onkeydown={unlock} />

{#if !isGamePath(page.url.pathname)}<PageLoader />{/if}

{@render children()}
