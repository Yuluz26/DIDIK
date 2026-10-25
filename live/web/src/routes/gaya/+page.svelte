<!-- Art sheet: every character, prop, badge, sticker and icon on one page, for reviewing the look. Not linked from the app. -->
<script lang="ts">
	import { ANIMALS, COLOURS, SKINS } from '$lib/names';
	import { GLYPH_NAMES } from '$lib/pixel/glyphs';
	import { PROP_KINDS } from '$lib/pixel/props';
	import Prop from '$lib/worlds/Prop.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';
	import Chibi from '$ui/Chibi.svelte';
	import Didi from '$ui/Didi.svelte';
	import Icon from '$ui/Icon.svelte';
	import StickerArt from '$ui/StickerArt.svelte';

	const WORLDS = ['sungai', 'kolam', 'pulau', 'hutan', 'peta', 'kampung', 'galeri', 'kebun', 'litar', 'stadium', 'lanun', 'menara'];
	const MOODS = ['happy', 'cheer', 'think', 'hint', 'wave'] as const;
	const STICKERS = ['hati', 'bintang', 'ketawa', 'tepuk', 'wah', 'ok', 'api', 'pelangi'];

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
	<h2>Didi</h2>
	<div class="row">
		{#each MOODS as mood (mood)}
			<figure><Didi {mood} size={110} /><figcaption>{mood}</figcaption></figure>
		{/each}
	</div>
	<h2>Prop</h2>
	<div class="row">
		{#each PROP_KINDS as kind (kind)}
			<figure><Prop {kind} tile={32} /><figcaption>{kind}</figcaption></figure>
		{/each}
	</div>
	<h2>Lencana dunia</h2>
	<div class="row">
		{#each WORLDS as world (world)}
			<figure><WorldBadge {world} size={80} /><figcaption>{world}</figcaption></figure>
		{/each}
	</div>
	<h2>Pelekat</h2>
	<div class="row">
		{#each STICKERS as sticker (sticker)}
			<figure><StickerArt name={sticker} size={64} /><figcaption>{sticker}</figcaption></figure>
		{/each}
	</div>
	<h2>Ikon</h2>
	<div class="row ink">
		{#each GLYPH_NAMES as name (name)}
			<figure><Icon {name} size={33} /><figcaption>{name}</figcaption></figure>
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
	.ink {
		background: var(--paper-2);
		color: var(--ink);
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
