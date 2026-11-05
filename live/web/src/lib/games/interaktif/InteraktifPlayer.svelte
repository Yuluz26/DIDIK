<!--
	Kuiz Interaktif on a child's screen. A candy-floss sky, Didi's cloud trail along the top, and one
	question at a time on a soft card: tap, drag, sort or spell, then Semak. After each answer Didi reacts,
	the stars earned pop in (three for right, fewer for nearly right) and, when it was not right, the right
	answer is shown on the spot. At the end of the trail: a celebration and the stars collected, while the
	others finish.

	Everything here is the room's own state from the server (the seat and the trail); nothing is decided in
	the browser. The look is soft and rounded on purpose: the game screens' pixel frame is set aside here.
-->
<script lang="ts">
	import { fly, scale } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person, PublicQuestion } from '$lib/types';
	import { play } from '$lib/sound';
	import { confetti } from '$lib/confetti';
	import { canSpeak, speak, stopSpeaking } from '$lib/speech';
	import Answer from '$lib/questions/Answer.svelte';
	import Avatar from '$ui/Avatar.svelte';
	import FullscreenToggle from '$ui/FullscreenToggle.svelte';
	import Icon from '$ui/Icon.svelte';
	import SoundToggle from '$ui/SoundToggle.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import Timer from '$ui/Timer.svelte';
	import CloudSky from './CloudSky.svelte';
	import DidiSoft, { type DidiMood } from './DidiSoft.svelte';
	import Trail from './Trail.svelte';

	let {
		client,
		game,
		me
	}: {
		client: RoomClient;
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		game: any;
		me: Me;
		people?: Map<string, Person>;
	} = $props();

	const seat = $derived(game.seat ?? {});
	const step = $derived((seat.step ?? 'wait') as 'wait' | 'question' | 'result' | 'done');
	const world = $derived(game.world ?? {});
	const total = $derived<number>(world.total ?? 0);
	const stars = $derived<number[]>(world.stars ?? []);
	const starSum = $derived(stars.reduce((a, b) => a + b, 0));
	const question = $derived(seat.question as PublicQuestion | undefined);
	const result = $derived(seat.result);
	const number = $derived(step === 'question' ? stars.length + 1 : stars.length);
	const paused = $derived(!!game.clock?.paused);
	const earned = $derived<number>(result?.reward?.stars ?? 0);

	const PRAISE = ['Hebat!', 'Pandainya!', 'Syabas!', 'Betul sekali!', 'Wah, bijak!'];
	const NEARLY = ['Hampir betul!', 'Sikit lagi!'];
	const KIND = ['Tak apa!', 'Cuba lagi nanti!'];
	const pickOf = (list: string[], n: number) => list[n % list.length];

	const mood = $derived<DidiMood>(
		step === 'done' ? 'cheer' : step === 'result' ? (result?.correct ? 'cheer' : earned > 0 ? 'happy' : 'oops') : step === 'question' ? 'think' : 'wave'
	);
	const title = $derived(
		result?.correct ? pickOf(PRAISE, stars.length) : earned > 0 ? pickOf(NEARLY, stars.length) : pickOf(KIND, stars.length)
	);
	const line = $derived(
		result?.correct
			? `Kamu dapat ${earned} bintang!`
			: earned > 0
				? `Sebahagian betul: ${earned} bintang. Ini jawapan yang betul.`
				: 'Ini jawapan yang betul. Jom teruskan!'
	);

	// one celebration for each answer, when it arrives
	let lastSeen = -1;
	$effect(() => {
		if (step !== 'result' || !result || seat.answered === lastSeen) return;
		lastSeen = seat.answered;
		stopSpeaking();
		if (result.correct) {
			play('correct');
			confetti({ count: 50 });
		} else {
			play('almost');
		}
		for (let i = 0; i < earned; i++) setTimeout(() => play('coin'), 420 + i * 220);
	});

	let cheered = false;
	$effect(() => {
		if (step !== 'done' || cheered) return;
		cheered = true;
		play('fanfare');
		confetti({ count: 120, spread: 120 });
	});

	function readAloud(q: PublicQuestion) {
		const options = q.choices?.map((c) => c.text).join(', ');
		speak(options ? `${q.prompt}. ${options}` : q.prompt);
	}

	const full = $derived(total > 0 && starSum === total * 3);

	// 3, 2, 1 before the first question, from the room's clock
	let count = $state(3);
	$effect(() => {
		if (game.stage !== 'intro') return;
		const clock = game.clock;
		let last = -1;
		const update = () => {
			const left = clock?.paused ? (clock.left ?? 0) : Math.max(0, (clock?.deadline ?? 0) - (Date.now() + client.offset));
			const value = Math.min(3, Math.ceil(left / 1000));
			if (value !== last) play(value > 0 ? 'tick' : 'go');
			last = value;
			count = value;
		};
		update();
		const id = setInterval(update, 100);
		return () => clearInterval(id);
	});
</script>

<div class="ik">
	<CloudSky mood={step === 'done' ? 'party' : 'day'} />

	<header class="top">
		<span class="me">
			<span class="face"><Avatar animal={me.avatar} colour={me.colour} skin={me.skin} size={40} /></span>
			<strong>{me.name}</strong>
		</span>
		<div class="trail-wrap">
			{#if total}<Trail {total} {stars} done={step === 'done'} />{/if}
		</div>
		<span class="tally" aria-label="{starSum} bintang">
			<Sticker key="bintang" size={26} alt="" eager />
			{#key starSum}<strong in:scale={{ start: 1.6, duration: 380, easing: backOut }}>{starSum}</strong>{/key}
		</span>
		<span class="tools">
			<FullscreenToggle />
			<SoundToggle />
		</span>
	</header>

	{#if game.stage === 'intro'}
		<main class="stage center">
			<div class="intro card" in:scale={{ start: 0.8, duration: 500, easing: backOut }}>
				<DidiSoft mood="wave" size={120} />
				<p class="hello">Jom main bersama Didi!</p>
				{#key count}
					<span class="count" aria-live="assertive" in:scale={{ start: 1.8, duration: 420, easing: backOut }}>{count > 0 ? count : 'Mula!'}</span>
				{/key}
			</div>
		</main>
	{:else}
		<div class="clock"><Timer clock={game.clock} offset={client.offset} total={game.length ?? 300} compact /></div>

		<main class="stage">
			{#key `${step}-${seat.answered ?? 0}`}
				<div class="slide" in:fly={{ y: 36, duration: 460, easing: backOut, delay: 120 }}>
					{#if step === 'question' && question}
						<section class="card qcard" aria-labelledby="ik-prompt">
							<div class="meta">
								<span class="chip num">Soalan {number}<small>/{total}</small></span>
								<span class="chip kind">{question.label}</span>
								{#if canSpeak()}
									<button type="button" class="listen" onclick={() => readAloud(question)}>
										<Icon name="speak" size={18} /> Dengar
									</button>
								{/if}
							</div>
							<h1 id="ik-prompt" class="prompt">{question.prompt}</h1>
							{#if question.image}<img class="picture" src={question.image} alt="" loading="eager" />{/if}
							<div class="answer">
								<Answer {question} disabled={paused} onanswer={(a) => client.send({ t: 'answer', a })} />
							</div>
						</section>
					{:else if step === 'result' && result}
						<section class="card rcard" class:right={result.correct} aria-live="polite">
							<div class="react">
								<DidiSoft {mood} size={104} />
								<div class="bubble">
									<p class="title">{title}</p>
									<p class="line">{line}</p>
								</div>
							</div>
							<div class="stars" aria-label="{earned} daripada 3 bintang">
								{#each [0, 1, 2] as i (i)}
									<span class="star" class:got={i < earned} style:--i={i}>
										<Sticker key="bintang" size={54} alt="" eager />
									</span>
								{/each}
							</div>
							{#if !result.correct && question}
								<div class="reveal">
									<p class="reveal-title">{question.prompt}</p>
									<Answer {question} disabled mine={result.answer} reveal={result.reveal} onanswer={() => {}} />
								</div>
							{/if}
							<button type="button" class="btn btn--big go" onclick={() => client.send({ t: 'next' })}>
								{result.reward?.last ? 'Lihat hadiah' : 'Teruskan'} <Icon name="next" />
							</button>
						</section>
					{:else if step === 'done'}
						<section class="card done" aria-live="polite">
							<div class="prize" aria-hidden="true">
								<span class="p1"><Sticker key={full ? 'mahkota' : 'piala'} size={92} alt="" eager /></span>
								<span class="p2"><Sticker key="mercun" size={56} alt="" eager /></span>
								<span class="p3"><Sticker key="bintang-bersinar" size={48} alt="" eager /></span>
							</div>
							<DidiSoft mood="cheer" size={120} />
							<h1>Tahniah, {me.name}!</h1>
							<p class="sum"><Sticker key="bintang" size={40} alt="" eager /> <strong>{starSum}</strong> / {total * 3} bintang</p>
							<p class="note">{full ? 'Semua bintang! Kamu memang hebat.' : 'Kamu sudah sampai ke hujung denai Didi.'}</p>
							<p class="wait">
								{world.finished ?? 1} daripada {world.players ?? 1} kawan sudah sampai. Tunggu yang lain, ya!
							</p>
						</section>
					{:else}
						<section class="card center-card"><DidiSoft mood="wave" size={110} /><p class="wait">Didi sedang menyediakan soalan kamu…</p></section>
					{/if}
				</div>
			{/key}
		</main>
	{/if}

	{#if paused && game.stage !== 'intro'}
		<div class="pause" transition:scale={{ start: 0.9, duration: 260 }} role="status">
			<div class="card pause-card">
				<DidiSoft mood="think" size={96} />
				<p class="title">Rehat sekejap</p>
				<p>Cikgu atau ibu bapa menekan Rehat. Kita sambung nanti!</p>
			</div>
		</div>
	{/if}
</div>

<style>
	/* The soft, rounded set of the game screens' own variables, for everything inside. */
	.ik {
		--edge: #d9c8f0;
		--r-sm: 12px;
		--r-md: 18px;
		--r-lg: 26px;
		--r-pill: 999px;
		--font-display: 'Fredoka Variable', ui-rounded, system-ui, sans-serif;
		--lift: 0 5px 0 var(--edge);
		--lift-low: 0 4px 0 var(--edge);
		--card-shadow: 0 6px 0 #e6dbf6, 0 18px 40px rgb(110 80 160 / 0.14);
		--ik-ink: #2c2340;
		position: relative;
		min-height: 100dvh;
		color: var(--ik-ink);
		isolation: isolate;
	}
	.top,
	.stage,
	.clock {
		position: relative;
		z-index: 1;
	}
	.top {
		position: sticky;
		top: 0;
		z-index: 10;
		display: grid;
		grid-template-columns: auto minmax(0, 1fr) auto auto;
		align-items: center;
		gap: 0.6rem;
		padding: calc(0.5rem + env(safe-area-inset-top, 0px)) var(--gutter-r) 0.5rem var(--gutter);
		background: linear-gradient(180deg, rgb(255 240 248 / 0.92), rgb(255 240 248 / 0.65) 70%, transparent);
		backdrop-filter: blur(6px);
	}
	.me {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		max-width: 11rem;
		padding: 0.2rem 0.7rem 0.2rem 0.2rem;
		border-radius: 999px;
		background: #fff;
		box-shadow: 0 3px 0 #ead9f7;
	}
	.face {
		display: grid;
		place-items: center;
		width: 2.4rem;
		height: 2.4rem;
		overflow: hidden;
		border-radius: 50%;
		background: #f5ecff;
	}
	.me strong {
		overflow: hidden;
		font: 600 1rem var(--font-display);
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.trail-wrap {
		min-width: 0;
	}
	.tally {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		min-height: 2.75rem;
		padding: 0 0.85rem 0 0.55rem;
		border-radius: 999px;
		background: #fff7d6;
		box-shadow: 0 3px 0 #f1d98b;
		font: 600 1.25rem var(--font-display);
	}
	.tools {
		display: flex;
		gap: 0.3rem;
	}
	.clock {
		width: min(100% - 2 * var(--gutter), 46rem);
		margin: 0.2rem auto 0;
	}
	.stage {
		display: grid;
		justify-items: center;
		padding: 0.8rem var(--gutter-r) calc(9rem + env(safe-area-inset-bottom, 0px)) var(--gutter);
	}
	.stage.center {
		align-content: center;
		min-height: 70dvh;
	}
	.slide {
		width: min(100%, 46rem);
	}
	.card {
		position: relative;
		display: grid;
		gap: 1rem;
		padding: clamp(1rem, 0.6rem + 2vw, 1.6rem);
		border-radius: 30px;
		background: #fff;
		box-shadow:
			0 7px 0 #e6dbf6,
			0 22px 46px rgb(110 80 160 / 0.16),
			inset 0 -4px 0 rgb(240 232 252 / 0.9);
	}
	.intro {
		justify-items: center;
		width: min(100%, 26rem);
		text-align: center;
	}
	.hello {
		font: 600 1.5rem var(--font-display);
		color: #5b3e99;
	}
	.count {
		display: grid;
		place-items: center;
		width: 6rem;
		height: 6rem;
		border-radius: 50%;
		background: linear-gradient(135deg, #ff7eb0, #ffb36e);
		box-shadow: 0 6px 0 #d9567f;
		color: #fff;
		font: 600 2.6rem var(--font-display);
	}
	.meta {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.45rem;
	}
	.chip {
		display: inline-flex;
		align-items: baseline;
		gap: 0.1rem;
		padding: 0.35rem 0.8rem;
		border-radius: 999px;
		font: 600 0.92rem var(--font-display);
	}
	.chip.num {
		background: linear-gradient(135deg, #ff7eb0, #ff9f6e);
		color: #fff;
		box-shadow: 0 3px 0 #d9567f;
	}
	.chip.num small {
		opacity: 0.85;
	}
	.chip.kind {
		background: #efe6ff;
		color: #5b3e99;
	}
	.listen {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		min-height: 2.6rem;
		margin-left: auto;
		padding: 0 0.95rem;
		border: 0;
		border-radius: 999px;
		background: #dff3ff;
		color: #1d5a99;
		font: 600 0.95rem var(--font-display);
		box-shadow: 0 3px 0 #a9d5f5;
		cursor: pointer;
	}
	.listen:active {
		transform: translateY(2px);
		box-shadow: 0 1px 0 #a9d5f5;
	}
	.prompt {
		font: 600 clamp(1.35rem, 1.05rem + 1.5vw, 2rem) / 1.25 var(--font-display);
		text-wrap: balance;
	}
	.picture {
		max-width: 100%;
		max-height: 30vh;
		justify-self: center;
		border-radius: 20px;
		object-fit: contain;
	}
	/* the answer tiles in the soft palette: pastel with dark words */
	.answer :global(.tiles .tile),
	.reveal :global(.tiles .tile) {
		--on: var(--ik-ink);
		border: 3px solid var(--shade);
		border-radius: 22px;
		box-shadow:
			0 6px 0 var(--shade),
			0 12px 20px rgb(110 80 160 / 0.12);
	}
	.answer :global(.tiles .tile.t0),
	.reveal :global(.tiles .tile.t0) {
		--c: #ffc2d4;
		--shade: #ec8fac;
	}
	.answer :global(.tiles .tile.t1),
	.reveal :global(.tiles .tile.t1) {
		--c: #b6ecdf;
		--shade: #5fc0a6;
	}
	.answer :global(.tiles .tile.t2),
	.reveal :global(.tiles .tile.t2) {
		--c: #ffe596;
		--shade: #e8b33a;
	}
	.answer :global(.tiles .tile.t3),
	.reveal :global(.tiles .tile.t3) {
		--c: #c4dcff;
		--shade: #7aa6ea;
	}
	.answer :global(.tiles .tile.t4),
	.reveal :global(.tiles .tile.t4) {
		--c: #daf3b2;
		--shade: #95c75b;
	}
	.answer :global(.tiles .tile.t5),
	.reveal :global(.tiles .tile.t5) {
		--c: #e2d2ff;
		--shade: #a487e8;
	}
	.answer :global(.tiles .tile .letter),
	.reveal :global(.tiles .tile .letter) {
		border-radius: 50%;
		background: rgb(255 255 255 / 0.7);
		color: var(--ik-ink);
	}
	.answer :global(.btn--big),
	.go {
		border-radius: 999px;
	}
	.rcard {
		justify-items: center;
		text-align: center;
	}
	.rcard.right {
		background: linear-gradient(180deg, #fffbe8, #fff 45%);
	}
	.react {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: center;
		gap: 0.6rem 1rem;
	}
	.bubble {
		position: relative;
		max-width: 22rem;
		padding: 0.8rem 1.1rem;
		border-radius: 22px;
		background: #f6efff;
		text-align: left;
	}
	.bubble::before {
		content: '';
		position: absolute;
		left: -9px;
		top: 50%;
		border: 10px solid transparent;
		border-right-color: #f6efff;
		border-left: 0;
		transform: translateY(-50%);
	}
	.title {
		font: 600 clamp(1.6rem, 1.2rem + 1.6vw, 2.3rem) / 1.1 var(--font-display);
	}
	.rcard.right .title {
		color: #d9467f;
	}
	.line {
		font-weight: 800;
	}
	.stars {
		display: flex;
		gap: 0.4rem;
	}
	.star {
		filter: grayscale(1) opacity(0.25);
		transform: scale(0.8);
	}
	.star.got {
		filter: none;
		animation: star-in 520ms var(--spring) both;
		animation-delay: calc(400ms + var(--i) * 220ms);
	}
	.star:nth-child(2) {
		transform: translateY(-10px) scale(0.8);
	}
	.star.got:nth-child(2) {
		--lift-y: -10px;
	}
	.reveal {
		display: grid;
		gap: 0.6rem;
		width: 100%;
		padding: 0.9rem;
		border-radius: 22px;
		background: #faf7ff;
		text-align: left;
	}
	.reveal-title {
		font: 600 1.05rem var(--font-display);
	}
	.go {
		width: min(100%, 20rem);
	}
	.done {
		justify-items: center;
		padding-top: 2.6rem;
		text-align: center;
		overflow: hidden;
	}
	.done h1 {
		font: 600 clamp(1.8rem, 1.3rem + 2vw, 2.6rem) / 1.1 var(--font-display);
		color: #d9467f;
	}
	.prize {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}
	.prize span {
		position: absolute;
		animation: pop-in 700ms var(--spring) both;
	}
	.p1 {
		top: 0.6rem;
		right: 1rem;
		animation-delay: 300ms !important;
	}
	.p2 {
		top: 1.2rem;
		left: 1rem;
		animation-delay: 500ms !important;
	}
	.p3 {
		bottom: 1rem;
		right: 1.6rem;
		animation-delay: 700ms !important;
	}
	.sum {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		padding: 0.4rem 1.1rem 0.4rem 0.6rem;
		border-radius: 999px;
		background: #fff7d6;
		box-shadow: 0 4px 0 #f1d98b;
		font: 600 1.3rem var(--font-display);
	}
	.sum strong {
		font-size: 1.8rem;
	}
	.note {
		font-weight: 800;
	}
	.wait {
		color: #6a5a86;
		font-weight: 800;
	}
	.center-card {
		justify-items: center;
		text-align: center;
	}
	.pause {
		position: fixed;
		inset: 0;
		z-index: 40;
		display: grid;
		place-items: center;
		padding: 1rem;
		background: rgb(60 40 90 / 0.3);
		backdrop-filter: blur(3px);
	}
	.pause-card {
		justify-items: center;
		max-width: 22rem;
		text-align: center;
	}
	@keyframes star-in {
		0% {
			transform: translateY(var(--lift-y, 0)) scale(0) rotate(-40deg);
		}
		100% {
			transform: translateY(var(--lift-y, 0)) scale(1) rotate(0deg);
		}
	}
	@media (max-width: 640px) {
		.top {
			grid-template-columns: auto minmax(0, 1fr) auto;
			grid-template-areas: 'me tally tools' 'trail trail trail';
			gap: 0.35rem 0.5rem;
		}
		.me {
			grid-area: me;
		}
		.tally {
			grid-area: tally;
			justify-self: end;
		}
		.tools {
			grid-area: tools;
		}
		.trail-wrap {
			grid-area: trail;
		}
		.me strong {
			max-width: 6.5rem;
		}
		.card {
			border-radius: 24px;
		}
		.bubble::before {
			display: none;
		}
	}
</style>
