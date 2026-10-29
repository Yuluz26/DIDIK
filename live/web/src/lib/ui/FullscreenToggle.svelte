<!--
	Full screen for the whole page, beside the sound switch on every game screen (the child's and the
	host's). Hidden where the browser cannot do it (an iPhone's Safari has no full-screen pages).
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import Icon from './Icon.svelte';

	let { light = false }: { light?: boolean } = $props();

	type Doc = Document & { webkitFullscreenElement?: Element | null; webkitExitFullscreen?: () => Promise<void>; webkitFullscreenEnabled?: boolean };
	type El = HTMLElement & { webkitRequestFullscreen?: () => Promise<void> };

	let able = $state(false);
	let full = $state(false);

	const current = () => (document as Doc).fullscreenElement ?? (document as Doc).webkitFullscreenElement ?? null;

	onMount(() => {
		const doc = document as Doc;
		able = !!(doc.fullscreenEnabled || doc.webkitFullscreenEnabled);
		const sync = () => (full = !!current());
		sync();
		document.addEventListener('fullscreenchange', sync);
		document.addEventListener('webkitfullscreenchange', sync);
		return () => {
			document.removeEventListener('fullscreenchange', sync);
			document.removeEventListener('webkitfullscreenchange', sync);
		};
	});

	async function toggle() {
		const doc = document as Doc;
		const root = document.documentElement as El;
		try {
			if (current()) await (doc.exitFullscreen?.() ?? doc.webkitExitFullscreen?.());
			else await (root.requestFullscreen?.({ navigationUI: 'hide' }) ?? root.webkitRequestFullscreen?.());
		} catch {
			/* refused (e.g. inside a frame that does not allow it): nothing changes */
		}
	}
</script>

{#if able}
	<button type="button" class="btn btn--icon" class:btn--plain={!light} class:light onclick={toggle} aria-pressed={full} aria-label={full ? 'Keluar skrin penuh' : 'Skrin penuh'} title={full ? 'Keluar skrin penuh' : 'Skrin penuh'}>
		<Icon name={full ? 'windowed' : 'fullscreen'} />
	</button>
{/if}

<style>
	.light {
		--c: rgb(255 255 255 / 0.18);
		--shade: rgb(0 0 0 / 0.18);
		--on: #fff;
	}
</style>
