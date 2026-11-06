<!--
	The three kinds of game, side by side under the front page's hero, each a ticket to its own section
	further down: Kuiz Interaktif, the 2D islands, and Hikayat (the story mode).
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import { reveal } from './reveal';

	const WAYS = [
		{ href: '#interaktif', sticker: 'bintang-bersinar', name: 'Kuiz Interaktif', line: 'Umum, Sains, Sejarah dan Pendidikan Islam. Baharu!', tone: 'pink' },
		{ href: '#pulau', sticker: 'bot', name: 'Permainan 2D', line: 'Empat belas pulau pixel bersama kawan.', tone: 'sea' },
		{ href: '#hikayat', sticker: 'mahkota', name: 'Story Mode', line: 'Hikayat Lima Alam: wira lawan boss.', tone: 'violet' }
	];
</script>

<nav class="ways wrap" aria-label="Tiga cara bermain">
	<p class="head" {@attach reveal()}>Tiga cara bermain dengan satu kuiz</p>
	<ul>
		{#each WAYS as way, i (way.href)}
			<li {@attach reveal(80 * i)}>
				<a class="way tone-{way.tone}" href={way.href}>
					<span class="art"><Sticker key={way.sticker} size={52} alt="" /></span>
					<span class="words"><strong>{way.name}</strong><span>{way.line}</span></span>
				</a>
			</li>
		{/each}
	</ul>
</nav>

<style>
	.ways {
		position: relative;
		z-index: 1;
		display: grid;
		gap: 0.8rem;
		padding-block: 0 1.5rem;
	}
	.head {
		font: 600 var(--fs-h2) var(--font-display);
		color: var(--on-sea);
	}
	ul {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 0.9rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.way {
		display: flex;
		align-items: center;
		gap: 0.8rem;
		height: 100%;
		padding: 0.8rem 1rem 0.8rem 0.8rem;
		border: 2px solid var(--edge);
		border-radius: var(--r-lg);
		background: var(--paper);
		color: var(--ink);
		text-decoration: none;
		box-shadow: 0 4px 0 var(--edge);
		transition: transform var(--t-press) steps(2);
	}
	.way:hover {
		transform: translateY(-3px);
		box-shadow: 0 7px 0 var(--edge);
	}
	.way:active {
		transform: translateY(3px);
		box-shadow: none;
	}
	.tone-pink {
		background: linear-gradient(135deg, #ffe3f0, #f0e6ff);
	}
	.tone-sea {
		background: linear-gradient(135deg, #dff6ff, #e6fbe8);
	}
	.tone-violet {
		background: linear-gradient(135deg, #efe6ff, #e2e6ff);
	}
	.art {
		display: grid;
		place-items: center;
		flex: none;
		width: 3.6rem;
		height: 3.6rem;
		border-radius: 50%;
		background: #fff;
	}
	.words {
		display: grid;
		gap: 0.1rem;
		line-height: 1.25;
	}
	.words strong {
		font: 600 1.15rem var(--font-display);
	}
	.words span {
		color: var(--ink-2);
		font-size: 0.92rem;
		font-weight: 700;
	}
	@media (max-width: 860px) {
		ul {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
