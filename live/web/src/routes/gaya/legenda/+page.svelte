<!--
	Art review for Legenda Story Mode: the real player screen fed with made-up states, one world and one
	step at a time, plus buttons that play the attack and counterattack animations. No room, no server:
	answer buttons use illustrative local results, never a real room. Not linked from the app (like /gaya).
-->
<script lang="ts">
	import { tick } from 'svelte';
	import { page } from '$app/state';
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person } from '$lib/types';
	import LegendaPlayer from '$lib/games/legenda/LegendaPlayer.svelte';
	import Stage from '$lib/games/legenda/Stage.svelte';
	import { ELEMENTS, type Element } from '$lib/games/legenda/data';

	const WORLDS = [
		{ key: 'chini', foe: 'Pengawal Teratai', title: 'Tasik Chini', boss: 'Naga Chini', intro: 'Kabus pagi menyelubungi tasik teratai.', clear: 'Teratai kembali mekar.' },
		{ key: 'lupar', foe: 'Penjaga Bakau', title: 'Batang Lupar', boss: 'Bujang Senang', intro: 'Senja di sungai Sarawak.', clear: 'Perahu boleh berlayar semula.' },
		{ key: 'larut', foe: 'Roh Paku Pakis', title: 'Hutan Larut', boss: 'Gajah Rimba', intro: 'Hutan hujan yang tua dan tebal.', clear: 'Cahaya menembusi kanopi.' },
		{ key: 'kancil', foe: 'Pelita Sesat', title: 'Rimba Bayangan', boss: 'Sang Kancil Bayangan', intro: 'Bulan ungu di atas rimba.', clear: 'Ilusi pecah.' },
		{ key: 'ledang', foe: 'Bayu Kabus', title: 'Gunung Ledang', boss: 'Penunggu Kabus', intro: 'Jambatan batu di puncak berkabus.', clear: 'Kabus terangkat.' }
	];
	const STEPS = ['select', 'intro', 'travel', 'encounter', 'question', 'unlock', 'gather', 'reveal', 'boss', 'wait', 'fallen', 'worldclear', 'victory'];

	let world = $state(Number(page.url.searchParams.get('world') ?? 0));
	let step = $state(page.url.searchParams.get('step') ?? 'boss');
	let hero = $state(page.url.searchParams.get('hero') ?? 'tuah');
	let element = $state(page.url.searchParams.get('element') ?? 'petir');
	let fullPlayer = $state(false);
	let demoResult = $state<boolean | null>(null);
	let demoAnswered = $state(0);
	let reviewHp = $state(5);
	let reviewHearts = $state(12);
	let reviewEnemy = $state<'idle' | 'beaten'>('idle');
	let reviewRun = 0;
	let reviewText = $state('Naga Chini menjaga tasik. Pilih gerakan untuk melihatnya.');
	async function review(action: 'reveal' | 'idle' | 'counter' | 'defeat' | 'hit', el?: Element) {
		const run = ++reviewRun;
		stage?.cancel();
		reviewEnemy = 'idle';
		stage?.reset();
		if (el) element = el;
		if (action === 'reveal' || action === 'idle') { reviewHp = 5; reviewHearts = 12; }
		await tick();
		if (run !== reviewRun) return;
		if (action === 'reveal') { reviewText = 'Naga Chini muncul dari kabus tasik.'; await stage?.enter(); }
		else if (action === 'counter') {
			reviewText = 'Boss Akan Menyerang!';
			reviewHearts = Math.max(0, reviewHearts - 3);
			await stage?.counter(() => { reviewText = 'Serangan Balas: gelombang Air!'; });
		} else if (action === 'hit') {
			reviewHp = Math.max(0, reviewHp - 1);
			reviewText = el === 'petir' ? 'Petir: kelemahan Naga Chini! Bonus elemen, satu bar sahaja.' : `Serangan ${el}: satu bar.`;
			await stage?.attack(el ?? 'petir', { weak: world === 0 && el === 'petir', finishing: reviewHp === 0 });
			if (run !== reviewRun) return;
			if (reviewHp === 0) { reviewEnemy = 'beaten'; stage?.celebrate(); }
		} else if (action === 'defeat') { reviewHp = 0; reviewEnemy = 'beaten'; stage?.celebrate(); reviewText = 'Boss Dikalahkan! Tasik kembali tenang.'; }
		else reviewText = 'Naga Chini menjaga tasik. Pilih gerakan untuk melihatnya.';
	}
	$effect(() => {
		void world; void hero; void fullPlayer;
		reviewRun++;
		reviewHp = 5; reviewHearts = 12; reviewEnemy = 'idle'; demoResult = null;
	});
	let stage = $state<Stage>();
	// `foe=1..5`: the demo stage fights that small enemy (they take turns standing left and right of the hero) instead of the boss
	const foeAt = Number(page.url.searchParams.get('foe') ?? 0);

	const client = { send: (message: { t: string; a?: unknown; element?: string }) => {
		if (message.t === 'answer') { demoResult = message.a === 'a'; demoAnswered++; }
		if (message.t === 'next') demoResult = null;
		if (message.t === 'element' && message.element) element = message.element;
	}, onFx: () => () => undefined, offset: 0 } as unknown as RoomClient;
	const me = { id: 'p1', name: 'Kancil Pelangi', avatar: 'kancil', colour: 'teal', team: null, online: true, bot: false, approved: true, score: 0 } as Me;
	const people = new Map<string, Person>();
	const question = {
		id: 'q1',
		type: 'single',
		label: 'Pilihan tunggal',
		prompt: 'Haiwan manakah yang mempunyai belalai?',
		image: null,
		timeLimit: 20,
		choices: [
			{ id: 'a', text: 'Gajah' },
			{ id: 'b', text: 'Harimau' },
			{ id: 'c', text: 'Penyu' },
			{ id: 'd', text: 'Kancil' }
		]
	};

	const game = $derived.by(() => {
		const boss = ['boss', 'wait', 'reveal', 'gather', 'worldclear', 'victory'].includes(step) || (step === 'fallen' && world % 2 === 1);
		const real = step === 'boss' ? (demoResult === null ? 'question' : 'result') : step;
		return {
			stage: 'play',
			seat: {
				step: real,
				answered: demoAnswered,
				result: demoResult === null ? undefined : { correct: demoResult, answer: demoResult ? 'a' : 'b', reveal: { correct: ['a'] }, reward: { element, weak: world === 0 && element === 'petir', bossHp: demoResult ? 2 : 3, change: demoResult ? 1 : -3 } },
				question: ['question', 'result'].includes(real) ? question : undefined,
				story: { hero, world, phase: boss ? 'boss' : 'road', cleared: boss ? 5 : 2, hearts: step === 'fallen' ? 0 : demoResult === false ? 6 : demoResult === true ? 10 : 9, elements: boss, element, ev: STEPS.indexOf(step), worlds: [], hits: 12 },
				raid: boss ? { id: 'r1', hp: demoResult === true ? 2 : 3, max: 5, round: 2, members: ['p1', 'p2'], answered: step === 'wait' ? ['p1'] : [], log: [] } : null,
				gather: step === 'gather' ? { behind: 2, ends: Date.now() + 40000 } : undefined
			},
			world: { scene: WORLDS[world], index: world, total: 5, friends: [], party: false, encounters: 5, maxHearts: 12 }
		};
	});
</script>

<svelte:head><title>Legenda · Gaya seni</title></svelte:head>

<nav class="wrap bar" class:over-player={fullPlayer} aria-label="Pilih adegan">
	<label>Dunia <select bind:value={world}>{#each WORLDS as w, i (w.key)}<option value={i}>{i + 1}. {w.title}</option>{/each}</select></label>
	<label>Langkah <select bind:value={step}>{#each STEPS as s (s)}<option>{s}</option>{/each}</select></label>
	<label>Wira <select bind:value={hero}><option value="tuah">Hang Tuah</option><option value="mahsuri">Mahsuri</option></select></label>
	<button class="btn" type="button" onclick={() => fullPlayer = !fullPlayer}>{fullPlayer ? 'Kembali ke gerak pertarungan' : 'Lihat skrin permainan'}</button>
</nav>

{#if fullPlayer}
{#key `${world}:${step}:${hero}:${element}`}
	<LegendaPlayer {client} {game} {me} {people} />
{/key}
{/if}

{#if !fullPlayer}
<section class="wrap moves">
	<h2>Gerak pertarungan</h2>
	<p>Pratonton seni dengan keputusan contoh. Pilih wira dan gerakan, atau buka skrin permainan untuk mencuba jawapan.</p>
	{#key `${world}:${hero}`}
	<div class="stage-box">
		<Stage bind:this={stage} {world} {hero} weapon={element as Element} heroName={hero === 'tuah' ? 'Hang Tuah' : 'Mahsuri'} hearts={reviewHearts} boss={foeAt ? null : { name: WORLDS[world].boss, hp: reviewHp, max: 5 }} foe={foeAt ? { name: WORLDS[world].foe, index: foeAt, total: 5 } : null} enemy={reviewEnemy} />
	</div>
	{/key}
	<p role="status">{reviewText}</p>
	<div class="row">
		{#each ELEMENTS as el (el)}<button type="button" class="btn" onclick={() => review('hit', el)}>Serang: {el}</button>{/each}
		<button type="button" class="btn" onclick={() => review('counter')}>Serangan balas</button>
		{#if world === 0 && !foeAt}
			<button type="button" class="btn" onclick={() => review('reveal')}>Kemunculan Naga</button>
			<button type="button" class="btn" onclick={() => review('idle')}>Tenang / mula semula</button>
			<button type="button" class="btn" onclick={() => review('defeat')}>Boss dikalahkan</button>
		{/if}
	</div>
</section>
{/if}

<style>
	/* In player view the review tools must not cover the question or its banner. */
	.bar.over-player { position: fixed; bottom: 0.5rem; right: 0.5rem; left: auto; width: auto; z-index: 60; padding: 0; }
	.over-player label { display: none; }
	.over-player button { min-height: 32px; padding: 0.4rem 0.65rem; font-size: 0.7rem; }
	.bar {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		padding-block: 1rem;
		font-weight: 800;
	}
	.moves {
		display: grid;
		gap: 0.8rem;
		padding-block: 2rem 4rem;
	}
	.stage-box {
		max-width: 960px;
	}
	.row {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
</style>
