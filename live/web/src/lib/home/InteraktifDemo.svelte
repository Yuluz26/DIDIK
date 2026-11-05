<!--
	A taste of Kuiz Interaktif on the front page: three hands-on questions (count, spell, sort) played right
	here, with the same answer pieces a child uses in a room. Nothing is sent anywhere: the three questions
	and their answers live in this file, and it is checked here. After each answer Didi reacts and the
	stars pop in; then the next question, round and round.
-->
<script lang="ts">
	import { fly, scale } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import { play } from '$lib/sound';
	import type { PublicQuestion, Reveal } from '$lib/types';
	import Answer from '$lib/questions/Answer.svelte';
	import Icon from '$ui/Icon.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import DidiSoft from '$lib/games/interaktif/DidiSoft.svelte';

	interface Demo {
		question: PublicQuestion;
		reveal: Reveal & { word?: string };
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		check: (answer: any) => number;
	}

	const base = { image: null, timeLimit: 60 };
	const DEMOS: Demo[] = [
		{
			question: { ...base, id: 'demo-kira', type: 'count', label: 'Kira dan masukkan', prompt: 'Masukkan 3 biji epal ke dalam bakul.', sticker: 'epal', place: 'bakul', supply: 7 },
			reveal: { correct: 3 },
			check: (n: number) => (n === 3 ? 1 : 0)
		},
		{
			question: {
				...base,
				id: 'demo-eja',
				type: 'spell',
				label: 'Susun huruf',
				prompt: 'Eja nama haiwan ini.',
				sticker: 'ikan',
				length: 4,
				tiles: [
					{ id: 'a', ch: 'a' },
					{ id: 'k', ch: 'k' },
					{ id: 'n', ch: 'n' },
					{ id: 'i', ch: 'i' }
				]
			},
			reveal: { correct: ['i', 'k', 'a', 'n'], word: 'ikan' },
			check: (ids: string[]) => ids.filter((id, i) => id === ['i', 'k', 'a', 'n'][i]).length / 4
		},
		{
			question: {
				...base,
				id: 'demo-isih',
				type: 'sort',
				label: 'Isih kumpulan',
				prompt: 'Haiwan ini tinggal di darat atau di laut?',
				groups: [
					{ id: 'darat', name: 'Darat', sticker: 'pokok' },
					{ id: 'laut', name: 'Laut', sticker: 'bot' }
				],
				items: [
					{ id: 'kucing', text: 'Kucing', sticker: 'kucing' },
					{ id: 'sotong', text: 'Sotong', sticker: 'sotong' },
					{ id: 'arnab', text: 'Arnab', sticker: 'arnab' },
					{ id: 'ikan', text: 'Ikan', sticker: 'ikan' }
				]
			},
			reveal: { correct: { kucing: 'darat', sotong: 'laut', arnab: 'darat', ikan: 'laut' } },
			check: (map: Record<string, string>) =>
				Object.entries({ kucing: 'darat', sotong: 'laut', arnab: 'darat', ikan: 'laut' }).filter(([k, v]) => map[k] === v).length / 4
		}
	];

	let at = $state(0);
	let round = $state(0);
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let given = $state<{ answer: any; fraction: number } | null>(null);
	let total = $state(0);

	const demo = $derived(DEMOS[at]);
	const earned = $derived(given ? (given.fraction === 1 ? 3 : given.fraction >= 0.5 ? 2 : given.fraction > 0 ? 1 : 0) : 0);

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	function answer(value: any) {
		const fraction = demo.check(value);
		given = { answer: value, fraction };
		const stars = fraction === 1 ? 3 : fraction >= 0.5 ? 2 : fraction > 0 ? 1 : 0;
		total += stars;
		play(fraction === 1 ? 'correct' : 'almost');
		for (let i = 0; i < stars; i++) setTimeout(() => play('coin'), 380 + i * 200);
	}

	function next() {
		play('pop');
		given = null;
		at = (at + 1) % DEMOS.length;
		round++;
	}
</script>

<div class="demo">
	<div class="bar">
		<span class="try">Cuba sekarang</span>
		<span class="dots" aria-label="Soalan {at + 1} daripada {DEMOS.length}">
			{#each DEMOS as _, i (i)}<span class="dot" class:on={i === at} class:past={i < at}></span>{/each}
		</span>
		<span class="tally" aria-label="{total} bintang"><Sticker key="bintang" size={22} alt="" /> {total}</span>
	</div>
	{#key round}
		<div class="body" in:fly={{ y: 24, duration: 420, easing: backOut }}>
			<p class="chip">{demo.question.label}</p>
			<p class="prompt">{demo.question.prompt}</p>
			{#if !given}
				<Answer question={demo.question} onanswer={answer} />
			{:else}
				<div class="react" in:scale={{ start: 0.8, duration: 380, easing: backOut }}>
					<DidiSoft mood={given.fraction === 1 ? 'cheer' : earned ? 'happy' : 'oops'} size={86} />
					<div>
						<p class="title">{given.fraction === 1 ? 'Hebat!' : earned ? 'Hampir betul!' : 'Tak apa!'}</p>
						<p class="stars" aria-label="{earned} bintang">
							{#each [0, 1, 2] as i (i)}<span class="star" class:got={i < earned} style:--i={i}><Sticker key="bintang" size={34} alt="" /></span>{/each}
						</p>
					</div>
				</div>
				{#if given.fraction < 1}
					<Answer question={demo.question} disabled mine={given.answer} reveal={demo.reveal} onanswer={() => {}} />
				{/if}
				<button type="button" class="btn btn--big next" onclick={next}>Soalan seterusnya <Icon name="next" /></button>
			{/if}
		</div>
	{/key}
</div>

<style>
	.demo {
		--edge: #d9c8f0;
		--r-sm: 12px;
		--r-md: 16px;
		--r-lg: 22px;
		--r-pill: 999px;
		--card: #fff;
		display: grid;
		gap: 0.8rem;
		padding: 1rem;
		border-radius: 30px;
		background: #fff;
		color: #2c2340;
		box-shadow:
			0 8px 0 #e6dbf6,
			0 26px 50px rgb(60 30 110 / 0.25);
	}
	.bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.6rem;
	}
	.try {
		padding: 0.3rem 0.8rem;
		border-radius: 999px;
		background: linear-gradient(135deg, #ff7eb0, #ffb36e);
		color: #fff;
		font: 600 0.88rem var(--font-display);
		box-shadow: 0 3px 0 #d9567f;
	}
	.dots {
		display: flex;
		gap: 0.35rem;
	}
	.dot {
		width: 0.7rem;
		height: 0.7rem;
		border-radius: 50%;
		background: #e8def6;
		transition: transform 300ms var(--spring);
	}
	.dot.past {
		background: #ffc93c;
	}
	.dot.on {
		background: #b98cff;
		transform: scale(1.3);
	}
	.tally {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		padding: 0.2rem 0.7rem 0.2rem 0.4rem;
		border-radius: 999px;
		background: #fff7d6;
		font: 600 1.05rem var(--font-display);
	}
	.body {
		display: grid;
		gap: 0.7rem;
	}
	.chip {
		justify-self: start;
		padding: 0.25rem 0.7rem;
		border-radius: 999px;
		background: #efe6ff;
		color: #5b3e99;
		font: 600 0.82rem var(--font-display);
	}
	.prompt {
		font: 600 clamp(1.2rem, 1rem + 0.8vw, 1.5rem) / 1.25 var(--font-display);
	}
	.react {
		display: flex;
		align-items: center;
		gap: 0.8rem;
		padding: 0.5rem 0.8rem;
		border-radius: 22px;
		background: #f6efff;
	}
	.title {
		font: 600 1.6rem/1.1 var(--font-display);
		color: #d9467f;
	}
	.stars {
		display: flex;
		gap: 0.2rem;
	}
	.star {
		filter: grayscale(1) opacity(0.25);
	}
	.star.got {
		filter: none;
		animation: pop-in 480ms var(--spring) both;
		animation-delay: calc(350ms + var(--i) * 200ms);
	}
	.next {
		width: 100%;
		border-radius: 999px;
	}
</style>
