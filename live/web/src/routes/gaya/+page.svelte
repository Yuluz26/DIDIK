<!-- Art sheet: every character and prop on one page, for reviewing the look. Not linked from the app. -->
<script lang="ts">
	import { ANIMALS, COLOURS, SKINS } from '$lib/names';
	import Chibi from '$ui/Chibi.svelte';

	const animals = Object.keys(ANIMALS);
	const colours = Object.keys(COLOURS);
	const skins = Object.keys(SKINS);
</script>

<svelte:head><title>Gaya seni · DIDIK Main Bersama</title></svelte:head>

<main class="wrap sheet">
	<h1>Watak</h1>
	<div class="row">
		{#each animals as animal, i (animal)}
			<figure><Chibi {animal} colour={colours[i % colours.length]} skin={skins[i % skins.length]} size={110} /><figcaption>{ANIMALS[animal]}</figcaption></figure>
		{/each}
	</div>
	<h2>Mood dan berjalan</h2>
	<div class="row">
		<figure><Chibi animal="harimau" colour="biru" mood="cheer" size={110} /><figcaption>cheer</figcaption></figure>
		<figure><Chibi animal="penyu" colour="jambu" mood="oops" size={110} /><figcaption>oops</figcaption></figure>
		<figure><Chibi animal="arnab" colour="ungu" mood="sleep" size={110} /><figcaption>sleep</figcaption></figure>
		<figure><Chibi animal="gajah" colour="kuning" walking size={110} /><figcaption>walking</figcaption></figure>
		<figure><Chibi animal="kucing" colour="teal" walking facing={-1} size={110} /><figcaption>walking left</figcaption></figure>
	</div>
	<h2>Warna kulit</h2>
	<div class="row">
		{#each skins as skin (skin)}
			<figure><Chibi animal="kancil" colour="hijau" {skin} size={90} /><figcaption>{skin}</figcaption></figure>
		{/each}
	</div>
</main>

<style>
	.sheet {
		display: grid;
		gap: 1rem;
		padding-block: 2rem 4rem;
	}
	.row {
		display: flex;
		flex-wrap: wrap;
		gap: 1.2rem;
		padding: 1.2rem;
		border-radius: var(--r-lg);
		background: #8fd05e;
	}
	figure {
		display: grid;
		justify-items: center;
		margin: 0;
	}
	figcaption {
		font-weight: 800;
	}
</style>
