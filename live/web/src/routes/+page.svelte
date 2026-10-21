<!--
	The front door. Children type a room code; parents go to their quizzes. Below, the eight games,
	each a world of its own colour.
-->
<script lang="ts">
	import { goto } from '$app/navigation';
	import { play } from '$lib/sound';
	import Avatar from '$ui/Avatar.svelte';
	import Didi from '$ui/Didi.svelte';
	import Icon from '$ui/Icon.svelte';
	import Logo from '$ui/Logo.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';

	let code = $state('');
	let problem = $state('');

	const GAMES = [
		{ world: 'sungai', title: 'Lumba Sampan', style: 'Serentak', line: 'Jawab betul dan pantas, sampan kamu meluncur ke garisan penamat.', bg: '#3ba7d9', ink: '#ffffff' },
		{ world: 'kolam', title: 'Lompat!', style: 'Serentak', line: 'Lompat ke pulau jawapan sebelum masa tamat. Pulau yang salah tenggelam!', bg: '#4fc3d9', ink: '#10343c' },
		{ world: 'pulau', title: 'Pulau Harta Karun', style: 'Ikut kadar sendiri', line: 'Setiap jawapan betul = satu penyodok. Gali dan cari permata.', bg: '#f6d58e', ink: '#4a3200' },
		{ world: 'hutan', title: 'Hutan Misteri', style: 'Jelajah', line: 'Jalan-jalan di hutan bersama kawan, buka peti soalan, kumpul lima kunci.', bg: '#2e6e43', ink: '#ffffff' },
		{ world: 'peta', title: 'Pasukan Warna', style: 'Pasukan', line: 'Harimau lawan Penyu. Tawan petak pulau untuk pasukan kamu.', bg: '#f28c28', ink: '#3a1d00' },
		{ world: 'kampung', title: 'Kampung Kita', style: 'Kerjasama', line: 'Semua pemain bina satu kampung bersama. Tiada yang kalah.', bg: '#8bcb6b', ink: '#1d3a12' },
		{ world: 'galeri', title: 'Teka Gambar', style: 'Serentak', line: 'Jawapan betul membuka petak gambar rahsia. Siapa paling cepat meneka?', bg: '#ffe7a3', ink: '#4a3200' },
		{ world: 'kebun', title: 'Kebun Ajaib', style: 'Ikut kadar sendiri', line: 'Jawab untuk dapat air. Tanam, siram dan tuai.', bg: '#9b6a43', ink: '#ffffff' }
	];

	function enter(event: Event) {
		event.preventDefault();
		const key = code.trim().toLowerCase().replace(/\s+/g, '');
		const fromLink = key.match(/\/m\/([a-z0-9-]+)/)?.[1];
		const target = fromLink ?? key;
		if (!/^(\d{6}|[a-z]+-[a-z]+-\d{2})$/.test(target)) {
			problem = 'Masukkan kod 6 digit, contohnya 482 913.';
			return;
		}
		play('pop');
		void goto(`/m/${target}`);
	}
</script>

<svelte:head><title>DIDIK Main Bersama: kuiz permainan bersama kawan</title></svelte:head>

<header class="top wrap">
	<Logo />
	<a class="parents" href="/ibu-bapa">Untuk ibu bapa <Icon name="next" size={18} /></a>
</header>

<main>
	<section class="hero wrap">
		<div class="copy">
			<h1>Main kuiz bersama kawan.</h1>
			<p class="lead">Ibu bapa tulis soalan. Kamu masuk dengan satu kod, pilih haiwan, dan terus bermain.</p>
			<form class="enter" onsubmit={enter}>
				<label for="code" class="visually-hidden">Kod bilik</label>
				<input
					id="code"
					class="input code"
					bind:value={code}
					inputmode="numeric"
					autocomplete="off"
					placeholder="Kod bilik"
					aria-describedby={problem ? 'code-problem' : undefined}
					aria-invalid={!!problem}
					oninput={() => (problem = '')}
				/>
				<button class="btn btn--sun btn--big">Masuk <Icon name="next" /></button>
			</form>
			{#if problem}<p id="code-problem" class="field-error">{problem}</p>{/if}
		</div>
		<div class="crowd" aria-hidden="true">
			<span class="didi"><Didi mood="wave" size={170} /></span>
			{#each [['harimau', 'jingga', 's2'], ['penyu', 'teal', 's4'], ['enggang', 'kuning', 's1'], ['gajah', 'biru', 's5'], ['arnab', 'jambu', 's3'], ['beruang', 'hijau', 's2']] as [animal, colour, skin], i (animal)}
				<span class="pal p{i}"><Avatar {animal} {colour} {skin} size={64} bob /></span>
			{/each}
		</div>
	</section>

	<section class="games" aria-labelledby="games-title">
		<div class="wrap">
			<h2 id="games-title">Lapan cara bermain</h2>
			<p class="sub">Setiap kuiz boleh dimainkan dalam mana-mana permainan ini.</p>
		</div>
		<ol class="worlds wrap">
			{#each GAMES as game, i (game.world)}
				<li class="world" style:--bg={game.bg} style:--ink={game.ink} style:--i={i}>
					<WorldBadge world={game.world} size={84} />
					<div>
						<p class="style">{game.style}</p>
						<h3>{game.title}</h3>
						<p>{game.line}</p>
					</div>
				</li>
			{/each}
		</ol>
	</section>

	<section class="how wrap" aria-labelledby="how-title">
		<h2 id="how-title">Macam mana ia berfungsi</h2>
		<ol class="steps">
			<li><span class="n">1</span><h3>Ibu bapa tulis kuiz</h3><p>Lapan jenis soalan: pilihan, betul atau salah, taip jawapan, nombor, susun, padankan dan isi tempat kosong. Tiada AI.</p></li>
			<li><span class="n">2</span><h3>Buka bilik, kongsi pautan</h3><p>Pilih permainan. Kanak-kanak masuk dengan pautan, kod QR atau kod 6 digit; tiada akaun.</p></li>
			<li><span class="n">3</span><h3>Main bersama</h3><p>Semua nampak kawan bermain di skrin masing-masing. Hos boleh rehat, langkau atau tamatkan.</p></li>
		</ol>
	</section>
</main>

<footer class="foot wrap">
	<p>DIDIK Main Bersama · percuma, tanpa iklan, tanpa akaun untuk kanak-kanak.</p>
</footer>

<style>
	.top {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		min-height: 4.4rem;
	}
	.parents {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		font-weight: 800;
		text-decoration: none;
	}
	.hero {
		display: grid;
		grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
		align-items: center;
		gap: 2rem;
		padding-block: 2.5rem 4rem;
	}
	.hero h1 {
		font-size: var(--fs-hero);
		line-height: 1.02;
	}
	.lead {
		margin-top: 1rem;
		max-width: 32rem;
		font-size: var(--fs-lead);
		color: var(--ink-2);
	}
	.enter {
		display: flex;
		gap: 0.7rem;
		margin-top: 1.8rem;
		max-width: 30rem;
	}
	.code {
		flex: 1;
		min-height: 3.75rem;
		font: 600 1.6rem var(--font-display);
		letter-spacing: 0.06em;
		text-align: center;
	}
	.crowd {
		position: relative;
		height: 22rem;
	}
	.didi {
		position: absolute;
		left: 50%;
		top: 50%;
		translate: -50% -50%;
	}
	.pal {
		position: absolute;
	}
	.p0 { left: 6%; top: 12%; }
	.p1 { right: 8%; top: 6%; }
	.p2 { left: 0; bottom: 22%; }
	.p3 { right: 2%; bottom: 26%; }
	.p4 { left: 22%; bottom: 0; }
	.p5 { right: 22%; bottom: 2%; }
	.pal:hover :global(svg) {
		animation: wiggle 0.6s ease-in-out;
	}
	.games {
		padding-block: 3.5rem;
		background: var(--ink);
		color: #fff;
	}
	.games h2 {
		font-size: var(--fs-h1);
	}
	.sub {
		margin-top: 0.4rem;
		color: rgb(255 255 255 / 0.75);
	}
	.worlds {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(min(100%, 17rem), 1fr));
		gap: 0.9rem;
		margin-top: 1.8rem;
		padding-left: var(--gutter);
		padding-right: var(--gutter-r);
		list-style: none;
	}
	.world {
		display: flex;
		align-items: flex-start;
		gap: 0.9rem;
		padding: 1.1rem;
		border-radius: var(--r-lg);
		background: var(--bg);
		color: var(--ink);
		transition: transform var(--t-state) var(--spring);
		animation: rise-in var(--t-enter) var(--ease-out) both;
		animation-delay: calc(var(--i) * 70ms);
	}
	.world:hover {
		transform: translateY(-5px) rotate(-1deg);
	}
	.world:hover :global(.badge) {
		animation: wiggle 0.6s ease-in-out;
	}
	.world h3 {
		font-size: 1.35rem;
	}
	.world p {
		font-weight: 700;
	}
	.world .style {
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		opacity: 0.85;
	}
	.how {
		display: grid;
		gap: 1.6rem;
		padding-block: 4rem;
	}
	.how h2 {
		font-size: var(--fs-h1);
	}
	.steps {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 1.6rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.steps li {
		display: grid;
		gap: 0.5rem;
		align-content: start;
	}
	.steps h3 {
		font-size: 1.35rem;
	}
	.steps p {
		color: var(--ink-2);
	}
	.n {
		display: grid;
		place-items: center;
		width: 2.6rem;
		height: 2.6rem;
		border-radius: 50%;
		background: var(--sun);
		font: 600 1.3rem var(--font-display);
		box-shadow: 0 4px 0 var(--sun-deep);
	}
	.foot {
		padding-block: 2rem 3rem;
		border-top: 2px solid var(--line);
		color: var(--ink-2);
		font-weight: 700;
	}
	@media (max-width: 820px) {
		.hero {
			grid-template-columns: minmax(0, 1fr);
			padding-top: 1.2rem;
		}
		.crowd {
			order: -1;
			height: 15rem;
		}
		.crowd {
			--didi-w: 120px;
		}
		.steps {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
