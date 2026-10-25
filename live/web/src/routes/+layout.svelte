<script lang="ts">
	import '@fontsource-variable/fredoka';
	import '@fontsource-variable/nunito';
	import '@fontsource-variable/pixelify-sans';
	import '../app.css';
	import { unlock } from '$lib/sound';

	let { children } = $props();
</script>

<!-- Browsers only allow sound after a first tap; any tap anywhere unlocks it. -->
<svelte:window onpointerdown={unlock} onkeydown={unlock} />

{@render children()}
