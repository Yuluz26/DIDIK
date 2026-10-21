<!--
	A child joining: pick an animal, a colour, and a suggested nickname. No typing needed, no real
	name asked for. A host can allow typed nicknames; those are checked on the server.
-->
<script lang="ts">
	import type { RoomInfo } from '$lib/types';
	import { ANIMALS, COLOURS, COLOUR_NAMES, randomOf, suggestName } from '$lib/names';
	import { play, unlock } from '$lib/sound';
	import Avatar from '$ui/Avatar.svelte';
	import Icon from '$ui/Icon.svelte';

	let {
		info,
		busy = false,
		error = null,
		onjoin
	}: { info: RoomInfo; busy?: boolean; error?: string | null; onjoin: (data: { name: string; avatar: string; colour: string }) => void } = $props();

	let animal = $state(randomOf(Object.keys(ANIMALS)));
	let colour = $state(randomOf(Object.keys(COLOURS)));
	let name = $state('');
	let typing = $state(false);
	let typed = $state('');

	$effect(() => {
		// A fresh suggestion that matches the chosen animal.
		name = suggestName(animal);
	});

	function chooseAnimal(key: string) {
		play('pop');
		animal = key;
	}

	function submit(event: Event) {
		event.preventDefault();
		unlock();
		play('join');
		onjoin({ name: typing && typed.trim() ? typed.trim() : name, avatar: animal, colour });
	}
</script>

<form class="join" onsubmit={submit}>
	<div class="preview">
		{#key animal + colour}
			<span class="me"><Avatar {animal} {colour} size={124} mood="cheer" /></span>
		{/key}
		<div class="name-row">
			{#if typing}
				<label class="visually-hidden" for="own-name">Nama kamu</label>
				<input id="own-name" class="input name-input" bind:value={typed} maxlength="16" placeholder="Nama samaran" autocomplete="off" />
			{:else}
				<output class="name" aria-live="polite">{name}</output>
				<button type="button" class="btn btn--plain btn--icon" onclick={() => (name = suggestName(animal, name))} aria-label="Cadang nama lain">
					<Icon name="shuffle" />
				</button>
			{/if}
		</div>
		{#if info.customNames}
			<button type="button" class="btn btn--ghost" onclick={() => (typing = !typing)}>
				{typing ? 'Guna nama cadangan' : 'Tulis nama sendiri'}
			</button>
		{/if}
	</div>

	<fieldset class="pick">
		<legend>Pilih haiwan kamu</legend>
		<div class="animals">
			{#each Object.entries(ANIMALS) as [key, label] (key)}
				<button type="button" class="animal" class:on={animal === key} onclick={() => chooseAnimal(key)} aria-pressed={animal === key}>
					<Avatar animal={key} {colour} size={58} />
					<span>{label}</span>
				</button>
			{/each}
		</div>
	</fieldset>

	<fieldset class="pick">
		<legend>Pilih warna</legend>
		<div class="colours">
			{#each Object.entries(COLOURS) as [key, hex] (key)}
				<button
					type="button"
					class="swatch"
					class:on={colour === key}
					style:--swatch={hex}
					onclick={() => {
						play('tap');
						colour = key;
					}}
					aria-pressed={colour === key}
					aria-label={COLOUR_NAMES[key]}
				></button>
			{/each}
		</div>
	</fieldset>

	{#if error}<p class="error" role="alert">{error}</p>{/if}
	{#if !info.accepting}<p class="error" role="alert">{info.reason}</p>{/if}

	<button class="btn btn--sun btn--big go" disabled={busy || !info.accepting}>
		{busy ? 'Masuk…' : 'Masuk bilik'} <Icon name="next" />
	</button>
</form>

<style>
	.join {
		display: grid;
		gap: 1.4rem;
	}
	.preview {
		display: grid;
		justify-items: center;
		gap: 0.6rem;
	}
	.me {
		display: inline-block;
		animation: pop-in 480ms var(--spring);
	}
	.name-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.name {
		font: 600 clamp(1.6rem, 1.2rem + 2vw, 2.3rem) var(--font-display);
	}
	.name-input {
		font: 600 1.4rem var(--font-display);
		text-align: center;
		max-width: 16rem;
	}
	.pick {
		margin: 0;
		padding: 0;
		border: 0;
		min-width: 0;
	}
	legend {
		margin-bottom: 0.6rem;
		font: 600 1.15rem var(--font-display);
	}
	.animals {
		display: grid;
		grid-template-columns: repeat(4, minmax(0, 1fr));
		gap: 0.5rem;
	}
	.animal {
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		padding: 0.55rem 0.2rem 0.45rem;
		border: 3px solid transparent;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: 0 3px 0 var(--line);
		font-weight: 800;
		font-size: 0.85rem;
		cursor: pointer;
		transition: transform var(--t-state) var(--spring), border-color var(--t-state);
	}
	.animal:hover {
		transform: translateY(-3px) rotate(-2deg);
	}
	.animal:hover :global(svg) {
		animation: wiggle 0.5s ease-in-out;
	}
	.animal.on {
		border-color: var(--ink);
		background: #fff3cf;
		transform: scale(1.04);
	}
	.colours {
		display: flex;
		flex-wrap: wrap;
		gap: 0.55rem;
	}
	.swatch {
		width: 2.9rem;
		height: 2.9rem;
		border: 4px solid #fff;
		border-radius: 50%;
		background: var(--swatch);
		box-shadow: 0 3px 0 var(--line);
		cursor: pointer;
		transition: transform var(--t-state) var(--spring);
	}
	.swatch:hover {
		transform: scale(1.12);
	}
	.swatch.on {
		outline: 3px solid var(--ink);
		outline-offset: 2px;
		transform: scale(1.1);
	}
	.error {
		padding: 0.7rem 1rem;
		border-radius: var(--r-md);
		background: var(--almost-soft);
		color: #7a3d00;
		font-weight: 800;
	}
	.go {
		width: 100%;
	}
	@media (max-width: 360px) {
		.animals {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}
</style>
