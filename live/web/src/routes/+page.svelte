<!--
	The front door, drawn as one sea seen from above. A child writes the room code on a ticket by the
	main island, where everyone gathers before a game; below, the eight games are islands a sampan
	sails between. Then the beach (how it works), dusk over the beach (the four 3D games), the
	parents' field and the back of the card.
-->
<script lang="ts">
	import { fade, fly } from 'svelte/transition';
	import Icon from '$ui/Icon.svelte';
	import Didi from '$ui/Didi.svelte';
	import Logo from '$ui/Logo.svelte';
	import IslandMap from '$lib/home/IslandMap.svelte';
	import MainIsland from '$lib/home/MainIsland.svelte';
	import Ticket from '$lib/home/Ticket.svelte';
	import Games3D from '$lib/home/Games3D.svelte';
	import { reveal } from '$lib/home/reveal';
	import { beachTile, grassFringe, seaTile, shoreStrip } from '$lib/pixel/sea';

	// The backdrops are small pixel pictures the page repeats (see lib/pixel/sea.ts).
	const sea = { a: `url(${seaTile(0).toURL(1)})`, b: `url(${seaTile(1).toURL(1)})`, shore: `url(${shoreStrip().toURL(1)})` };
	const beach = `url(${beachTile().toURL(1)})`;
	const fringe = `url(${grassFringe().toURL(1)})`;

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
				['Pilih satu permainan', '12 pilihan'],
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

	// The slip is cut along the bottom in square teeth, each as wide as a few sprite pixels.
	const TEETH = 24;
	const teeth = `polygon(0 0, 100% 0, ${Array.from({ length: TEETH }, (_, i) => {
		const right = (100 - (i * 100) / TEETH).toFixed(2);
		const left = (100 - ((i + 1) * 100) / TEETH).toFixed(2);
		const edge = i % 2 ? 'calc(100% - 8px)' : '100%';
		return `${right}% ${edge}, ${left}% ${edge}`;
	}).join(', ')})`;

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
		<a class="far" href="#dunia-3d">Permainan 3D</a>
		<a class="parents" href="/ibu-bapa"><span class="long">Untuk ibu bapa</span><span class="short">Ibu bapa</span> <Icon name="next" size={18} /></a>
	</nav>
</header>

<main>
	<div class="sea" style:--sea-a={sea.a} style:--sea-b={sea.b} style:--shore={sea.shore}>
		<div class="swell" aria-hidden="true"></div>

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

		<div class="shore" aria-hidden="true"></div>
	</div>

<section id="cara" class="beach" style:--beach={beach} aria-labelledby="cara-tajuk">
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
		<div class="slip-shadow" {@attach reveal(120)}>
			<div class="slip" style:clip-path={teeth}>
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
	</div>
</section>

<Games3D />

<section class="field" style:--fringe={fringe} aria-labelledby="ibu-bapa-tajuk">
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
					<li><a href="#dunia-3d">Empat permainan 3D</a></li>
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
	/* The sea is a small picture repeated, with two frames of wave marks that take turns. */
	.swell {
		position: absolute;
		inset: 0;
		background: var(--sea-a) 0 0 / calc(var(--px) * 64) calc(var(--px) * 64);
		image-rendering: pixelated;
		pointer-events: none;
		animation: swell 3s step-end infinite;
	}
	@keyframes swell {
		0% {
			background-image: var(--sea-a);
		}
		50% {
			background-image: var(--sea-b);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.swell {
			animation: none;
		}
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
	/* A dashed underline, like a row of stepping stones, on the links you point at. */
	nav a:hover,
	.address a:hover {
		text-decoration: underline dashed;
		text-decoration-thickness: 3px;
		text-underline-offset: 6px;
	}
	nav .parents {
		padding: 0.4rem 0.85rem;
		border: 2px solid var(--edge);
		border-radius: var(--r-md);
		background: var(--paper);
		box-shadow: 0 3px 0 var(--edge);
		color: var(--ink);
		transition: transform var(--t-press) steps(2);
	}
	nav .parents:hover {
		transform: translateY(-2px);
		box-shadow: 0 5px 0 var(--edge);
		text-decoration: none;
	}
	nav .parents:active {
		transform: translateY(3px);
		box-shadow: none;
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
	/* Surf over the shallows, then wet sand: the sea's last edge before the beach. */
	.shore {
		position: absolute;
		left: 0;
		bottom: -1px;
		width: 100%;
		height: calc(var(--px) * 16);
		background: var(--shore) 0 100% / calc(var(--px) * 48) calc(var(--px) * 16) repeat-x;
		image-rendering: pixelated;
	}

	/* ---------------------------------------------------------------- the beach: how it works */
	.beach {
		background: var(--beach) 0 0 / calc(var(--px) * 64) calc(var(--px) * 64);
		image-rendering: pixelated;
	}
	.beach > * {
		image-rendering: auto;
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
		border: 2px solid var(--edge);
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: 0 4px 0 var(--edge);
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
	/* The slip is cut along its foot, so its hard shadow is drawn around the cut. */
	.slip-shadow {
		filter: drop-shadow(0 4px 0 #c9ae74);
		transition: transform var(--t-press) steps(2);
	}
	.slip-shadow:hover {
		transform: translateY(-2px);
	}
	.slip {
		padding: 1.8rem 1.9rem 3rem;
		background: var(--paper);
	}
	.slip-title {
		font: 600 2rem/1.1 var(--font-display);
	}
	.slip h3 {
		margin-top: 1.5rem;
		font: 800 1rem/1.3 var(--font-body);
		color: var(--brand-ink);
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
		border-bottom: 4px dashed #dccfb4;
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
	/* Blades of grass along the top, rising into the dusk above. */
	.field {
		position: relative;
		overflow: hidden;
		background: var(--field);
		color: #fff;
	}
	.field::before {
		content: '';
		position: absolute;
		inset: 0 0 auto;
		height: calc(var(--px) * 14);
		background: var(--fringe) 0 0 / calc(var(--px) * 32) calc(var(--px) * 14) repeat-x;
		image-rendering: pixelated;
	}
	.cta {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr);
		gap: 2rem 4rem;
		align-items: end;
		padding-top: calc(5rem + var(--px) * 14);
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
		border: 2px solid var(--edge);
		border-radius: var(--r-lg);
		background: var(--paper);
		box-shadow: 0 4px 0 var(--edge);
		color: var(--ink);
		text-align: center;
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
		border: 2px solid var(--edge);
		border-radius: var(--r-md);
		background: var(--ink);
		box-shadow: 0 3px 0 #000;
		color: var(--paper);
		font: 600 1.3rem var(--font-display);
		text-decoration: none;
		transition: transform var(--t-press) steps(2);
	}
	.bar:hover {
		transform: translateY(-2px);
		box-shadow: 0 5px 0 #000;
	}
	.bar:active {
		transform: translateY(3px);
		box-shadow: none;
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
		--tooth: 24px;
		display: grid;
		grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
		gap: 2rem 3rem;
		padding: 3.6rem 3rem 2rem;
		background: var(--paper);
		/* A battlement top edge, like a card cut from a pad: square teeth, as wide as they are deep. */
		mask:
			linear-gradient(#000 0 0) 0 var(--tooth) / 100% calc(100% - var(--tooth)) no-repeat, /* taste-skill-ignore: a mask that cuts the edge, not a fill */
			linear-gradient(90deg, #000 var(--tooth), #0000 0) 0 0 / calc(var(--tooth) * 2) var(--tooth) repeat-x; /* taste-skill-ignore: mask */
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
		/* Perforated round the edge like a stamp: square holes along the border, the middle left whole. */
		mask:
			linear-gradient(#000 0 0) content-box, /* taste-skill-ignore: mask layers that punch the holes, not a fill */
			conic-gradient(from 90deg at 6px 6px, #0000 25%, #000 0) -3px -3px / 10px 10px round; /* taste-skill-ignore: mask */
		transition: transform var(--t-press) steps(2);
	}
	.postcard:hover .stamp {
		transform: translateY(-3px);
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
		border: 2px solid var(--edge);
		border-left: 4px dashed var(--edge);
		border-radius: var(--r-md);
		background: var(--sun);
		color: var(--ink);
		font: 600 1.0625rem var(--font-display);
		cursor: pointer;
		box-shadow: 0 3px 0 var(--edge); /* taste-skill-ignore: it floats over the page */
		transition: transform var(--t-press) steps(2);
	}
	.mini-ticket:hover {
		transform: translateY(-2px);
		box-shadow: 0 5px 0 var(--edge);
	}
	.mini-ticket:active {
		transform: translateY(3px);
		box-shadow: none;
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
	/* The three section links need about 860px beside the logo and the parents' link. */
	@media (max-width: 900px) {
		nav .far {
			display: none;
		}
	}
	@media (max-width: 720px) {
		.postcard {
			grid-template-columns: minmax(0, 1fr);
			padding: 3rem 1.4rem 1.6rem;
		}
		.reply {
			padding: 2rem 1.4rem 4.5rem;
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
