<!-- Tap a sticker to send it; it floats above your animal on every screen in the room. -->
<script lang="ts">
	import StickerArt from './StickerArt.svelte';
	import { play } from '$lib/sound';

	let { onsend }: { onsend: (id: string) => void } = $props();

	const STICKERS: [string, string][] = [
		['hati', 'Hati'],
		['bintang', 'Bintang'],
		['ketawa', 'Ketawa'],
		['tepuk', 'Tepuk tangan'],
		['wah', 'Wah'],
		['ok', 'Bagus'],
		['api', 'Hebat'],
		['pelangi', 'Pelangi']
	];

	let cooling = $state(false);

	function send(id: string) {
		if (cooling) return;
		play('sticker');
		onsend(id);
		cooling = true;
		setTimeout(() => (cooling = false), 1300);
	}
</script>

<div class="bar" role="group" aria-label="Hantar stiker">
	{#each STICKERS as [id, name] (id)}
		<button type="button" class="sticker" class:cooling onclick={() => send(id)} aria-label="Hantar stiker {name}">
			<StickerArt name={id} size={34} />
		</button>
	{/each}
</div>

<style>
	.bar {
		display: grid;
		grid-template-columns: repeat(8, minmax(0, 1fr));
		justify-items: center;
		gap: 0.3rem;
		padding: 0.45rem;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	.sticker {
		display: grid;
		place-items: center;
		width: 3rem;
		height: 3rem;
		border: 0;
		border-radius: var(--r-md);
		background: transparent;
		cursor: pointer;
		transition: transform var(--t-state) var(--spring), background-color var(--t-state);
	}
	.sticker:hover {
		background: var(--paper-2);
		transform: translateY(-4px) rotate(-8deg) scale(1.12);
	}
	.sticker:active {
		transform: scale(0.88);
	}
	.cooling {
		opacity: 0.45;
	}
	@media (max-width: 460px) {
		.bar {
			grid-template-columns: repeat(4, minmax(0, 1fr));
		}
	}
</style>
