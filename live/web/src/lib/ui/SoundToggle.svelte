<script lang="ts">
	import { isMuted, onMuteChange, setMuted, unlock } from '$lib/sound';
	import Icon from './Icon.svelte';

	let { light = false }: { light?: boolean } = $props();
	let muted = $state(isMuted());

	$effect(() => onMuteChange((value) => (muted = value)));

	function toggle() {
		unlock();
		setMuted(!muted);
	}
</script>

<button type="button" class="btn btn--icon" class:btn--plain={!light} class:light onclick={toggle} aria-pressed={!muted} aria-label={muted ? 'Hidupkan bunyi' : 'Senyapkan bunyi'}>
	<Icon name={muted ? 'mute' : 'sound'} />
</button>

<style>
	.light {
		--c: rgb(255 255 255 / 0.18);
		--shade: rgb(0 0 0 / 0.18);
		--on: #fff;
	}
</style>
