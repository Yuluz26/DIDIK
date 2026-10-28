<!--
	A child's screen in Legenda Story Mode. The server's step (game.seat.step) chooses what is shown;
	this screen only plays the cinematic for that step and sends `next` when it ends (or when the child
	taps Teruskan), naming the step's `ev` so a double tap never skips one.

	Nothing here walks or dodges. The child chooses a hero, reads, answers, picks an element at the
	boss, and watches: the attack or the counterattack plays only once the server has checked the answer.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person } from '$lib/types';
	import { confetti } from '$lib/confetti';
	import Answer from '$lib/questions/Answer.svelte';
	import QuestionCard from '$lib/questions/QuestionCard.svelte';
	import Icon from '$ui/Icon.svelte';
	import Hud from '../Hud.svelte';
	import HeroSelect from './HeroSelect.svelte';
	import Stage from './Stage.svelte';
	import {
		ELEMENTS,
		ELEMENT_NAME,
		HEROES,
		elementIcon,
		elementUrls,
		heartsText,
		heroArt,
		preload,
		reducedMotion,
		symbol,
		worldUrls,
		battleBg,
		bossArt,
		field,
		type Element
	} from './data';
	import { sfx } from './sfx';

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let { client, game, me, people }: { client: RoomClient; game: any; me: Me; people: Map<string, Person> } = $props();

	const seat = $derived(game.seat ?? {});
	const step = $derived((seat.step as string) ?? 'wait');
	const story = $derived(seat.story ?? {});
	const scene = $derived(game.world?.scene ?? {});
	const worldIndex = $derived<number>(game.world?.index ?? 0);
	const total = $derived<number>(game.world?.total ?? 5);
	const encounters = $derived<number>(game.world?.encounters ?? 5);
	const raid = $derived(seat.raid);
	const hero = $derived<string>(story.hero ?? 'tuah');
	const heroInfo = $derived(HEROES.find((h) => h.key === hero) ?? HEROES[0]);
	const friends = $derived((game.world?.friends ?? []) as { id: string; hero: string | null; hearts: number; step: string }[]);
	const boss = $derived(story.phase === 'boss');
	const question = $derived(seat.question);
	const result = $derived(seat.result);

	let stage = $state<Stage>();
	let wipe = $state<HTMLDivElement>();
	let still = $state(false);
	let animating = $state(false);
	let ready = $state(false);
	let lastAnswered = -1;
	let lastStepKey = '';
	let timer: ReturnType<typeof setTimeout> | null = null;

	onMount(() => {
		still = reducedMotion();
		const off = client.onFx((fx) => {
			if (fx.kind === 'story-hit' && fx.player !== me.id && raid && fx.raid === raid.id) stage?.friendHit(fx.element);
		});
		return () => {
			off();
			if (timer) clearTimeout(timer);
		};
	});

	// Load the world's art before its first scene; the elements' art once they are near.
	const artKey = $derived(`${worldIndex}:${story.hero ?? ''}`);
	const elementsNear = $derived((story.cleared ?? 0) >= 3 || !!story.elements);
	$effect(() => {
		const key = artKey;
		ready = false;
		// Never hold the scene back for a slow image: after a few seconds it draws as it arrives.
		const fallback = setTimeout(() => (ready = true), 3000);
		void preload(worldUrls(worldIndex, story.hero ?? null)).then(() => {
			if (key === artKey) ready = true;
		});
		return () => clearTimeout(fallback);
	});
	$effect(() => {
		if (elementsNear) void preload(elementUrls());
	});

	function next() {
		if (timer) clearTimeout(timer);
		timer = null;
		client.send({ t: 'next', ev: story.ev });
	}

	function later(ms: number) {
		if (timer) clearTimeout(timer);
		timer = setTimeout(next, still ? Math.min(ms, 1800) : ms);
	}

	// Each new step: play its cinematic, and move on by itself after it.
	$effect(() => {
		const key = `${step}:${story.ev}`;
		if (key === lastStepKey) return;
		lastStepKey = key;
		if (timer) clearTimeout(timer);
		timer = null;
		if (step === 'intro') {
			stage?.reset();
			sfx('unlock', 0.5);
			void playWipe();
			later(4600);
		} else if (step === 'travel') later(2800);
		else if (step === 'encounter') {
			void stage?.enter();
			later(1700);
		} else if (step === 'clear') {
			sfx('correct', 0.5);
			later(1800);
		} else if (step === 'unlock') {
			sfx('unlock');
			later(4200);
		} else if (step === 'reveal') {
			stage?.reset();
			later(4000);
		} else if (step === 'worldclear') {
			stage?.celebrate();
			sfx('unlock');
			confetti({ count: 90 });
			later(6500);
		} else if (step === 'fallen') {
			stage?.fall();
		} else if (step === 'victory') {
			stage?.celebrate();
			confetti({ count: 160, spread: 1.3 });
		} else if (step === 'question') {
			stage?.reset();
		}
	});

	// A checked answer: the hero's attack or the enemy's counterattack, then on to the next step.
	$effect(() => {
		if (step !== 'result' || !result || seat.answered === lastAnswered) return;
		lastAnswered = seat.answered;
		const reward = result.reward ?? {};
		animating = true;
		const run = async () => {
			if (result.correct) {
				sfx(boss ? 'hit' : 'correct');
				await stage?.attack(boss ? (reward.element as Element) : null, { weak: reward.weak, finishing: reward.bossHp === 0, healed: reward.change > 0 });
				if (reward.change > 0) sfx('heal', 0.4);
			} else {
				sfx('wrong');
				await stage?.counter();
			}
			animating = false;
			// A wrong answer stays on screen with the right answer shown until the child taps on.
			if (result.correct) later(1100);
			else later(9000);
		};
		void run();
	});

	/** The world transition: the twelve alpha frames supplied for it, over the new world. */
	async function playWipe() {
		if (still || !wipe) return;
		wipe.style.opacity = '1';
		for (let frame = 0; frame < 12; frame++) {
			wipe.style.backgroundPosition = `${(frame % 4) * 33.333}% ${Math.floor(frame / 4) * 50}%`;
			await new Promise((r) => setTimeout(r, 70));
		}
		wipe.style.opacity = '0';
	}

	/** Alt+1 to Alt+5 pick an element at the boss (plain digits already answer the question). */
	function onkey(e: KeyboardEvent) {
		if (!e.altKey || e.ctrlKey || e.metaKey || step !== 'question' || !boss || !story.elements) return;
		const el = ELEMENTS[Number(e.code.replace('Digit', '')) - 1];
		if (!el) return;
		e.preventDefault();
		chooseElement(el);
	}

	function chooseElement(el: Element) {
		if (el === story.element) return;
		sfx('click', 0.5);
		client.send({ t: 'element', element: el });
	}

	function send(a: unknown) {
		client.send({ t: 'answer', a, ev: story.ev, el: boss ? story.element : undefined });
	}

	const enemyState = $derived(
		step === 'clear' ? 'gone' : step === 'worldclear' || step === 'victory' ? 'beaten' : step === 'encounter' ? 'enter' : 'idle'
	);
	const showEnemy = $derived(['encounter', 'question', 'result', 'clear', 'wait', 'fallen', 'worldclear'].includes(step));
	const stageMode = $derived(step === 'travel' ? 'travel' : ['intro', 'unlock', 'gather', 'reveal', 'victory'].includes(step) ? 'scenery' : 'battle');
	// The enemy being fought: an enemy cleared by this answer still counts as the one on screen.
	const foeIndex = $derived(
		Math.min(encounters, (story.cleared ?? 0) + (step === 'clear' || (step === 'result' && result?.correct) ? 0 : 1))
	);
	const answered = $derived(raid ? raid.answered.length : 0);
	const fighting = $derived(raid ? raid.members.length : 1);
</script>

<svelte:window onkeydown={onkey} />

<Hud {me} score={game.score ?? 0} />

{#if step === 'select'}
	<main class="wrap story"><HeroSelect onpick={(h) => client.send({ t: 'hero', hero: h, ev: story.ev })} /></main>
{:else if game.stage === 'intro'}
	<main class="wrap story"><p class="loading">Membuka kitab legenda…</p></main>
{:else}
	<main class="wrap story step-{step}">
		<div class="frame" style:--ar={field(worldIndex).ar}>
			<Stage
				bind:this={stage}
				world={worldIndex}
				{hero}
				heroName={me.name}
				hearts={story.hearts ?? 12}
				maxHearts={game.world?.maxHearts ?? 12}
				foe={!boss ? { name: scene.foe ?? 'Musuh', index: foeIndex, total: encounters } : null}
				boss={boss && raid ? { name: scene.boss, hp: raid.hp, max: raid.max, subtitle: scene.title } : null}
				elements={story.hero ? { unlocked: !!story.elements, selected: story.element ?? 'api', disabled: step !== 'question' || !boss, onpick: chooseElement } : null}
				enemy={showEnemy ? enemyState : 'none'}
				friends={friends.filter((f) => f.step !== 'select')}
				mode={stageMode}
				dim={['intro', 'unlock', 'gather', 'fallen', 'reveal', 'victory'].includes(step)}
			/>

			{#if step === 'intro'}
				<div class="overlay title-card" role="status">
					<img class="emblem" src={symbol(worldIndex)} alt="" />
					<p class="kicker">Dunia {worldIndex + 1} / {total}</p>
					<h2>{scene.title}</h2>
					<p class="story-line">{scene.intro}</p>
					<button type="button" class="skip" onclick={next}>Teruskan <Icon name="next" size={18} /></button>
				</div>
			{:else if step === 'travel'}
				<div class="overlay caption" role="status">
					<p>{heroInfo.name} meneruskan perjalanan… <span>Musuh {foeIndex} / {encounters}</span></p>
				</div>
			{:else if step === 'encounter'}
				<div class="overlay banner warn" role="status"><p>Musuh muncul!</p></div>
			{:else if step === 'clear'}
				<div class="overlay banner good" role="status"><p>Musuh tewas! {story.cleared} / {encounters}</p></div>
			{:else if step === 'unlock'}
				<div class="overlay unlock" role="status">
					<p class="kicker">Lima musuh ditewaskan</p>
					<h2>Senjata elemen terbuka!</h2>
					<ul class="orbs">
						{#each ELEMENTS as el, i (el)}
							<li style:--i={i}><img src={elementIcon(el)} alt="" /><span>{ELEMENT_NAME[el]}</span></li>
						{/each}
					</ul>
					<p class="story-line">Pilih elemen sebelum menjawab soalan boss. Jawapan betul melancarkan seranganmu.</p>
					<button type="button" class="skip" onclick={next}>Teruskan <Icon name="next" size={18} /></button>
				</div>
			{:else if step === 'gather'}
				<div class="overlay unlock" role="status">
					<p class="kicker">Pintu boss</p>
					<h2>Menunggu kawan</h2>
					<p class="story-line">
						{seat.gather?.behind
							? `${seat.gather.behind} kawan masih dalam perjalanan. Kita lawan ${scene.boss} bersama-sama!`
							: 'Bersedia…'}
					</p>
				</div>
			{:else if step === 'reveal'}
				<div class="overlay boss-reveal" role="status">
					<img class="reveal-bg" src={battleBg(worldIndex)} alt="" />
					<img class="reveal-boss" src={bossArt(worldIndex)} alt="" />
					<div class="nameplate">
						<p class="kicker">Penjaga {scene.title}</p>
						<h2>{scene.boss}</h2>
						<p>Lima bar kuasa. Setiap jawapan betul membuang satu bar.</p>
					</div>
					<button type="button" class="skip" onclick={next}>Lawan! <Icon name="next" size={18} /></button>
				</div>
			{:else if step === 'wait'}
				<div class="overlay caption" role="status">
					<p>Seranganmu sudah dihantar! Menunggu kawan menjawab… <span>{answered} / {fighting}</span></p>
				</div>
			{:else if step === 'fallen'}
				<div class="overlay unlock fallen" role="alert">
					<h2>{heroInfo.name} tumbang!</h2>
					<p class="story-line">
						Jangan risau. Kamu sambung di sini dengan enam hati penuh{boss ? ', dan kerosakan pada boss kekal.' : '.'}
					</p>
					<button type="button" class="btn btn--sun btn--big" onclick={() => client.send({ t: 'retry', ev: story.ev })}>Cuba lagi</button>
				</div>
			{:else if step === 'worldclear'}
				<div class="overlay title-card clear" role="status">
					<img class="emblem" src={symbol(worldIndex)} alt="" />
					<p class="kicker">Dunia dibebaskan</p>
					<h2>{scene.title}</h2>
					<p class="story-line">{scene.clear}</p>
					<button type="button" class="btn btn--sun btn--big" onclick={next}>{worldIndex + 1 < total ? 'Dunia seterusnya' : 'Penamat'} <Icon name="next" /></button>
				</div>
			{:else if step === 'victory'}
				<div class="overlay title-card victory" role="status">
					<img class="victor" src={heroArt(hero, 'victory')} alt="" />
					<p class="kicker">Tamat · Lima dunia legenda</p>
					<h2>Wira Legenda!</h2>
					<ul class="emblems">
						{#each Array(total) as _, i (i)}<li><img src={symbol(i)} alt="" /></li>{/each}
					</ul>
					<p class="story-line">{me.name} menewaskan lima penjaga dengan {story.hits ?? 0} serangan boss. Tunggu hos menamatkan permainan.</p>
				</div>
			{/if}

			<div class="wipe" bind:this={wipe} aria-hidden="true"></div>
			{#if !ready}<p class="loader" aria-live="polite">Memuat dunia…</p>{/if}
		</div>

		{#if (step === 'question' || step === 'result') && question}
			<section class="panel" aria-label="Soalan pertarungan">
				<div class="paper">
					<QuestionCard {question} />
					<Answer
						{question}
						disabled={step !== 'question'}
						mine={step === 'result' ? result?.answer : undefined}
						reveal={step === 'result' && !result?.correct ? result?.reveal : null}
						allRight={result?.correct}
						onanswer={send}
					/>
				</div>
				{#if step === 'result' && result}
					<div class="verdict" class:good={result.correct} role="status">
						<p>
							{#if result.correct}
								Betul! {boss ? 'Serangan mengena.' : 'Musuh ditewaskan.'}{result.reward?.change > 0 ? ' +½ hati' : ''}
							{:else}
								Belum tepat. {boss ? scene.boss : 'Musuh'} menyerang balas: −1½ hati. Lihat jawapan yang betul.
							{/if}
							<span class="left">Hati: {heartsText(story.hearts ?? 0)} / 6</span>
						</p>
						<button type="button" class="btn btn--sun" disabled={animating} onclick={next}>Teruskan <Icon name="next" size={18} /></button>
					</div>
				{/if}
			</section>
		{/if}
	</main>
{/if}

<style>
	.story {
		display: grid;
		gap: 0.8rem;
		justify-items: center;
		padding-block: 0.8rem 3rem;
	}
	.loading {
		padding: 4rem 1rem;
		font: 700 1.3rem var(--font-pixel);
		text-align: center;
	}
	.frame {
		position: relative;
		width: min(100%, 1280px, calc((100dvh - 10rem) * var(--ar, 1.7778)));
		min-width: min(100%, 320px);
		border-radius: 16px;
		box-shadow:
			0 0 0 3px #d9a441,
			0 0 0 6px #5a3b10,
			0 18px 40px rgb(0 0 0 / 0.3);
	}
	.step-question,
	.step-result {
		justify-items: stretch;
		width: min(100%, 1480px);
		margin-inline: auto;
	}
	.step-question .frame,
	.step-result .frame {
		width: 100%;
		min-width: 0;
	}
	@media (min-width: 1000px) {
		.step-question,
		.step-result {
			grid-template-columns: minmax(0, 1fr) minmax(20rem, 25rem);
			align-items: start;
		}
	}
	.overlay {
		position: absolute;
		inset: 0;
		z-index: 10;
		container-type: inline-size;
		display: grid;
		place-content: center;
		justify-items: center;
		gap: 0.4rem;
		padding: 4cqw;
		color: #fff4d8;
		text-align: center;
		pointer-events: none;
	}
	.overlay button {
		pointer-events: auto;
	}
	.overlay h2 {
		font: 700 clamp(1.4rem, 6.2cqw, 4rem) / 1 var(--font-pixel);
		color: #fff;
		text-shadow:
			0 0.4cqw 0 #5a3b10,
			0 0 2cqw rgb(255 200 90 / 0.5);
	}
	.kicker {
		font: 700 clamp(0.7rem, 1.8cqw, 1.1rem) / 1 var(--font-pixel);
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: #ffd27a;
	}
	.story-line {
		max-width: 46ch;
		font-weight: 700;
		font-size: clamp(0.8rem, 2.1cqw, 1.25rem);
		line-height: 1.35;
		text-shadow: 0 2px 6px rgb(0 0 0 / 0.8);
	}
	.title-card {
		background: radial-gradient(ellipse at 50% 55%, rgb(8 16 36 / 0.72), rgb(8 16 36 / 0.25) 70%);
		animation: card-in 900ms cubic-bezier(0.2, 0.8, 0.2, 1) both;
	}
	.emblem {
		width: clamp(56px, 12cqw, 150px);
		filter: drop-shadow(0 0 2cqw rgb(255 210 120 / 0.6));
		animation: emblem 2.4s ease-in-out infinite;
	}
	.skip {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		margin-top: 0.6rem;
		padding: 0.4rem 0.9rem;
		border: 2px solid #d9a441;
		border-radius: 999px;
		background: rgb(10 20 46 / 0.8);
		color: #fff4d8;
		font-weight: 800;
		cursor: pointer;
	}
	.caption {
		place-content: end center;
		padding-bottom: 3cqw;
	}
	.caption p {
		padding: 1cqw 2.4cqw;
		border: 0.25cqw solid #d9a441;
		border-radius: 1.2cqw;
		background: rgb(10 20 46 / 0.86);
		font-weight: 800;
		font-size: clamp(0.8rem, 2cqw, 1.2rem);
	}
	.caption span {
		margin-left: 0.6em;
		color: #ffd27a;
	}
	.banner {
		place-content: center;
	}
	.banner p {
		padding: 1.4cqw 5cqw;
		font: 700 clamp(1.2rem, 5cqw, 3.2rem) / 1 var(--font-pixel);
		background: linear-gradient(90deg, transparent, rgb(120 10 20 / 0.9) 20%, rgb(120 10 20 / 0.9) 80%, transparent);
		animation: slash-in 600ms cubic-bezier(0.2, 0.9, 0.3, 1.2) both;
	}
	.banner.good p {
		background: linear-gradient(90deg, transparent, rgb(20 90 50 / 0.9) 20%, rgb(20 90 50 / 0.9) 80%, transparent);
	}
	.unlock {
		background: rgb(8 16 36 / 0.55);
		animation: card-in 700ms ease-out both;
	}
	.orbs,
	.emblems {
		display: flex;
		gap: clamp(0.3rem, 2cqw, 1.6rem);
		margin: 1cqw 0;
		padding: 0;
		list-style: none;
	}
	.orbs li {
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		font-weight: 800;
		font-size: clamp(0.65rem, 1.7cqw, 1rem);
		animation: orb-in 700ms cubic-bezier(0.2, 0.9, 0.3, 1.3) both;
		animation-delay: calc(400ms + var(--i) * 180ms);
	}
	.orbs img {
		width: clamp(38px, 9cqw, 110px);
		filter: drop-shadow(0 0 1.4cqw rgb(255 220 150 / 0.7));
	}
	.emblems img {
		width: clamp(28px, 6cqw, 72px);
	}
	/* Not `.reveal`: app.css uses that name for the home page's scroll-in sections. */
	.boss-reveal {
		background: #05080f;
		place-content: stretch;
		padding: 0;
		overflow: hidden;
		animation: card-in 500ms ease-out both;
	}
	.reveal-bg {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: fill;
		filter: brightness(0.35) saturate(1.1) blur(2px);
		animation: closeup 4.2s ease-out both;
	}
	.reveal-boss {
		position: absolute;
		right: 2cqw;
		bottom: 0;
		height: 94%;
		width: auto;
		max-width: 62%;
		object-fit: contain;
		object-position: bottom right;
		filter: drop-shadow(0 0 3cqw rgb(255 210 120 / 0.35));
		animation: rise-boss 1.6s cubic-bezier(0.2, 0.9, 0.3, 1) both;
	}
	@keyframes rise-boss {
		from {
			opacity: 0;
			transform: translateY(8cqw) scale(0.92);
		}
	}
	.nameplate {
		position: absolute;
		left: 4cqw;
		bottom: 5cqw;
		display: grid;
		justify-items: start;
		gap: 0.3rem;
		max-width: 52cqw;
		padding: 1.6cqw 2.4cqw;
		border-left: 0.6cqw solid #d9a441;
		background: linear-gradient(90deg, rgb(5 8 15 / 0.88), rgb(5 8 15 / 0.2));
		text-align: left;
		animation: plate-in 900ms 500ms cubic-bezier(0.2, 0.9, 0.3, 1) both;
	}
	.nameplate p:last-child {
		font-weight: 700;
		font-size: clamp(0.75rem, 1.8cqw, 1.1rem);
	}
	.boss-reveal .skip {
		position: absolute;
		right: 3cqw;
		bottom: 3cqw;
	}
	.fallen h2 {
		color: #ffb0b0;
	}
	.victor {
		width: clamp(90px, 22cqw, 260px);
		filter: drop-shadow(0 0 2cqw rgb(255 220 120 / 0.6));
		animation: emblem 1.6s ease-in-out infinite;
	}
	.wipe {
		position: absolute;
		inset: 0;
		z-index: 12;
		border-radius: 16px;
		background: url('/story/fx/transition_4x3.webp') 0 0 / 400% 300%;
		opacity: 0;
		pointer-events: none;
	}
	.loader {
		position: absolute;
		right: 1rem;
		bottom: 0.8rem;
		z-index: 11;
		padding: 0.2rem 0.7rem;
		border-radius: 999px;
		background: rgb(0 0 0 / 0.6);
		color: #fff;
		font-weight: 800;
		font-size: 0.85rem;
	}

	.panel {
		display: grid;
		gap: 0.7rem;
		width: 100%;
		min-width: 0;
		padding: 0.8rem;
		border-radius: 16px;
		background: linear-gradient(180deg, #13284f, #0a1530);
		box-shadow:
			inset 0 0 0 3px #d9a441,
			inset 0 0 0 6px #5a3b10;
		animation: rise-in var(--t-enter) var(--ease-out);
	}
	.paper {
		display: grid;
		gap: 0.9rem;
		padding: 1rem 1.1rem;
		border-radius: 12px;
		background: linear-gradient(180deg, #fffaf0, #f6ecd6);
		color: var(--ink);
		box-shadow: inset 0 0 0 2px #e4cfa0;
	}
	.verdict {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		gap: 0.6rem;
		padding: 0.7rem 0.9rem;
		border-radius: 12px;
		background: rgb(200 40 50 / 0.2);
		color: #ffe1e1;
		font-weight: 800;
	}
	.verdict.good {
		background: rgb(40 180 100 / 0.2);
		color: #d9ffe8;
	}
	.verdict .left {
		display: block;
		color: #ffd27a;
		font-size: 0.9rem;
	}

	/* A phone's stage is small: tighter cards so a whole scene fits inside it. */
	@container (max-width: 520px) {
		.overlay {
			gap: 0.15rem;
			padding: 3cqw;
		}
		.overlay h2 {
			font-size: 1.15rem;
		}
		.story-line {
			font-size: 0.72rem;
			line-height: 1.25;
		}
		.kicker {
			font-size: 0.62rem;
		}
		.emblem {
			width: 40px;
		}
		.orbs {
			margin: 0.1rem 0;
		}
		.orbs img {
			width: 28px;
		}
		.orbs li {
			font-size: 0.6rem;
		}
		.skip {
			margin-top: 0.2rem;
			padding: 0.2rem 0.6rem;
			font-size: 0.75rem;
		}
		.overlay .btn--big {
			padding: 0.4rem 0.9rem;
			font-size: 0.9rem;
		}
		.nameplate {
			max-width: 70cqw;
		}
		.victor {
			width: 70px;
		}
		.emblems img {
			width: 24px;
		}
	}
	@keyframes card-in {
		from {
			opacity: 0;
			transform: scale(1.04);
		}
	}
	@keyframes emblem {
		50% {
			transform: translateY(-4px) scale(1.04);
		}
	}
	@keyframes slash-in {
		from {
			opacity: 0;
			transform: translateX(-30%) skewX(-12deg);
		}
	}
	@keyframes orb-in {
		from {
			opacity: 0;
			transform: translateY(30px) scale(0.4);
		}
	}
	@keyframes closeup {
		from {
			transform: scale(1.35) translateY(4%);
			filter: brightness(0.3);
		}
		40% {
			filter: brightness(1);
		}
		to {
			transform: scale(1.05);
		}
	}
	@keyframes plate-in {
		from {
			opacity: 0;
			transform: translateX(-8%);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.overlay,
		.overlay *,
		.reveal-bg {
			animation-duration: 1ms !important;
			animation-iteration-count: 1 !important;
		}
	}
</style>
