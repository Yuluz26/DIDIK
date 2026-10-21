<!--
	Teka Gambar beside the question on the big screen: the gallery, with everyone who has guessed
	cheering at the front and the rest of the room behind them.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { play } from '$lib/sound';
	import PictureGallery, { type Frame } from './PictureGallery.svelte';

	let { client, frame, people }: { client: RoomClient; frame: Frame; people: Map<string, Person> } = $props();

	const visitors = $derived([
		...frame.guessers,
		...[...people.values()].filter((p) => p.approved && p.online && !frame.guessers.includes(p.id)).map((p) => p.id)
	]);

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind === 'guessed') play('pop');
			else if (fx.kind === 'picture') play('key');
		})
	);
</script>

<div class="picture-side">
	<PictureGallery {frame} {people} {visitors} cheering={frame.guessers} />
	{#if frame.done && frame.name}
		<p class="answer">Gambar ini <strong>{frame.name}</strong></p>
	{:else}
		<p class="hint">Taip nama gambar di peranti kamu bila-bila masa.</p>
	{/if}
</div>

<style>
	.picture-side {
		display: grid;
		gap: 0.6rem;
	}
	.answer {
		padding: 0.6rem 0.9rem;
		border-radius: var(--r-md);
		background: var(--sun);
		font-weight: 700;
		text-align: center;
		animation: pop-in 450ms var(--spring);
	}
	.answer strong {
		font: 600 1.5rem var(--font-display);
	}
	.hint {
		color: var(--ink-2);
		font-weight: 700;
		text-align: center;
	}
</style>
