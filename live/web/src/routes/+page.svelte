<!--
	The front door, drawn as one sea seen from above. A child writes the room code on a ticket by the
	main island, where everyone gathers before a game; below, the eight games are islands a sampan
	sails between. Then the beach (how it works), the parents' field and the back of the card.
-->
<script lang="ts">
	import { fade, fly } from 'svelte/transition';
	import Icon from '$ui/Icon.svelte';
	import Didi from '$ui/Didi.svelte';
	import Logo from '$ui/Logo.svelte';
	import IslandMap from '$lib/home/IslandMap.svelte';
	import MainIsland from '$lib/home/MainIsland.svelte';
	import Ticket from '$lib/home/Ticket.svelte';
	import { reveal } from '$lib/home/reveal';

	const PLAN: { when: string; rows: [string, string][] }[] = [
		{
			when: 'Sebelum bermain: ibu bapa',
			rows: [
				['Tulis soalan sendiri', '8 jenis'],
				['Tambah gambar pada soalan', 'jika mahu'],
				['Simpan kuiz', 'sekali sahaja']
			]
		},
		{
			when: 'Bila mahu bermain',
			rows: [
				['Pilih satu pulau permainan', '8 pilihan'],
				['Kongsi pautan, kod QR atau kod', '6 digit']
			]
		},
		{
			when: 'Semasa bermain: kanak-kanak',
			rows: [
				['Pilih haiwan, warna dan nama', 'tanpa akaun'],
				['Jawab dan main bersama kawan', 'telefon sendiri'],
				['Hos boleh rehat atau langkau', 'bila-bila']
			]
		}
	];

	// The slip is torn off along the bottom: a row of small teeth.
	const TEETH = 28;
	const zigzag = `polygon(0 0, 100% 0, ${Array.from({ length: TEETH * 2 + 1 }, (_, i) => `${(100 - (i * 100) / (TEETH * 2)).toFixed(2)}% ${i % 2 ? '100%' : 'calc(100% - 12px)'}`).join(', ')})`;

	// Small wave marks on the sea, in % of the sea's size.
	const WAVES = [
		[47, 6], [95, 9], [2, 30], [46, 33], [96, 41], [1.5, 58], [97, 70], [2, 88], [49, 93], [95, 96]
	];

	let ticket = $state<ReturnType<typeof Ticket>>();
	let ticketArea = $state<HTMLElement>();
	let pastTicket = $state(false);

	// Once the ticket has scrolled away, a small one follows the page so a code can go in from anywhere.
	$effect(() => {
		if (!ticketArea || !('IntersectionObserver' in window)) return;
		const watch = new IntersectionObserver(([entry]) => (pastTicket = !entry.isIntersecting && entry.boundingClientRect.top < 0));
		watch.observe(ticketArea);
		return () => watch.disconnect();
	});

	function backToTicket() {
		const still = matchMedia('(prefers-reduced-motion: reduce)').matches;
		ticketArea?.scrollIntoView({ behavior: still ? 'auto' : 'smooth', block: 'center' });
		setTimeout(() => ticket?.focus(), still ? 0 : 450);
	}
</script>

<svelte:head><title>DIDIK Main Bersama: kuiz permainan bersama kawan</title></svelte:head>

<!-- The bar lies over the top of the sea; everything after it is the page's main content. -->
<header class="top wrap">
	<Logo light />
	<nav aria-label="Laman utama">
		<a class="far" href="#pulau">Lapan pulau</a>
		<a class="far" href="#cara">Cara bermain</a>
		<a class="parents" href="/ibu-bapa"><span class="long">Untuk ibu bapa</span><span class="short">Ibu bapa</span> <Icon name="next" size={18} /></a>
	</nav>
</header>

<main>
	<div class="sea">
		<div class="waves" aria-hidden="true">
			{#each WAVES as [x, y] (`${x}-${y}`)}
				<svg viewBox="0 0 36 10" style:left="{x}%" style:top="{y}%" focusable="false">
					<path d="M2 7 q8 -7 16 0 q8 -7 16 0" />
				</svg>
			{/each}
		</div>

		<section class="hero wrap" aria-labelledby="hero-title">
			<div class="copy">
				<h1 id="hero-title" {@attach reveal(0)}>Main kuiz bersama kawan.</h1>
				<p class="lead" {@attach reveal(90)}>Ibu bapa tulis soalan. Kamu masuk dengan kod bilik, pilih haiwan, dan terus bermain.</p>
				<div bind:this={ticketArea} {@attach reveal(180)}><Ticket bind:this={ticket} /></div>
			</div>
			<div class="home-island" {@attach reveal(260)}><MainIsland /></div>
		</section>

		<section id="pulau" class="islands wrap" aria-labelledby="pulau-tajuk" {@attach reveal()}>
			<IslandMap>
				{#snippet head()}
					<div class="islands-head">
						<h2 id="pulau-tajuk">Satu kuiz, lapan pulau</h2>
						<p>Semua berkumpul di dataran dahulu. Bila hos tekan Mula, kamu belayar ke pulau yang dipilih dan menjawab soalan yang sama di sana.</p>
					</div>
				{/snippet}
			</IslandMap>
		</section>

		<svg class="shore" viewBox="0 0 1440 80" preserveAspectRatio="none" aria-hidden="true" focusable="false">
			<path d="M0 34 C140 14 260 52 400 34 C540 16 660 50 800 32 C940 14 1060 48 1200 30 C1300 18 1380 30 1440 26 V80 H0z" fill="#e8f6fc" opacity=".7" />
			<path d="M0 46 C140 28 260 64 400 46 C540 28 660 62 800 44 C940 26 1060 60 1200 42 C1300 30 1380 42 1440 38 V80 H0z" fill="var(--sand-soft)" />
		</svg>
	</div>

<section id="cara" class="beach" aria-labelledby="cara-tajuk">
	<div class="wrap how">
		<div class="how-head" {@attach reveal()}>
			<h2 id="cara-tajuk">Ibu bapa tulis, anak-anak main</h2>
			<p>Kuiz ditulis sekali oleh orang yang kenal anak-anak itu. Selepas itu ia boleh dimainkan di mana-mana pulau, berapa kali pun.</p>
			<figure class="sample" data-ui>
				<div class="sample-card">
					<p class="sample-q">Apakah haiwan kebangsaan Malaysia?</p>
					<div class="tiles">
						{#each ['Harimau Malaya', 'Gajah', 'Orang utan', 'Enggang'] as choice, i (choice)}
							<span class="tile t{i}" class:right={i === 0}>
								<span class="letter">{'ABCD'[i]}</span><span class="text">{choice}</span>
								{#if i === 0}<span class="mark"><Icon name="check" size={18} /></span>{/if}
							</span>
						{/each}
					</div>
				</div>
				<figcaption>Satu soalan daripada kuiz contoh <cite>Haiwan di Malaysia</cite>, seperti yang dilihat di telefon.</figcaption>
			</figure>
		</div>
		<div class="slip" style:clip-path={zigzag} {@attach reveal(120)}>
			<p class="slip-title">Jadual bermain</p>
			{#each PLAN as part (part.when)}
				<h3>{part.when}</h3>
				<ul>
					{#each part.rows as [what, note] (what)}
						<li><span>{what}</span><span class="leader" aria-hidden="true"></span><span class="value">{note}</span></li>
					{/each}
				</ul>
			{/each}
			<p class="total"><span>Jumlah bayaran</span><span>Percuma</span></p>
		</div>
	</div>
</section>

<section class="field" aria-labelledby="ibu-bapa-tajuk">
	<div class="wrap cta">
		<p class="why" {@attach reveal()}>Soalan di sini ditulis oleh orang yang kenal anak-anak itu: ibu bapa, guru, abang dan kakak. Tiada AI yang mengarangnya.</p>
		<div class="reply" {@attach reveal(120)}>
			<h2 id="ibu-bapa-tajuk">Tulis kuiz pertama</h2>
			<p>Akaun ibu bapa percuma. Daftar dengan e-mel, tulis soalan, dan buka bilik bila-bila masa.</p>
			<a class="bar" href="/ibu-bapa">Ke ruang ibu bapa <span class="arrow"><Icon name="next" /></span></a>
		</div>
	</div>
</section>
</main>

<footer class="foot">
	<div class="wrap">
		<div class="postcard">
			<div class="message">
				<p class="sign">Jumpa di dataran!</p>
				<p>DIDIK Main Bersama ialah tempat kanak-kanak bermain kuiz bersama kawan. Percuma, tanpa iklan dan tanpa akaun untuk kanak-kanak.</p>
			</div>
			<div class="address">
				<span class="stamp" aria-hidden="true"><Didi mood="happy" size={54} /></span>
				<ul>
					<li><a href="#tiket">Masuk bilik dengan kod</a></li>
					<li><a href="#pulau">Lapan pulau permainan</a></li>
					<li><a href="#cara">Cara bermain</a></li>
					<li><a href="/ibu-bapa">Ruang ibu bapa</a></li>
				</ul>
			</div>
			<p class="imprint">DIDIK Main Bersama, 2026</p>
		</div>
	</div>
</footer>

{#if pastTicket}
	<button type="button" class="mini-ticket" onclick={backToTicket} in:fly={{ y: 48, duration: 320 }} out:fade={{ duration: 140 }}>
		Ada kod? <strong>Masuk</strong>
	</button>
{/if}

<style>
	/* ---------------------------------------------------------------- the sea: hero and islands */
	.sea {
		position: relative;
		overflow: hidden;
		background: var(--sea-map);
		color: var(--on-sea);
	}
	.waves {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}
	@media (max-width: 1000px) {
		.waves {
			display: none;
		}
	}
	.waves svg {
		position: absolute;
		width: 2.2rem;
		height: auto;
	}
	.waves path {
		fill: none;
		stroke: #3f93c6;
		stroke-width: 2.4;
		stroke-linecap: round;
	}
	.top {
		position: absolute;
		inset: 0 0 auto;
		z-index: 2;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		min-height: 4.6rem;
	}
	nav {
		display: flex;
		align-items: center;
		gap: 1.6rem;
	}
	nav a {
		display: inline-flex;
		align-items: center;
		gap: 0.2rem;
		color: var(--on-sea);
		font-weight: 800;
		text-decoration: none;
		white-space: nowrap;
	}
	/* A wavy underline, like a line of water, on the links you point at. */
	nav a:hover,
	.address a:hover {
		text-decoration: underline wavy;
		text-decoration-thickness: 2px;
		text-underline-offset: 6px;
	}
	nav .parents {
		padding: 0.45rem 0.9rem;
		border-radius: var(--r-pill);
		background: var(--paper);
		color: var(--ink);
		transition: transform var(--t-state) var(--spring);
	}
	nav .parents:hover {
		transform: rotate(-3deg) scale(1.04);
		text-decoration: none;
	}
	.parents .short {
		display: none;
	}
	.hero {
		position: relative;
		z-index: 1;
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		align-items: center;
		gap: 2rem;
		padding-block: 5.1rem 3.5rem;
	}
	.hero h1 {
		font-size: clamp(2.4rem, 1.1rem + 3.7vw, 4.4rem);
		line-height: 1.02;
	}
	.lead {
		margin-top: 1rem;
		max-width: 30rem;
		font-size: var(--fs-lead);
	}
	.home-island {
		min-width: 0;
		margin-right: -1rem;
	}
	.islands {
		position: relative;
		z-index: 1;
		padding-block: 2.5rem 7rem;
	}
	.islands-head {
		display: grid;
		gap: 0.7rem;
		max-width: 40rem;
	}
	.islands-head h2 {
		font-size: var(--fs-h1);
	}
	.islands-head p {
		font-size: var(--fs-lead);
	}
	.shore {
		position: absolute;
		left: 0;
		bottom: -1px;
		width: 100%;
		height: 4.5rem;
	}

	/* ---------------------------------------------------------------- the beach: how it works */
	.beach {
		background: var(--sand-soft);
	}
	.how {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 30rem);
		gap: 2.5rem 4rem;
		align-items: start;
		padding-block: 3.5rem 6rem;
	}
	.how-head {
		display: grid;
		gap: 1rem;
		max-width: 30rem;
	}
	.how-head h2 {
		font-size: var(--fs-h1);
	}
	.how-head p {
		font-size: var(--fs-lead);
	}
	/* One real question as the game shows it, lying on the sand. */
	.sample {
		display: grid;
		gap: 0.7rem;
		max-width: 27rem;
		margin: 1.2rem 0 0;
	}
	.sample-card {
		padding: 1.1rem;
		border-radius: var(--r-lg);
		background: var(--card);
		rotate: -2deg;
		transition: rotate 420ms var(--spring);
	}
	.sample:hover .sample-card {
		rotate: 0deg;
	}
	.sample-q {
		margin-bottom: 0.9rem;
		font: 600 1.3rem / 1.25 var(--font-display);
	}
	.sample .tile {
		min-height: 3.4rem;
		padding: 0.6rem 0.75rem;
		font-size: 1.05rem;
		cursor: default;
	}
	.sample figcaption {
		color: var(--ink-2);
		font-size: 0.875rem;
		font-weight: 700;
	}
	.sample cite {
		font-style: normal;
		font-weight: 800;
	}
	.slip {
		padding: 1.8rem 1.9rem 3rem;
		background: var(--paper);
		transition: transform 420ms var(--spring);
	}
	.slip:hover {
		transform: rotate(0.8deg) translateY(-3px);
	}
	.slip-title {
		font: 600 2rem/1.1 var(--font-display);
	}
	.slip h3 {
		margin-top: 1.5rem;
		font: 800 1rem/1.3 var(--font-body);
		color: var(--brand);
	}
	.slip ul {
		display: grid;
		gap: 0.45rem;
		margin: 0.5rem 0 0;
		padding: 0;
		list-style: none;
	}
	/* When a line wraps, the dots and the value stay with its last line. */
	.slip li {
		display: flex;
		align-items: last baseline;
		gap: 0.5rem;
	}
	.slip li > span:first-child {
		flex: 0 1 auto;
		min-width: 0;
	}
	.leader {
		flex: 1 0 1rem;
		border-bottom: 4px dotted #dccfb4;
		translate: 0 -0.25rem;
	}
	.value {
		color: var(--ink-2);
		white-space: nowrap;
	}
	.total {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
		margin: 1.6rem -1.9rem 0;
		padding: 0.7rem 1.9rem;
		background: var(--ink);
		color: var(--paper);
		font: 600 1.3rem/1.3 var(--font-display);
	}

	/* ---------------------------------------------------------------- the field: for parents */
	.field {
		overflow: hidden;
		background: var(--field);
		color: #fff;
	}
	.cta {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr);
		gap: 2rem 4rem;
		align-items: end;
		padding-top: 5rem;
	}
	.why {
		max-width: 26rem;
		padding-bottom: 5.5rem;
		font-size: var(--fs-lead);
	}
	.reply {
		display: grid;
		justify-items: center;
		gap: 0.9rem;
		margin-bottom: -3.5rem;
		padding: 2.6rem 2.6rem 5.5rem;
		background: var(--paper);
		color: var(--ink);
		text-align: center;
		rotate: 2deg;
		transition: rotate 420ms var(--spring);
	}
	.reply:hover {
		rotate: 0.5deg;
	}
	.reply h2 {
		font-size: var(--fs-h2);
	}
	.reply p {
		max-width: 26rem;
		color: var(--ink-2);
	}
	.bar {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.4rem;
		width: 100%;
		min-height: 3.5rem;
		margin-top: 0.6rem;
		border-radius: var(--r-md);
		background: var(--ink);
		color: var(--paper);
		font: 600 1.3rem var(--font-display);
		text-decoration: none;
		transition: transform var(--t-press) var(--ease-out);
	}
	.bar:active {
		transform: scale(0.98, 0.95);
	}
	.arrow {
		display: inline-flex;
		transition: transform var(--t-state) var(--spring);
	}
	.bar:hover .arrow {
		transform: translateX(5px);
	}

	/* ---------------------------------------------------------------- the back of the card */
	.foot {
		position: relative;
		background: var(--field);
		padding-bottom: 2.5rem;
	}
	.postcard {
		--bite: 18px;
		display: grid;
		grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
		gap: 2rem 3rem;
		padding: 3.6rem 3rem 2rem;
		background: var(--paper);
		/* A scalloped top edge, like a card torn from a pad. */
		mask:
			radial-gradient(circle var(--bite) at 50% 0, #0000 97%, #000) 0 0 / 46px 100% repeat-x; /* taste-skill-ignore: a mask that cuts the edge, not a fill */
	}
	.sign {
		font: 600 var(--fs-h2) / 1.1 var(--font-display);
	}
	.message p + p {
		margin-top: 0.7rem;
		max-width: 30rem;
		color: var(--ink-2);
	}
	.address {
		position: relative;
		padding-right: 6.5rem;
	}
	.address ul {
		display: grid;
		gap: 0.6rem;
		margin: 0;
		padding: 0;
		list-style: none;
		font-size: 1.1rem;
		font-weight: 800;
	}
	.address a {
		color: var(--ink);
		text-decoration: none;
	}
	.stamp {
		position: absolute;
		top: 0;
		right: 0;
		display: grid;
		place-items: center;
		width: 4.6rem;
		height: 5.6rem;
		padding: 5px;
		background: var(--sun);
		/* Perforated round the edge like a stamp: holes along the border, the middle left whole. */
		mask:
			linear-gradient(#000 0 0) content-box, /* taste-skill-ignore: mask layers that punch the holes, not a fill */
			radial-gradient(circle 3.5px, #0000 96%, #000) -5px -5px / 10px 10px round; /* taste-skill-ignore: mask */
		rotate: 6deg;
		transition: rotate 420ms var(--spring);
	}
	.postcard:hover .stamp {
		rotate: -4deg;
	}
	.imprint {
		grid-column: 1 / -1;
		color: var(--ink-2);
		font-size: 0.875rem;
		font-weight: 700;
	}

	/* ---------------------------------------------------------------- the small ticket that follows */
	.mini-ticket {
		position: fixed;
		right: max(1rem, env(safe-area-inset-right, 0px));
		bottom: max(1rem, env(safe-area-inset-bottom, 0px));
		z-index: 40;
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.75rem 1.1rem 0.75rem 1rem;
		border: 0;
		border-left: 4px dotted var(--sun-deep);
		border-radius: var(--r-md);
		background: var(--sun);
		color: var(--ink);
		font: 600 1.0625rem var(--font-display);
		cursor: pointer;
		box-shadow: var(--lift-low); /* taste-skill-ignore: it floats over the page */
		--shade: var(--sun-deep);
		transition: transform var(--t-state) var(--spring);
	}
	.mini-ticket:hover {
		transform: rotate(-4deg) scale(1.05);
	}
	.mini-ticket:active {
		transform: scale(0.96);
	}

	/* ---------------------------------------------------------------- narrower screens */
	@media (max-width: 1000px) {
		.hero {
			grid-template-columns: minmax(0, 1fr);
			padding-bottom: 2.5rem;
		}
		.home-island {
			justify-self: center;
			width: 100%;
			max-width: 40rem;
			margin: 0;
		}
		.how {
			grid-template-columns: minmax(0, 1fr);
		}
		.cta {
			grid-template-columns: minmax(0, 1fr);
		}
		.why {
			padding-bottom: 0;
		}
	}
	@media (max-width: 720px) {
		nav .far {
			display: none;
		}
		.postcard {
			grid-template-columns: minmax(0, 1fr);
			padding: 3rem 1.4rem 1.6rem;
		}
		.reply {
			padding: 2rem 1.4rem 4.5rem;
			rotate: 1deg;
		}
		.slip {
			padding-inline: 1.3rem;
		}
		.total {
			margin-inline: -1.3rem;
			padding-inline: 1.3rem;
		}
	}
	/* Small phones: a smaller wordmark, then on the smallest only the mark and "didik", so the parents'
	   link keeps its gutter. */
	@media (max-width: 420px) {
		.top :global(.logo) {
			font-size: 1.15rem;
		}
		.top :global(.logo svg) {
			width: 2.1rem;
			height: 2.1rem;
		}
	}
	@media (max-width: 360px) {
		.top :global(.word span) {
			display: none;
		}
	}
	@media (max-width: 440px) {
		.parents .long {
			display: none;
		}
		.parents .short {
			display: inline;
		}

	}
</style>
