<!--
	Under the front page's Kuiz Interaktif cloud: the four kinds a parent picks from when opening a room
	(lib/interaktifKinds.ts). Each card has a picture of its world (the solar system, A Famosa, the Kaabah,
	or the general kind's candy colours) with its stickers on it, what a child does there, and the names of
	its games. The photographs are from Wikimedia Commons, credited in static/rajah/CREDITS.txt.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import { diagramUrl } from '$lib/diagrams';
	import { INTERAKTIF_KINDS, kindGames } from '$lib/interaktifKinds';
	import { reveal } from './reveal';

	// where each photograph is cropped, so its subject stays in the banner
	const FOCUS: Record<string, string> = { 'rajah-suria': '42% 50%', 'rajah-afamosa': '50% 42%', 'rajah-kaabah': '50% 62%' };
</script>

<div class="kinds-row">
	<header {@attach reveal()}>
		<h3 id="jenis-interaktif">Empat jenis Kuiz Interaktif</h3>
		<p>Mana-mana kuiz boleh dimainkan dalam keempat-empatnya. Ibu bapa dan guru memilih jenisnya semasa membuka bilik.</p>
	</header>
	<ul class="cards">
		{#each INTERAKTIF_KINDS as kind, i (kind.key)}
			{@const games = kindGames(kind)}
			<li class="card" style:--tint={kind.tint} style:--kind-ink={kind.ink} {@attach reveal(80 * i)}>
				<div class="banner" class:photo={!!kind.photo}>
					{#if kind.photo}
						<img src={diagramUrl(kind.photo)} alt="" loading="lazy" decoding="async" style:object-position={FOCUS[kind.photo] ?? '50% 50%'} />
					{/if}
					<span class="stickers" aria-hidden="true">
						{#each kind.stickers as s, k (s)}<span class="st" style:--d="{k * 0.5 + i * 0.3}s"><Sticker key={s} size={k === 1 ? 62 : 48} alt="" /></span>{/each}
					</span>
				</div>
				<div class="body">
					<p class="kicker">{kind.kicker}</p>
					<h4>{kind.name}</h4>
					<p class="line">{kind.line}</p>
					{#if games.length}
						<p class="games"><strong>{games.length} permainan:</strong> {games.map((g) => g.title).join(' · ')}</p>
					{:else}
						<p class="games"><strong>Setiap jenis soalan</strong> mempunyai permainan sentuhnya sendiri.</p>
					{/if}
				</div>
			</li>
		{/each}
	</ul>
</div>

<style>
	.kinds-row {
		display: grid;
		gap: 1.2rem;
		margin-top: clamp(2rem, 4vw, 3rem);
	}
	header {
		display: grid;
		gap: 0.35rem;
		max-width: 40rem;
		color: #fff;
	}
	h3 {
		font: 600 clamp(1.5rem, 1.1rem + 1.6vw, 2.2rem) / 1.1 'Fredoka Variable', ui-rounded, sans-serif;
		text-shadow: 0 3px 0 rgb(10 40 80 / 0.35);
	}
	header p {
		color: rgb(255 255 255 / 0.9);
		font-size: var(--fs-lead);
	}
	.cards {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(min(100%, 15.5rem), 1fr));
		gap: 1rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.card {
		display: grid;
		grid-template-rows: auto 1fr;
		overflow: hidden;
		border-radius: 28px;
		background: var(--tint);
		box-shadow:
			0 8px 0 rgb(255 255 255 / 0.45),
			0 22px 40px rgb(10 40 80 / 0.3);
	}
	.banner {
		position: relative;
		height: 8.5rem;
		overflow: hidden;
		/* the general kind's banner: Didi's candy sky with a few soft bubbles */
		background:
			radial-gradient(circle at 72% 28%, rgb(255 255 255 / 0.55) 0 7%, transparent 7.5%),
			radial-gradient(circle at 86% 58%, rgb(255 255 255 / 0.4) 0 4%, transparent 4.5%),
			radial-gradient(circle at 58% 70%, rgb(255 255 255 / 0.35) 0 3%, transparent 3.5%),
			radial-gradient(circle at 85% 12%, rgb(255 236 160 / 0.9), transparent 32%),
			linear-gradient(160deg, #ffd3e8, #e2d4ff 55%, #cfeeff);
	}
	.banner img {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
	/* a soft shade at the bottom of a photograph, so the stickers stand out */
	.banner.photo::after {
		content: '';
		position: absolute;
		inset: 0;
		background: linear-gradient(180deg, transparent 35%, rgb(10 20 40 / 0.55));
		pointer-events: none;
	}
	.stickers {
		position: absolute;
		z-index: 1;
		left: 0.8rem;
		bottom: 0.5rem;
		display: flex;
		align-items: flex-end;
		gap: 0.15rem;
	}
	.st {
		filter: drop-shadow(0 6px 6px rgb(10 20 40 / 0.35));
		animation: bob 3.6s ease-in-out infinite;
		animation-delay: var(--d);
	}
	@keyframes bob {
		50% {
			transform: translateY(-6px) rotate(-4deg);
		}
	}
	.body {
		display: grid;
		align-content: start;
		gap: 0.3rem;
		padding: 0.9rem 1.1rem 1.2rem;
		color: #3a3350;
	}
	.kicker {
		color: var(--kind-ink);
		font: 600 0.74rem/1.2 var(--font-display);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}
	h4 {
		color: #2c2340;
		font: 600 1.45rem/1.1 'Fredoka Variable', ui-rounded, sans-serif;
	}
	.line {
		font-size: 0.95rem;
		line-height: 1.4;
	}
	.games {
		margin-top: 0.2rem;
		padding-top: 0.5rem;
		border-top: 2px dashed rgb(0 0 0 / 0.08);
		color: #5b5272;
		font-size: 0.82rem;
		line-height: 1.45;
	}
	.games strong {
		color: var(--kind-ink);
	}
	/* On a phone the four cards are a row to swipe through, the next one peeking in at the edge, rather
	   than four screens of scrolling. */
	@media (max-width: 640px) {
		.cards {
			display: flex;
			gap: 0.8rem;
			margin-inline: calc(-1 * var(--gutter)) calc(-1 * var(--gutter-r));
			padding: 0.2rem var(--gutter-r) 2.2rem var(--gutter);
			overflow-x: auto;
			overscroll-behavior-x: contain;
			scroll-snap-type: x mandatory;
			scroll-padding-inline: var(--gutter) var(--gutter-r);
			scrollbar-width: none;
		}
		.cards::-webkit-scrollbar {
			display: none;
		}
		.card {
			flex: 0 0 82%;
			scroll-snap-align: start;
		}
		.banner {
			height: 7.5rem;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.st {
			animation: none;
		}
	}
</style>
