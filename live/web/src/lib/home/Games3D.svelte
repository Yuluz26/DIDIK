<!--
	The front page at dusk: the four 3D games. The sun sets over the beach above, and the section is lit
	like their worlds. Choosing a game in the list shows a real frame from it on the screen beside the
	list. Like the eight island games, any of them can be played with any quiz, by any class.
-->
<script lang="ts">
	import { duskSky } from '$lib/pixel/sea';
	import { reveal } from './reveal';

	const sky = `url(${duskSky().toURL(1)})`;

	const GAMES = [
		{
			key: 'litar',
			title: 'Litar Kart',
			pace: 'Semua menjawab serentak',
			line: 'Tiga pusingan litar. Jawapan betul dan pantas memecut kart; tiga betul berturut-turut menyalakan nitro.',
			alt: 'Kart pemain melintasi garisan penamat di litar pada waktu senja, dilihat dari belakang sebuah kart.'
		},
		{
			key: 'penalti',
			title: 'Sepakan Penalti',
			pace: 'Dua pasukan',
			line: 'Harimau lawan Penyu. Pasukan yang lebih ramai menjawab betul menjaringkan gol; yang kurang, diselamatkan penjaga gol.',
			alt: 'Stadium pada waktu malam: penyepak baru menendang bola dan penjaga gol terjun ke tepi gawang.'
		},
		{
			key: 'lanun',
			title: 'Peti Lanun',
			pace: 'Ikut kadar sendiri',
			line: 'Setiap jawapan betul membuka satu daripada tiga peti: emas, ganda dua, atau peluang merampas emas kapal lain.',
			alt: 'Kapal-kapal lanun di teluk ketika matahari terbenam, dengan longgokan emas di atas geladak.'
		},
		{
			key: 'menara',
			title: 'Menara 118',
			pace: 'Seisi kelas bersama',
			line: 'Setiap blok yang diletakkan menaikkan menara kelas ke arah ketinggian Merdeka 118, melepasi Komtar dan Petronas.',
			alt: 'Menara kelas berwarna-warni hampir siap di tengah bandar, di sebelah Komtar, Menara Kuala Lumpur dan Menara Berkembar Petronas.'
		}
	];

	let shown = $state('litar');
</script>

<section id="dunia-3d" class="dusk" style:--sky={sky} aria-labelledby="dunia-3d-tajuk">
	<div class="wrap grid">
		<div class="copy" {@attach reveal()}>
			<h2 id="dunia-3d-tajuk">Empat permainan dalam 3D</h2>
			<p class="lead">Kuiz yang sama, dalam dunia 3D: litar kart, stadium, kapal lanun dan menara setinggi Merdeka 118. Pemain menjawab di telefon; dunianya bergerak di skrin besar.</p>
			<ol class="games">
				{#each GAMES as game, i (game.key)}
					<li>
						<button
							type="button"
							class="game"
							aria-pressed={shown === game.key}
							onclick={() => (shown = game.key)}
							onpointerenter={() => (shown = game.key)}
							onfocus={() => (shown = game.key)}
						>
							<span class="num">{String(i + 1).padStart(2, '0')}</span>
							<span class="text">
								<span class="title">{game.title}</span>
								<span class="pace">{game.pace}</span>
								<span class="line">{game.line}</span>
							</span>
						</button>
					</li>
				{/each}
			</ol>
			<p class="where">Pilih mana-mana daripada dua belas permainan untuk kuiz apa pun.</p>
		</div>
		<figure class="screen" {@attach reveal(120)}>
			<div class="frames">
				{#each GAMES as game (game.key)}
					<img
						src="/dunia-3d/{game.key}.webp"
						alt={game.alt}
						class:on={shown === game.key}
						aria-hidden={shown !== game.key}
						width="1200"
						height="900"
						loading="lazy"
						decoding="async"
					/>
				{/each}
			</div>
			<figcaption>Gambar sebenar dari permainan: {GAMES.find((g) => g.key === shown)?.title}.</figcaption>
		</figure>
	</div>
</section>

<style>
	/* The beach's sand turning to sunset, then to the evening the 3D worlds are lit by: bands of
	   colour whose edges are dithered, with a few stars, painted in lib/pixel/sea.ts. */
	.dusk {
		--ink: #f3efe6;
		--ink-2: #bccac7;
		--brand-ink: #5cc795;
		color: var(--ink);
		background: #0f1f24 var(--sky) 0 0 / calc(var(--px) * 96) calc(var(--px) * 88) repeat-x;
		image-rendering: pixelated;
	}
	.dusk > * {
		image-rendering: auto;
	}
	.grid {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr);
		gap: 2.5rem 4rem;
		align-items: start;
		padding-block: 16rem 6rem;
	}
	.copy {
		display: grid;
		gap: 1rem;
	}
	h2 {
		font-size: var(--fs-h1);
	}
	.lead {
		font-size: var(--fs-lead);
		color: var(--ink-2);
		max-width: 30rem;
	}
	.games {
		display: grid;
		margin: 0.6rem 0 0;
		padding: 0;
		list-style: none;
		border-top: 1px solid rgb(255 255 255 / 0.12);
	}
	.games li {
		border-bottom: 1px solid rgb(255 255 255 / 0.12);
	}
	.game {
		display: grid;
		grid-template-columns: 2.6rem minmax(0, 1fr);
		gap: 0.8rem;
		width: 100%;
		padding: 1rem 0.4rem 1rem 0;
		border: 0;
		background: transparent;
		color: inherit;
		text-align: left;
		cursor: pointer;
	}
	.game:focus-visible {
		outline: 3px solid var(--sun);
		outline-offset: 2px;
	}
	.num {
		padding-top: 0.2rem;
		color: var(--ink-2);
		font: 600 1rem var(--font-display);
		font-variant-numeric: tabular-nums;
		transition: color var(--t-state);
	}
	.text {
		display: grid;
		gap: 0.15rem;
	}
	.title {
		font: 600 1.45rem/1.15 var(--font-display);
		transition: color var(--t-state);
	}
	.pace {
		color: var(--brand-ink);
		font-size: 0.9rem;
		font-weight: 800;
	}
	/* The line opens under the chosen game only, so the list stays short. */
	.line {
		display: none;
		margin-top: 0.3rem;
		color: var(--ink-2);
		max-width: 30rem;
	}
	.game[aria-pressed='true'] .line {
		display: block;
		animation: rise-in var(--t-enter) var(--ease-out);
	}
	.game[aria-pressed='true'] .num,
	.game[aria-pressed='true'] .title,
	.game:hover .title {
		color: var(--sun);
	}
	.where {
		color: var(--ink-2);
		font-size: 0.95rem;
	}
	.screen {
		position: sticky;
		top: 6rem;
		display: grid;
		gap: 0.7rem;
		margin: 0;
	}
	.frames {
		position: relative;
		aspect-ratio: 4 / 3;
		border: 2px solid #071418;
		border-radius: var(--r-md);
		overflow: hidden;
		background: #13303d;
		box-shadow: 0 4px 0 #071418;
	}
	.frames img {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
		opacity: 0;
		transition: opacity 240ms steps(4);
	}
	.frames img.on {
		opacity: 1;
	}
	figcaption {
		color: var(--ink-2);
		font-size: 0.875rem;
		font-weight: 700;
	}
	/* A phone or tablet: the heading, then the picture, then the list to choose from. */
	@media (max-width: 900px) {
		.grid {
			grid-template-columns: minmax(0, 1fr);
			gap: 1rem;
			padding-block: 16rem 4rem;
		}
		.copy {
			display: contents;
		}
		.screen {
			position: static;
			order: 1;
			margin-block: 0.6rem;
		}
		.games,
		.where {
			order: 2;
		}
	}
	/* On a phone the sky is a third smaller, and so is the room it needs. */
	@media (max-width: 700px) {
		.grid {
			padding-block: 14rem 4rem;
		}
	}
</style>
