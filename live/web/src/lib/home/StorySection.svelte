<!--
	The front page's Hikayat Lima Alam section (the story mode), a slideshow of the five worlds. Each slide is one
	world: its battlefield painting with the hero facing the world's boss (its introduction portrait, as
	the game shows it, rising in its own glow), its name, its story line, the
	boss and the element it fears. The slides move on every few seconds (a bar on the world's chip
	shows how long is left); arrows, the chips, a swipe or the arrow keys change slide, and a button
	pauses it. With reduced motion it starts paused and slides without moving. Only the shown painting
	and its neighbours are loaded, and nothing until the section comes near the screen.
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import { ELEMENTS, ELEMENT_NAME, battleBg, elementIcon, heroWeaponArt, introArt, introFlip, symbol, type Element } from '$lib/games/legenda/data';

	const WORLDS: { key: string; name: string; boss: string; intro: string; weak: Element; hero: 'tuah' | 'mahsuri'; weapon: Element; aura: string }[] = [
		{ key: 'chini', name: 'Tasik Chini', boss: 'Naga Chini', intro: 'Kabus pagi menyelubungi tasik teratai. Di dasarnya, Naga Chini menjaga rahsia lama.', weak: 'petir', hero: 'tuah', weapon: 'air', aura: '#38d6c8' },
		{ key: 'lupar', name: 'Batang Lupar', boss: 'Bujang Senang', intro: 'Senja di sungai Sarawak. Rumah panjang terdiam; sang buaya legenda sedang menunggu.', weak: 'api', hero: 'mahsuri', weapon: 'api', aura: '#ff8a3d' },
		{ key: 'larut', name: 'Hutan Larut', boss: 'Gajah Rimba', intro: 'Hutan hujan yang tua dan tebal. Langkah Gajah Rimba menggegarkan denai.', weak: 'angin', hero: 'tuah', weapon: 'angin', aura: '#9ad66a' },
		{ key: 'kancil', name: 'Rimba Bayangan', boss: 'Sang Kancil Bayangan', intro: 'Bulan ungu di atas rimba. Sang Kancil Bayangan menguji akal sesiapa yang lalu.', weak: 'tanah', hero: 'mahsuri', weapon: 'tanah', aura: '#b07cff' },
		{ key: 'ledang', name: 'Gunung Ledang', boss: 'Penunggu Kabus', intro: 'Jambatan batu di puncak berkabus. Penunggu Kabus menanti ujian terakhir.', weak: 'air', hero: 'tuah', weapon: 'petir', aura: '#dcecff' }
	];
	const N = WORLDS.length;
	const EVERY = 3500;

	let shown = $state(0);
	// which way the last change went, so the new painting comes in from that side
	let way = $state(1);
	let paused = $state(false);
	let focused = $state(false);
	let hidden = $state(false);
	let still = $state(false);
	let seen = $state(false);
	let section = $state<HTMLElement>();
	// bumps on every change, so the timer and the chip's bar start again
	let turn = $state(0);

	const world = $derived(WORLDS[shown]);
	const near = $derived(new Set([shown, (shown + 1) % N, (shown + N - 1) % N]));
	const playing = $derived(seen && !paused && !focused && !hidden);

	function go(to: number, direction = to > shown ? 1 : -1) {
		way = direction;
		shown = (to + N) % N;
		turn++;
	}
	const next = () => go(shown + 1, 1);
	const prev = () => go(shown - 1, -1);

	$effect(() => {
		still = matchMedia('(prefers-reduced-motion: reduce)').matches;
		if (still) paused = true;
		const onVisibility = () => (hidden = document.hidden);
		document.addEventListener('visibilitychange', onVisibility);
		return () => document.removeEventListener('visibilitychange', onVisibility);
	});

	// Nothing is fetched until the section comes near the screen.
	$effect(() => {
		if (!section || !('IntersectionObserver' in window)) {
			seen = true;
			return;
		}
		const watch = new IntersectionObserver(([entry]) => entry.isIntersecting && ((seen = true), watch.disconnect()), { rootMargin: '300px' });
		watch.observe(section);
		return () => watch.disconnect();
	});

	$effect(() => {
		void turn;
		if (!playing) return;
		const timer = setTimeout(next, EVERY);
		return () => clearTimeout(timer);
	});

	// a swipe across the painting changes slide
	let downX: number | null = null;
	function down(event: PointerEvent) {
		downX = event.clientX;
	}
	function up(event: PointerEvent) {
		if (downX === null) return;
		const dx = event.clientX - downX;
		downX = null;
		if (Math.abs(dx) > 40) (dx < 0 ? next : prev)();
	}

	function keys(event: KeyboardEvent) {
		if (event.key === 'ArrowRight') {
			event.preventDefault();
			next();
		} else if (event.key === 'ArrowLeft') {
			event.preventDefault();
			prev();
		}
	}
</script>

<section
	id="hikayat"
	class="story wrap"
	aria-roledescription="tayangan slaid"
	aria-labelledby="legenda-tajuk"
	bind:this={section}
	onfocusin={() => (focused = true)}
	onfocusout={(e) => (focused = !!section?.contains(e.relatedTarget as Node))}
>
	<div class="frame" class:still>
		<div class="scene" aria-hidden="true" onpointerdown={down} onpointerup={up} onpointercancel={() => (downX = null)}>
			{#if seen}
				{#each WORLDS as w, i (w.name)}
					{#if near.has(i)}
						<img class="field" class:on={i === shown} style:--from="{way * 6}%" src={battleBg(i)} alt="" draggable="false" />
					{/if}
				{/each}
				{#key shown}
					<div class="boss-spot" style:--aura={world.aura}>
						<span class="aura"></span>
						<span class="ground"></span>
						<img class="boss" class:flip={introFlip(shown)} src={introArt(shown)} alt="" draggable="false" />
					</div>
					<img class="hero" src={heroWeaponArt(world.hero, world.weapon)} alt="" draggable="false" />
				{/key}
			{/if}
			<div class="shade"></div>
		</div>

		<div class="copy">
			<p class="badge"><span>Baharu</span> Mod pengembaraan</p>
			<h2 id="legenda-tajuk">Hikayat Lima Alam</h2>

			{#key shown}
				<div class="slide" role="group" aria-roledescription="slaid" aria-label="Dunia {shown + 1} daripada {N}: {world.name}" style:--from="{way * 1.2}rem">
					<p class="count">Dunia {shown + 1} / {N}</p>
					<h3 class="world-name"><img class="emblem e-{world.key}" src={symbol(shown)} alt="" width="44" height="44" /> {world.name}</h3>
					<p class="intro">{world.intro}</p>
					<p class="boss-line">
						<span>Boss: <strong>{world.boss}</strong></span>
						<span class="weak">Takut <img src={elementIcon(world.weak)} alt="" width="28" height="28" /> <strong>{ELEMENT_NAME[world.weak]}</strong></span>
					</p>
				</div>
			{/key}

			<div class="controls" role="toolbar" aria-label="Tayangan dunia" tabindex="-1" onkeydown={keys}>
				<button type="button" class="round" onclick={prev} aria-label="Dunia sebelum"><Icon name="back" /></button>
				<ul class="worlds" aria-label="Pilih dunia">
					{#each WORLDS as w, i (w.name)}
						<li>
							<button type="button" class:on={i === shown} aria-current={i === shown ? 'true' : undefined} onclick={() => go(i)} aria-label={w.name}>
								<img class="emblem e-{w.key}" src={symbol(i)} alt="" width="46" height="46" />
								{#if i === shown}
									{#key turn}<span class="bar" class:run={playing} style:--every="{EVERY}ms"></span>{/key}
								{/if}
							</button>
						</li>
					{/each}
				</ul>
				<button type="button" class="round" onclick={next} aria-label="Dunia seterusnya"><Icon name="next" /></button>
				<button type="button" class="round pause" onclick={() => (paused = !paused)} aria-pressed={paused} aria-label={paused ? 'Main tayangan' : 'Jeda tayangan'}>
					<Icon name={paused ? 'play' : 'pause'} />
				</button>
			</div>

			<ul class="facts">
				<li><strong>5</strong> dunia, 5 boss besar</li>
				<li><strong>Solo</strong> atau <strong>Party</strong> bersama kelas</li>
				<li class="elements">
					{#each ELEMENTS as el (el)}<img src={elementIcon(el)} alt={ELEMENT_NAME[el]} title={ELEMENT_NAME[el]} width="32" height="32" />{/each}
					<span>lima elemen</span>
				</li>
			</ul>

			<a class="go" href="/ibu-bapa">Main dengan kuiz anda <Icon name="next" /></a>
		</div>
	</div>
</section>

<style>
	.story {
		position: relative;
		padding-block: 2rem 3rem;
	}
	.frame {
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr);
		min-height: 32rem;
		overflow: hidden;
		border-radius: 22px;
		background: #0d1630;
		color: #fff4d8;
		box-shadow:
			inset 0 0 0 3px #d9a441,
			inset 0 0 0 6px rgb(13 22 48 / 0.9),
			0 1.4rem 2.6rem rgb(5 15 40 / 0.45);
	}
	.scene {
		position: absolute;
		inset: 0;
		touch-action: pan-y;
		user-select: none;
	}
	.field {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
		opacity: 0;
		transform: translateX(var(--from)) scale(1.06);
		transition:
			opacity 900ms ease,
			transform 1.4s cubic-bezier(0.2, 0.8, 0.2, 1);
	}
	.field.on {
		opacity: 1;
		transform: translateX(0) scale(1);
	}
	/* The boss stands in the painting's open middle, in a glow of its world's colour, on its own
	   shadow, so the portrait sits in the scene instead of on top of it. It stands over the shade
	   that darkens the painting for the words, and stops short of them. */
	.boss-spot {
		position: absolute;
		z-index: 1;
		left: 21%;
		bottom: 7%;
		width: 34%;
		height: 70%;
		display: grid;
		place-items: end center;
		pointer-events: none;
	}
	.aura {
		position: absolute;
		inset: 8% 4% 6%;
		border-radius: 50%;
		background: radial-gradient(closest-side, color-mix(in srgb, var(--aura) 55%, transparent), color-mix(in srgb, var(--aura) 18%, transparent) 60%, transparent);
		filter: blur(6px);
		animation:
			glow-in 900ms ease-out both,
			pulse 3.6s ease-in-out 900ms infinite;
	}
	.ground {
		position: absolute;
		bottom: -2%;
		left: 16%;
		right: 16%;
		height: 12%;
		border-radius: 50%;
		background: radial-gradient(closest-side, rgb(0 0 0 / 0.55), transparent);
	}
	.boss {
		position: relative;
		max-width: 100%;
		max-height: 100%;
		object-fit: contain;
		object-position: bottom;
		filter: drop-shadow(0 0 0.9rem color-mix(in srgb, var(--aura) 60%, transparent)) drop-shadow(0 0.8rem 1rem rgb(0 0 0 / 0.5));
		animation:
			appear 1s 120ms cubic-bezier(0.2, 0.9, 0.3, 1.05) both,
			float 4.5s ease-in-out 1.2s infinite;
	}
	/* the boss turns to look at the hero on its left */
	.boss.flip {
		scale: -1 1;
	}
	.hero {
		position: absolute;
		z-index: 2;
		left: 2%;
		bottom: 5%;
		height: 46%;
		width: auto;
		filter: drop-shadow(0 0.6rem 0.8rem rgb(0 0 0 / 0.5));
		animation: rise 700ms 300ms cubic-bezier(0.2, 0.9, 0.3, 1.1) both;
	}
	/* the copy side darkens so the words read over any painting */
	.shade {
		position: absolute;
		inset: 0;
		background: linear-gradient(90deg, rgb(13 22 48 / 0.05) 0%, rgb(13 22 48 / 0.25) 45%, rgb(13 22 48 / 0.88) 62%, rgb(13 22 48 / 0.95) 100%);
		pointer-events: none;
	}
	.copy {
		position: relative;
		grid-column: 2;
		display: grid;
		align-content: center;
		gap: 0.85rem;
		padding: 2rem 2rem 2rem 0.5rem;
	}
	.badge {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		font: 700 0.8rem var(--font-display);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: #ffd98a;
	}
	.badge span {
		padding: 0.2rem 0.6rem;
		border-radius: 999px;
		background: #e2549f;
		color: #fff;
	}
	h2 {
		font: 700 clamp(1.9rem, 1.3rem + 2.4vw, 3rem) / 1.05 var(--font-display);
		color: #fff4d8;
		text-shadow: 0 3px 0 #7a4a12;
	}
	.slide {
		display: grid;
		gap: 0.55rem;
		min-height: 11.5rem;
		animation: slide-in 520ms cubic-bezier(0.2, 0.9, 0.3, 1) both;
	}
	.count {
		color: #ffd98a;
		font: 700 0.8rem var(--font-display);
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}
	.world-name {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		font: 700 1.6rem/1.1 var(--font-display);
		color: #fff;
	}
	.intro {
		max-width: 30rem;
		color: #f3e6c8;
		font-size: 1.02rem;
	}
	.boss-line {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.4rem 1.2rem;
		font-weight: 700;
	}
	.boss-line strong {
		color: #ffcf5a;
	}
	.weak {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
	}
	.controls {
		display: flex;
		align-items: center;
		gap: 0.45rem;
		flex-wrap: wrap;
	}
	.round {
		display: grid;
		place-items: center;
		width: 2.75rem;
		height: 2.75rem;
		padding: 0;
		border: 2px solid rgb(217 164 65 / 0.55);
		border-radius: 50%;
		background: rgb(255 255 255 / 0.08);
		color: #fff4d8;
		cursor: pointer;
		transition:
			transform 140ms ease,
			background 140ms ease;
	}
	.round:hover {
		background: rgb(255 207 90 / 0.18);
		transform: translateY(-1px);
	}
	.pause {
		margin-left: 0.2rem;
	}
	.worlds {
		display: flex;
		gap: 0.4rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.worlds button {
		position: relative;
		display: grid;
		place-items: center;
		width: 2.9rem;
		height: 2.9rem;
		padding: 0;
		border: 0;
		border-radius: 50%;
		background: none;
		opacity: 0.72;
		cursor: pointer;
		transition:
			transform 160ms ease,
			opacity 160ms ease;
	}
	.worlds button:hover {
		opacity: 1;
		transform: translateY(-2px);
	}
	/* the chosen world's medallion is whole-bright, ringed in light */
	.worlds button.on {
		opacity: 1;
		box-shadow:
			0 0 0 2px #0d1630,
			0 0 0 4px #ffcf5a,
			0 0 1rem rgb(255 207 90 / 0.55);
	}
	/* how long until the next world, under the chosen medallion */
	.bar {
		position: absolute;
		left: 15%;
		bottom: -0.55rem;
		height: 3px;
		width: 70%;
		border-radius: 2px;
		background: #ffcf5a;
		transform: scaleX(0);
		transform-origin: left;
	}
	.bar.run {
		animation: fill var(--every) linear forwards;
	}
	/* Each world's emblem moves its own way: on the slide's title, on the chosen chip, and on a chip
	   under the pointer. Tasik Chini ripples like water, Batang Lupar floats on the river, Hutan Larut
	   stomps, Rimba Bayangan flickers like a shadow, Gunung Ledang glows in the mist. */
	.emblem {
		transform-origin: 50% 60%;
	}
	.world-name .emblem,
	.worlds button.on .emblem,
	.worlds button:hover .emblem {
		animation: var(--emblem) infinite;
	}
	.e-chini {
		--emblem: ripple 2.4s ease-in-out;
	}
	.e-lupar {
		--emblem: drift 2.8s ease-in-out;
	}
	.e-larut {
		--emblem: stomp 1.6s cubic-bezier(0.3, 0, 0.4, 1);
	}
	.e-kancil {
		--emblem: flicker 2.2s steps(1, end);
	}
	.e-ledang {
		--emblem: mist 4s ease-in-out;
	}
	@keyframes ripple {
		0%,
		100% {
			transform: rotate(0deg) scale(1);
			filter: drop-shadow(0 0 0 #38d6c8);
		}
		30% {
			transform: rotate(-8deg) scale(1.06);
		}
		55% {
			transform: rotate(6deg) scale(1.03);
			filter: drop-shadow(0 0 6px #38d6c8);
		}
	}
	@keyframes drift {
		0%,
		100% {
			transform: translateY(0) rotate(-4deg);
		}
		50% {
			transform: translateY(-4px) rotate(4deg);
		}
	}
	@keyframes stomp {
		0%,
		55%,
		100% {
			transform: translateY(0) scale(1, 1);
		}
		20% {
			transform: translateY(-6px) scale(0.94, 1.06);
		}
		40% {
			transform: translateY(0) scale(1.12, 0.86);
		}
	}
	@keyframes flicker {
		0%,
		100% {
			opacity: 1;
			transform: translateX(0);
			filter: drop-shadow(0 0 5px #b07cff);
		}
		40% {
			opacity: 0.35;
			transform: translateX(-2px);
		}
		46% {
			opacity: 1;
			transform: translateX(2px);
		}
		70% {
			opacity: 0.6;
			transform: translateX(0);
			filter: drop-shadow(0 0 10px #b07cff);
		}
	}
	@keyframes mist {
		0%,
		100% {
			transform: translateY(0);
			filter: drop-shadow(0 0 2px #ffffff) brightness(1);
		}
		50% {
			transform: translateY(-3px);
			filter: drop-shadow(0 0 9px #e8f4ff) brightness(1.15);
		}
	}
	.round:focus-visible,
	.worlds button:focus-visible {
		outline: 3px solid #ffcf5a;
		outline-offset: 2px;
	}
	.facts {
		display: grid;
		gap: 0.3rem;
		margin: 0;
		padding: 0;
		list-style: none;
		font-weight: 700;
		font-size: 0.95rem;
	}
	.facts strong {
		color: #ffcf5a;
	}
	.elements {
		display: flex;
		align-items: center;
		gap: 0.25rem;
	}
	.elements span {
		margin-left: 0.3rem;
	}
	.go {
		justify-self: start;
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		min-height: 3rem;
		padding: 0.7rem 1.3rem;
		border-radius: 999px;
		background: linear-gradient(180deg, #ffd66b, #f4a524);
		color: #3a2306;
		font: 700 1.05rem var(--font-display);
		text-decoration: none;
		box-shadow:
			0 4px 0 #a8650c,
			0 0.8rem 1.4rem rgb(0 0 0 / 0.3);
		transition: transform 140ms ease;
	}
	.go:hover {
		transform: translateY(-2px);
	}
	.go:active {
		transform: translateY(2px);
		box-shadow: 0 2px 0 #a8650c;
	}
	.go:focus-visible {
		outline: 3px solid #fff;
		outline-offset: 3px;
	}
	@keyframes rise {
		from {
			opacity: 0;
			transform: translateY(1.2rem) scale(0.96);
		}
	}
	@keyframes appear {
		from {
			opacity: 0;
			transform: translateY(1.6rem) scale(0.9);
			filter: brightness(2.2) drop-shadow(0 0 1.6rem var(--aura));
		}
		55% {
			opacity: 1;
		}
	}
	@keyframes glow-in {
		from {
			opacity: 0;
			transform: scale(0.6);
		}
	}
	@keyframes pulse {
		50% {
			opacity: 0.7;
			transform: scale(1.05);
		}
	}
	@keyframes float {
		50% {
			transform: translateY(-0.5rem);
		}
	}
	@keyframes slide-in {
		from {
			opacity: 0;
			transform: translateX(var(--from));
		}
	}
	@keyframes fill {
		to {
			transform: scaleX(1);
		}
	}
	@media (max-width: 860px) {
		.frame {
			grid-template-columns: minmax(0, 1fr);
			grid-template-rows: 17rem auto;
			min-height: 0;
		}
		.scene {
			bottom: auto;
			height: 17rem;
		}
		.shade {
			background: linear-gradient(180deg, rgb(13 22 48 / 0) 55%, rgb(13 22 48 / 0.95) 100%);
		}
		.boss-spot {
			left: auto;
			right: 3%;
			width: 60%;
			height: 80%;
		}
		.hero {
			height: 62%;
		}
		.copy {
			grid-column: 1;
			grid-row: 2;
			padding: 1.2rem 1.2rem 1.6rem;
			background: #0d1630;
		}
	}
	.still .emblem {
		animation: none !important;
	}
	.still .field,
	.still .boss,
	.still .aura,
	.still .hero,
	.still .slide {
		transition: opacity 200ms linear;
		animation: none;
		transform: none;
	}
</style>
