<!-- The first screen of the story: choose a hero. Two playable heroes for now, one of each. -->
<script lang="ts">
	import { HEROES, heroArt } from './data';
	import { sfx } from './sfx';

	let { onpick }: { onpick: (hero: string) => void } = $props();
	let chosen = $state<string | null>(null);

	function pick(key: string) {
		if (chosen) return;
		chosen = key;
		sfx('click');
		onpick(key);
	}
</script>

<section class="select" aria-labelledby="pilih-wira">
	<p class="kicker">Legenda · Story Mode</p>
	<h2 id="pilih-wira">Pilih wira kamu</h2>
	<p class="lead">Wira akan mengembara sendiri. Kamu jawab soalan untuk menyerang.</p>
	<div class="heroes">
		{#each HEROES as hero (hero.key)}
			<button type="button" class="hero" class:chosen={chosen === hero.key} disabled={!!chosen && chosen !== hero.key} onclick={() => pick(hero.key)}>
				<span class="art"><img src={heroArt(hero.key, 'portrait')} alt="" /></span>
				<span class="name">{hero.name}</span>
				<span class="title">{hero.title}</span>
				<span class="blurb">{hero.blurb}</span>
			</button>
		{/each}
	</div>
</section>

<style>
	.select {
		display: grid;
		justify-items: center;
		gap: 0.6rem;
		padding: 1.4rem 1rem 2rem;
		border-radius: 18px;
		background:
			radial-gradient(ellipse at 50% 0%, rgb(255 210 120 / 0.25), transparent 60%),
			linear-gradient(180deg, #13284f, #0a1530);
		color: #fff4d8;
		text-align: center;
		box-shadow: inset 0 0 0 3px #d9a441, inset 0 0 0 6px #5a3b10;
	}
	.kicker {
		font: 700 0.9rem/1 var(--font-pixel);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #ffd27a;
	}
	h2 {
		font: 700 clamp(1.8rem, 1.2rem + 2.6vw, 3rem) / 1.05 var(--font-pixel);
		color: #fff;
		text-shadow: 0 3px 0 #5a3b10;
	}
	.lead {
		max-width: 36ch;
		color: #d9e4ff;
		font-weight: 600;
	}
	.heroes {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: clamp(0.6rem, 2vw, 1.4rem);
		width: min(100%, 720px);
		margin-top: 0.6rem;
	}
	.hero {
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		padding: 0.8rem 0.6rem 1rem;
		border: 3px solid #d9a441;
		border-radius: 16px;
		background: linear-gradient(180deg, rgb(43 78 150 / 0.65), rgb(14 28 64 / 0.9));
		color: inherit;
		cursor: pointer;
		transition:
			transform 220ms var(--spring, ease),
			box-shadow 220ms;
	}
	.hero:hover:not(:disabled),
	.hero:focus-visible {
		transform: translateY(-6px);
		box-shadow: 0 0 0 4px rgb(255 210 120 / 0.5), 0 18px 30px rgb(0 0 0 / 0.35);
	}
	.hero.chosen {
		box-shadow: 0 0 0 5px #ffd27a, 0 0 40px rgb(255 210 120 / 0.6);
	}
	.hero:disabled:not(.chosen) {
		opacity: 0.45;
	}
	.art {
		display: grid;
		place-items: end center;
		width: 100%;
		aspect-ratio: 3 / 4;
		max-height: 46vh;
	}
	.art img {
		width: 100%;
		height: 100%;
		object-fit: contain;
		object-position: bottom;
		filter: drop-shadow(0 10px 14px rgb(0 0 0 / 0.45));
	}
	.hero:hover:not(:disabled) .art img {
		animation: sway 1.2s ease-in-out infinite;
	}
	.name {
		font: 700 clamp(1.2rem, 0.9rem + 1.4vw, 1.8rem) / 1.1 var(--font-pixel);
	}
	.title {
		color: #ffd27a;
		font-weight: 800;
		font-size: 0.9rem;
	}
	.blurb {
		color: #c9d6f5;
		font-size: 0.9rem;
		font-weight: 600;
	}
	@keyframes sway {
		50% {
			transform: translateY(-6px) rotate(-1.5deg);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.hero:hover:not(:disabled) .art img {
			animation: none;
		}
	}
</style>
