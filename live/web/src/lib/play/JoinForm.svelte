<!--
	A child joining: type their own name (or take a suggestion), pick an animal hood, a colour and a
	skin tone, and see the character they will play as. Typed names are checked on the server; a host
	can switch to suggested names only.
-->
<script lang="ts">
	import type { JoinData } from '$lib/room.svelte';
	import type { RoomInfo } from '$lib/types';
	import { ANIMALS, COLOURS, COLOUR_NAMES, SKINS, SKIN_NAMES, randomOf, suggestName } from '$lib/names';
	import { tick } from '$lib/pixel/icons';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import { play, unlock } from '$lib/sound';
	import Avatar from '$ui/Avatar.svelte';
	import CharacterStage from '$ui/CharacterStage.svelte';
	import Icon from '$ui/Icon.svelte';

	let {
		info,
		busy = false,
		error = null,
		onjoin
	}: { info: RoomInfo; busy?: boolean; error?: string | null; onjoin: (data: JoinData) => void } = $props();

	let animal = $state(randomOf(Object.keys(ANIMALS)));
	let colour = $state(randomOf(Object.keys(COLOURS)));
	let skin = $state(randomOf(Object.keys(SKINS)));
	let name = $state('');
	let typed = $state('');
	// A name of their own unless the host chose suggested names only.
	const typing = $derived(info.customNames);

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
		onjoin({ name: typing && typed.trim() ? typed.trim() : name, avatar: animal, colour, skin });
	}
</script>

<form class="join" onsubmit={submit}>
	<div class="preview">
		<CharacterStage {animal} {colour} {skin} />
		<div class="name-row">
			{#if typing}
				<div class="own">
					<label class="own-label" for="own-name">Nama kamu</label>
					<div class="own-row">
						<input
							id="own-name"
							class="input name-input"
							bind:value={typed}
							maxlength="16"
							placeholder={name}
							autocomplete="off"
							autocapitalize="words"
							enterkeyhint="go"
							aria-describedby="own-hint"
						/>
						<button
							type="button"
							class="btn btn--plain btn--icon"
							onclick={() => {
								name = suggestName(animal, name);
								typed = name;
							}}
							aria-label="Cadang nama"
						>
							<Icon name="shuffle" />
						</button>
					</div>
					<p class="own-hint" id="own-hint">Nama panggilan sahaja, 2 hingga 16 huruf. Kosongkan untuk guna “{name}”.</p>
				</div>
			{:else}
				<output class="name" aria-live="polite">{name}</output>
				<button type="button" class="btn btn--plain btn--icon" onclick={() => (name = suggestName(animal, name))} aria-label="Cadang nama lain">
					<Icon name="shuffle" />
				</button>
			{/if}
		</div>
	</div>

	<fieldset class="pick">
		<legend>Pilih haiwan kamu</legend>
		<div class="animals">
			{#each Object.entries(ANIMALS) as [key, label] (key)}
				<button type="button" class="animal" class:on={animal === key} onclick={() => chooseAnimal(key)} aria-pressed={animal === key}>
					<Avatar animal={key} {colour} {skin} size={58} />
					<span>{label}</span>
				</button>
			{/each}
		</div>
	</fieldset>

	<div class="looks">
		<fieldset class="pick">
			<legend>Warna baju</legend>
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
					>
						{#if colour === key}<Sprite sheet={tick()} s={2} />{/if}
					</button>
				{/each}
			</div>
		</fieldset>

		<fieldset class="pick">
			<legend>Warna kulit</legend>
			<div class="colours">
				{#each Object.entries(SKINS) as [key, hex] (key)}
					<button
						type="button"
						class="swatch"
						class:on={skin === key}
						style:--swatch={hex}
						onclick={() => {
							play('tap');
							skin = key;
						}}
						aria-pressed={skin === key}
						aria-label={SKIN_NAMES[key]}
					>
						{#if skin === key}<Sprite sheet={tick()} s={2} />{/if}
					</button>
				{/each}
			</div>
		</fieldset>
	</div>

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
	.name-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.name {
		font: 600 clamp(1.6rem, 1.2rem + 2vw, 2.3rem) var(--font-display);
	}
	.own {
		display: grid;
		justify-items: center;
		gap: 0.35rem;
	}
	.own-label {
		font: 600 1.1rem var(--font-display);
	}
	.own-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.name-input {
		font: 600 1.4rem var(--font-display);
		text-align: center;
		width: min(16rem, 62vw);
	}
	.own-hint {
		max-width: 22rem;
		color: var(--ink-2);
		font-size: 0.85rem;
		text-align: center;
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
	/* Chosen things lift off the page on a hard underside, the way every control in the pixel theme does. */
	.animal {
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		padding: 0.55rem 0.2rem 0.45rem;
		border: 2px solid var(--edge);
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: 0 3px 0 var(--edge);
		font-weight: 800;
		font-size: 0.85rem;
		cursor: pointer;
		transition: transform var(--t-press) steps(2), box-shadow var(--t-press) steps(2);
	}
	.animal:hover {
		transform: translateY(-2px);
		box-shadow: 0 5px 0 var(--edge);
	}
	.animal:active {
		transform: translateY(3px);
		box-shadow: 0 0 0 var(--edge);
	}
	.animal.on {
		background: var(--feed-gold);
		outline: 3px solid var(--sun);
		outline-offset: 1px;
		transform: translateY(-2px);
		box-shadow: 0 5px 0 var(--edge);
	}
	.colours {
		display: flex;
		flex-wrap: wrap;
		gap: 0.55rem;
	}
	.swatch {
		display: grid;
		place-items: center;
		width: 2.75rem;
		height: 2.75rem;
		padding: 0;
		border: 2px solid var(--edge);
		border-radius: 3px;
		background: var(--swatch);
		/* A lit top-left and a shaded bottom-right edge, then the hard underside. */
		box-shadow:
			inset 3px 3px 0 rgb(255 255 255 / 0.36),
			inset -3px -3px 0 rgb(0 0 0 / 0.16),
			0 3px 0 var(--edge);
		cursor: pointer;
		transition: transform var(--t-press) steps(2), box-shadow var(--t-press) steps(2);
	}
	.swatch:hover {
		transform: translateY(-2px);
	}
	.swatch:active {
		transform: translateY(2px);
	}
	.swatch.on {
		outline: 3px solid var(--ink);
		outline-offset: 2px;
		transform: translateY(-2px);
	}
	.looks {
		display: grid;
		gap: 1.4rem;
	}
	@media (min-width: 640px) {
		.looks {
			grid-template-columns: minmax(0, 1.6fr) minmax(0, 1fr);
		}
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
