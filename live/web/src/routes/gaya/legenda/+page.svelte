<!--
	Art review for Legenda Story Mode: the real player screen fed with made-up states, one world and one
	step at a time, plus buttons that play the attack and counterattack animations. No room, no server:
	the answer buttons here do nothing. Not linked from the app (like /gaya).
-->
<script lang="ts">
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
	let stage = $state<Stage>();

	const client = { send: () => undefined, onFx: () => () => undefined, offset: 0 } as unknown as RoomClient;
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
		const real = step === 'boss' ? 'question' : step;
		return {
			stage: 'play',
			seat: {
				step: real,
				answered: 0,
				question: real === 'question' ? question : undefined,
				story: { hero, world, phase: boss ? 'boss' : 'road', cleared: boss ? 5 : 2, hearts: step === 'fallen' ? 0 : 9, elements: boss, element: 'petir', ev: STEPS.indexOf(step), worlds: [], hits: 12 },
				raid: boss ? { id: 'r1', hp: 3, max: 5, round: 2, members: ['p1', 'p2'], answered: step === 'wait' ? ['p1'] : [], log: [] } : null,
				gather: step === 'gather' ? { behind: 2, ends: Date.now() + 40000 } : undefined
			},
			world: { scene: WORLDS[world], index: world, total: 5, friends: [], party: false, encounters: 5, maxHearts: 12 }
		};
	});
</script>

<svelte:head><title>Legenda · Gaya seni</title></svelte:head>

<nav class="wrap bar" aria-label="Pilih adegan">
	<label>Dunia <select bind:value={world}>{#each WORLDS as w, i (w.key)}<option value={i}>{i + 1}. {w.title}</option>{/each}</select></label>
	<label>Langkah <select bind:value={step}>{#each STEPS as s (s)}<option>{s}</option>{/each}</select></label>
	<label>Wira <select bind:value={hero}><option value="tuah">Hang Tuah</option><option value="mahsuri">Mahsuri</option></select></label>
</nav>

{#key `${world}:${step}:${hero}`}
	<LegendaPlayer {client} {game} {me} {people} />
{/key}

<section class="wrap moves">
	<h2>Gerak pertarungan</h2>
	<div class="stage-box">
		<Stage bind:this={stage} {world} {hero} heroName="Hang Tuah" hearts={9} boss={{ name: WORLDS[world].boss, hp: 3, max: 5 }} enemy="idle" />
	</div>
	<div class="row">
		{#each ELEMENTS as el (el)}<button type="button" class="btn" onclick={() => stage?.attack(el as Element, { weak: el === 'petir', healed: true })}>Serang: {el}</button>{/each}
		<button type="button" class="btn" onclick={() => stage?.counter()}>Serangan balas</button>
	</div>
</section>

<style>
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
