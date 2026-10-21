<!--
	A child's Teka Gambar: the gallery with the hidden picture, and a box to type a guess at any
	moment. A wrong guess means a short wait before the next one; a right guess early, while most
	tiles are closed, earns the most.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { confetti } from '$lib/confetti';
	import { play } from '$lib/sound';
	import PictureGallery, { type Frame } from './PictureGallery.svelte';

	let { client, frame, me, people }: { client: RoomClient; frame: Frame; me: Person; people: Map<string, Person> } = $props();

	let text = $state('');
	let wrong = $state(false);
	let waiting = $state(false);
	let cooling = $state(false);
	let timer: ReturnType<typeof setTimeout> | undefined;

	const visitors = $derived([me.id, ...frame.guessers.filter((id) => id !== me.id)].slice(0, 4));

	function guess(event: SubmitEvent) {
		event.preventDefault();
		if (!text.trim() || cooling || waiting) return;
		waiting = true;
		wrong = false;
		client.send({ t: 'guess', text: text.trim() });
		clearTimeout(timer);
		timer = setTimeout(() => (waiting = false), 3000);
	}

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind === 'guess-right') {
				waiting = false;
				text = '';
				play('correct');
				confetti({ count: 90 });
			} else if (fx.kind === 'guess-wrong') {
				waiting = false;
				wrong = true;
				cooling = true;
				play('wrongGuess');
				setTimeout(() => (cooling = false), 2500);
			} else if (fx.kind === 'tiles') {
				play('tiles');
			} else if (fx.kind === 'picture') {
				play('key');
				wrong = false;
			}
		})
	);
</script>

<section class="teka">
	<PictureGallery {frame} {people} {visitors} me={me.id} cheering={frame.guessers} />

	{#if frame.guessed}
		<p class="note right">Betul, gambar ini <strong>{frame.name}</strong>! Kamu dapat {frame.bonus} mata.</p>
	{:else if frame.done}
		<p class="note">Gambar ini <strong>{frame.name}</strong>. Gambar baharu muncul pada soalan seterusnya.</p>
	{:else}
		<form class="guess" class:shake={wrong} onsubmit={guess}>
			<label for="picture-guess">Apa gambar ini?</label>
			<div class="row">
				<input
					id="picture-guess"
					bind:value={text}
					maxlength="40"
					autocomplete="off"
					autocapitalize="off"
					spellcheck="false"
					placeholder="Taip nama gambar"
					oninput={() => (wrong = false)}
				/>
				<button type="submit" class="btn btn--sun" disabled={!text.trim() || cooling || waiting}>Teka</button>
			</div>
			<p class="help" aria-live="polite">
				{#if wrong}
					Bukan itu. Tunggu sekejap, kemudian cuba lagi.
				{:else}
					Lebih awal kamu meneka, lebih banyak mata.
				{/if}
			</p>
		</form>
	{/if}
</section>

<style>
	.teka {
		display: grid;
		gap: 0.7rem;
	}
	.guess {
		display: grid;
		gap: 0.35rem;
		padding: 0.8rem 0.9rem;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	.guess.shake {
		animation: shake 420ms var(--ease-out);
	}
	label {
		font: 600 1.05rem var(--font-display);
	}
	.row {
		display: flex;
		gap: 0.5rem;
	}
	input {
		flex: 1;
		min-width: 0;
		padding: 0.6rem 0.9rem;
		border: 2px solid var(--line);
		border-radius: var(--r-sm);
		background: var(--paper);
		font: inherit;
		font-weight: 700;
	}
	input:focus-visible {
		border-color: var(--brand);
		outline: none;
	}
	.help {
		color: var(--ink-2);
		font-size: var(--fs-small);
		font-weight: 600;
	}
	.shake .help {
		color: var(--almost);
	}
	.note {
		padding: 0.7rem 0.9rem;
		border-radius: var(--r-md);
		background: var(--brand-soft);
		font-weight: 700;
	}
	.note.right {
		background: var(--good-soft);
		animation: pop-in 450ms var(--spring);
	}
</style>
