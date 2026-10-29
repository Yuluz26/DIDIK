<!--
	A child's screen in Legenda Story Mode. The server's step (game.seat.step) chooses what is shown;
	this screen only plays the cinematic for that step and sends `next` when it ends (or when the child
	taps Teruskan), naming the step's `ev` so a double tap never skips one.

	Nothing here walks or dodges. The child chooses a hero, reads, answers, picks an element at the
	boss, and watches: the attack or the counterattack plays only once the server has checked the answer.

	After the hero is chosen the whole screen is the game (`.arena`, fixed, with the browser's full screen
	asked for at the tap that chooses the hero). The question is a popup over the scene, never a panel
	beside it; while the attack or counterattack plays the popup steps aside so the fight can be seen, and
	a wrong answer brings it back with the right answer shown.
-->
<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { fade } from 'svelte/transition';
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person } from '$lib/types';
	import { confetti } from '$lib/confetti';
	import Answer from '$lib/questions/Answer.svelte';
	import QuestionCard from '$lib/questions/QuestionCard.svelte';
	import FullscreenToggle from '$ui/FullscreenToggle.svelte';
	import Hud from '../Hud.svelte';
	import Icon from '$ui/Icon.svelte';
	import SoundToggle from '$ui/SoundToggle.svelte';
	import Banner from './Banner.svelte';
	import { BANNERS } from './banners';
	import HeroSelect from './HeroSelect.svelte';
	import Stage from './Stage.svelte';
	import {
		ELEMENTS,
		ELEMENT_NAME,
		HEROES,
		elementIcon,
		elementUrls,
		heartIcons,
		heartsText,
		heroArt,
		preload,
		sleep,
		reducedMotion,
		symbol,
		worldUrls,
		battleBg,
		sceneArt,
		sceneAr,
		sceneSound,
		sceneStill,
		introArt,
		introFlip,
		heroWeaponArt,
		WORLD_ART,
		bossArt,
		type Element,
		storyArt
	} from './data';
	import { sfx, sound } from './sfx';
	import { keepPlaying } from './livevideo';
	import { sceneSource, warmScenes } from './scenes';

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let { client, game, me, people }: { client: RoomClient; game: any; me: Me; people: Map<string, Person> } = $props();

	// The seat's answer count the attack or counterattack has finished playing for.
	let doneFor = $state(-1);
	let popup = $state<HTMLElement>();
	let scrim = $state<HTMLElement>();
	// The banner on screen now, if any (`n` tells one showing from the next).
	let banner = $state<{ id: string; ms: number; n: number } | null>(null);
	let bannerN = 0;
	const picked = new Set<number>();

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
	// A checked answer is being played out: the popup waits until the fight has been seen.
	const animating = $derived(step === 'result' && !!result && doneFor !== seat.answered);

	let stage = $state<Stage>();
	let wipe = $state<HTMLDivElement>();
	let still = $state(false);
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
	// The world is ready to be seen once its art is in and its living video plays (or after a few seconds
	// whatever happens); until then a curtain with the world's emblem hides it, then lifts, so a new world
	// fades in whole instead of appearing piece by piece.
	let liveWorld = $state(-1);
	let waitedFor = $state('');
	$effect(() => {
		const key = artKey;
		const cap = setTimeout(() => (waitedFor = key), 3500);
		return () => clearTimeout(cap);
	});
	const sceneReady = $derived(ready && (still || liveWorld === worldIndex || waitedFor === artKey));
	// While the child fights a world's boss, the next world's art and video arrive in the background.
	$effect(() => {
		const next = worldIndex + 1;
		if (!elementsNear || next >= total) return;
		void preload(worldUrls(next, story.hero ?? null));
		warmScenes([sceneArt(next)]);
	});
	// the reveal's backdrop plays the same video, from memory
	let revealSrc = $state<string | null>(null);
	$effect(() => {
		const w = worldIndex;
		let gone = false;
		void sceneSource(sceneArt(w)).then((src) => {
			if (!gone) revealSrc = src;
		});
		return () => (gone = true);
	});
	$effect(() => {
		if (elementsNear) void preload(elementUrls(hero));
	});
	// The banners the story uses load once the world has (the other supplied ones are not used).
	const USED = [
		'pertarungan_bermula', 'jawapan_betul', 'jawapan_salah', 'boss_akan_menyerang', 'serangan_balas', 'nyawa_berkurang',
		'pilih_elemen', 'elemen_dibuka', 'boss_muncul', 'boss_dikalahkan', 'dunia_seterusnya', 'cuba_lagi', 'kemenangan'
	];
	$effect(() => {
		if (!ready) return;
		void preload(USED.map((id) => (BANNERS[id]?.animated ? storyArt(`banners/${id}_sheet.webp`) : storyArt(`banners/${id}.webp`))));
	});

	/** Shows a transition banner for `ms`; resolves when it has gone. */
	async function show(id: string, ms = 1100): Promise<void> {
		const n = ++bannerN;
		banner = { id, ms, n };
		await sleep(ms);
		if (bannerN === n) banner = null;
	}

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
			// the title card, its sound and its timer begin once the world is ready to be seen
			introWaiting = true;
		} else if (step === 'travel') later(3400);
		else if (step === 'encounter') {
			void stage?.enter();
			void show('pertarungan_bermula', 2200);
			later(2600);
		} else if (step === 'clear') {
			sfx('correct', 0.5);
			later(2400);
		} else if (step === 'unlock') {
			sfx('unlock');
			void show('elemen_dibuka', 2600);
			later(5800);
		} else if (step === 'reveal') {
			stage?.reset();
			void show('boss_muncul', 2400);
			sound(sceneSound(worldIndex), 0.7);
			later(7800);
		} else if (step === 'worldclear') {
			stage?.celebrate();
			sfx('unlock');
			confetti({ count: 90 });
			void show('boss_dikalahkan', 2600);
			later(7600);
		} else if (step === 'fallen') {
			stage?.fall();
			void show('cuba_lagi', 2200);
		} else if (step === 'victory') {
			stage?.celebrate();
			confetti({ count: 160, spread: 1.3 });
			void show('kemenangan', 3400);
		} else if (step === 'question') {
			stage?.reset();
			// The first boss question of a world: remind the child to choose an element.
			if (boss && story.elements && !picked.has(worldIndex)) {
				picked.add(worldIndex);
				void show('pilih_elemen', 2000);
			}
		}
	});

	// The world's title card, once the curtain lifts: the wipe, the banner, the world's own sound.
	let introWaiting = $state(false);
	$effect(() => {
		if (!introWaiting || !sceneReady || step !== 'intro') return;
		introWaiting = false;
		sfx('unlock', 0.5);
		void playWipe();
		if (worldIndex > 0) void show('dunia_seterusnya', 2600);
		sound(sceneSound(worldIndex), 0.55);
		later(7000);
	});

	// A checked answer: the hero's attack or the enemy's counterattack, then on to the next step.
	$effect(() => {
		if (step !== 'result' || !result || seat.answered === lastAnswered) return;
		const mine = seat.answered;
		lastAnswered = mine;
		const reward = result.reward ?? {};
		const run = async () => {
			if (result.correct) {
				sfx(boss ? 'hit' : 'correct');
				void show('jawapan_betul', 1600);
				await stage?.attack(boss ? (reward.element as Element) : null, { weak: reward.weak, finishing: reward.bossHp === 0, healed: reward.change > 0 });
				if (reward.change > 0) sfx('heal', 0.4);
			} else {
				sfx('wrong');
				await show('jawapan_salah', 1400);
				void show(boss ? 'boss_akan_menyerang' : 'serangan_balas', 1500);
				await stage?.counter();
				void show('nyawa_berkurang', 1400);
			}
			doneFor = mine;
			// A right answer moves on by itself; a wrong one stays, with the right answer shown, until the child taps on.
			if (result.correct) later(1900);
			else later(12000);
		};
		void run();
	});

	// The question popup takes focus when it opens, so the keyboard answers it at once.
	$effect(() => {
		if (step === 'question' && popup) popup.focus({ preventScroll: true });
	});

	// The game fills the screen: the page behind it does not scroll.
	$effect(() => {
		if (step === 'select' || game.stage === 'intro') return;
		const was = document.body.style.overflow;
		document.body.style.overflow = 'hidden';
		return () => (document.body.style.overflow = was);
	});

	/**
	 * Shrinks the popup to fit the viewport, so the whole question shows without scrolling (the scroll bar
	 * is hidden; a very small screen can still scroll). It measures the popup at full size first.
	 */
	function fit() {
		if (!popup || !scrim) return;
		popup.style.zoom = '1';
		const box = getComputedStyle(scrim);
		const room = {
			h: scrim.clientHeight - parseFloat(box.paddingTop) - parseFloat(box.paddingBottom),
			w: scrim.clientWidth - parseFloat(box.paddingLeft) - parseFloat(box.paddingRight)
		};
		const k = Math.min(1, room.h / popup.scrollHeight, room.w / popup.offsetWidth);
		popup.style.zoom = k < 1 ? String(Math.max(0.5, k)) : '';
	}
	const refit = () => requestAnimationFrame(() => requestAnimationFrame(fit));

	$effect(() => {
		// Whenever what the popup holds changes, fit it again once it has been drawn.
		void [step, question?.id, story.element, story.hearts, animating, result?.correct, popup];
		if (popup) void tick().then(refit);
	});

	/** Asks the browser for full screen (and, on a phone, landscape). It must come from a tap; if the
	 *  browser says no, the game still fills the page. */
	function goFullscreen() {
		const root = document.documentElement as HTMLElement & { webkitRequestFullscreen?: () => Promise<void> };
		if (document.fullscreenElement) return;
		try {
			const asked = root.requestFullscreen?.({ navigationUI: 'hide' }) ?? root.webkitRequestFullscreen?.();
			void Promise.resolve(asked)
				.then(() => (screen.orientation as unknown as { lock?: (o: string) => Promise<void> })?.lock?.('landscape'))
				.catch(() => undefined);
		} catch {
			/* not allowed here: nothing changes */
		}
	}

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
	// The question popup is open while a question is asked and, for a wrong answer, once the counterattack has played.
	const asking = $derived((step === 'question' || step === 'result') && !!question);
	const popupAway = $derived(step === 'result' && (animating || !!result?.correct));
	const answered = $derived(raid ? raid.answered.length : 0);
	const fighting = $derived(raid ? raid.members.length : 1);
</script>

<svelte:window onkeydown={onkey} onresize={refit} />

{#if step === 'select'}
	<Hud {me} score={game.score ?? 0} />
	<main class="wrap story">
		<HeroSelect
			onpick={(h) => {
				goFullscreen();
				client.send({ t: 'hero', hero: h, ev: story.ev });
			}}
		/>
	</main>
{:else if game.stage === 'intro'}
	<Hud {me} score={game.score ?? 0} />
	<main class="wrap story"><p class="loading">Membuka kitab legenda…</p></main>
{:else}
	<div class="arena step-{step}" class:asking style:--backdrop="url({battleBg(worldIndex)})">
		<div class="frame" style:--ar={sceneAr(worldIndex)}>
			<Stage
				bind:this={stage}
				world={worldIndex}
				{hero}
				heroName={me.name}
				hearts={story.hearts ?? 12}
				maxHearts={game.world?.maxHearts ?? 12}
				foe={!boss ? { name: scene.foe ?? 'Musuh', index: foeIndex, total: encounters } : null}
				boss={boss && raid ? { name: scene.boss, hp: raid.hp, max: raid.max, subtitle: scene.title } : null}
				elements={story.hero && !asking ? { unlocked: !!story.elements, selected: story.element ?? 'api', disabled: true, onpick: chooseElement } : null}
				weapon={story.elements ? ((story.element ?? 'api') as Element) : null}
				enemy={showEnemy ? enemyState : 'none'}
				friends={friends.filter((f) => f.step !== 'select')}
				mode={stageMode}
				dim={['intro', 'unlock', 'gather', 'fallen', 'reveal', 'victory'].includes(step)}
				paused={step === 'reveal'}
				onlive={(w) => (liveWorld = w)}
			/>

			{#if step === 'intro' && sceneReady}
				<div class="overlay title-card" role="status" out:fade={{ duration: still ? 0 : 320 }}>
					<img class="emblem" src={symbol(worldIndex)} alt="" />
					<p class="kicker">Dunia {worldIndex + 1} / {total}</p>
					<h2>{scene.title}</h2>
					<p class="story-line">{scene.intro}</p>
					<button type="button" class="skip" onclick={next}>Teruskan <Icon name="next" size={18} /></button>
				</div>
			{:else if step === 'travel'}
				<div class="overlay caption" role="status" out:fade={{ duration: still ? 0 : 320 }}>
					<p>{heroInfo.name} meneruskan perjalanan… <span>Musuh {foeIndex} / {encounters}</span></p>
				</div>
			{:else if step === 'clear'}
				<div class="overlay banner good" role="status" out:fade={{ duration: still ? 0 : 320 }}><p>Musuh tewas! {story.cleared} / {encounters}</p></div>
			{:else if step === 'unlock'}
				<div class="overlay unlock" role="status" out:fade={{ duration: still ? 0 : 320 }}>
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
				<div class="overlay unlock" role="status" out:fade={{ duration: still ? 0 : 320 }}>
					<p class="kicker">Pintu boss</p>
					<h2>Menunggu kawan</h2>
					<p class="story-line">
						{seat.gather?.behind
							? `${seat.gather.behind} kawan masih dalam perjalanan. Kita lawan ${scene.boss} bersama-sama!`
							: 'Bersedia…'}
					</p>
				</div>
			{:else if step === 'reveal'}
				<!-- the hero on the left faces the boss on the right, which turns to look back at the hero -->
				<div class="overlay boss-reveal" role="status" style:--aura={WORLD_ART[worldIndex].aura} out:fade={{ duration: still ? 0 : 320 }}>
					<!-- first the boss stirs in its living world, close up; then the world dims behind the two who will fight -->
					<video class="reveal-bg" {@attach keepPlaying} src={revealSrc ?? sceneArt(worldIndex)} poster={sceneStill(worldIndex)} muted loop autoplay playsinline disablepictureinpicture aria-hidden="true"></video>
					<span class="reveal-aura"></span>
					<img class="reveal-hero" src={heroWeaponArt(hero, (story.element ?? 'api') as Element)} alt="" />
					<span class="reveal-ground"></span>
					<!-- the boss's introduction portrait; the battle sprite if it cannot be loaded -->
					<img
						class="reveal-boss"
						class:flip={introFlip(worldIndex)}
						src={introArt(worldIndex)}
						alt=""
						onerror={(e) => {
							const img = e.currentTarget as HTMLImageElement;
							img.classList.remove('flip');
							if (!img.src.includes('/boss.webp')) img.src = bossArt(worldIndex);
						}}
					/>
					<div class="nameplate">
						<p class="kicker">Penjaga {scene.title}</p>
						<h2>{scene.boss}</h2>
						<p>Lima bar kuasa. Setiap jawapan betul membuang satu bar.</p>
						<button type="button" class="skip" onclick={next}>Lawan! <Icon name="next" size={18} /></button>
					</div>
				</div>
			{:else if step === 'wait'}
				<div class="overlay caption" role="status" out:fade={{ duration: still ? 0 : 320 }}>
					<p>Seranganmu sudah dihantar! Menunggu kawan menjawab… <span>{answered} / {fighting}</span></p>
				</div>
			{:else if step === 'fallen'}
				<div class="overlay unlock fallen" role="alert" out:fade={{ duration: still ? 0 : 320 }}>
					<h2>{heroInfo.name} tumbang!</h2>
					<p class="story-line">
						Jangan risau. Kamu sambung di sini dengan enam hati penuh{boss ? ', dan kerosakan pada boss kekal.' : '.'}
					</p>
					<button type="button" class="btn btn--sun btn--big" onclick={() => client.send({ t: 'retry', ev: story.ev })}>Cuba lagi</button>
				</div>
			{:else if step === 'worldclear'}
				<div class="overlay title-card clear" role="status" out:fade={{ duration: still ? 0 : 320 }}>
					<img class="emblem" src={symbol(worldIndex)} alt="" />
					<p class="kicker">Dunia dibebaskan</p>
					<h2>{scene.title}</h2>
					<p class="story-line">{scene.clear}</p>
					<button type="button" class="btn btn--sun btn--big" onclick={next}>{worldIndex + 1 < total ? 'Dunia seterusnya' : 'Penamat'} <Icon name="next" /></button>
				</div>
			{:else if step === 'victory'}
				<div class="overlay title-card victory" role="status" out:fade={{ duration: still ? 0 : 320 }}>
					<img class="victor" src={heroArt(hero, 'victory')} alt="" />
					<p class="kicker">Tamat · Lima dunia legenda</p>
					<h2>Wira Legenda!</h2>
					<ul class="emblems">
						{#each Array(total) as _, i (i)}<li><img src={symbol(i)} alt="" /></li>{/each}
					</ul>
					<p class="story-line">{me.name} menewaskan lima penjaga dengan {story.hits ?? 0} serangan boss. Tunggu hos menamatkan permainan.</p>
				</div>
			{/if}

			{#if banner}{#key banner.n}<Banner id={banner.id} ms={banner.ms} />{/key}{/if}

			<div class="wipe" bind:this={wipe} aria-hidden="true"></div>
			<!-- the curtain between worlds: the new world's emblem, until the world is ready to be seen -->
			<div class="curtain" class:up={sceneReady} role="status" aria-live="polite">
				<img class="curtain-emblem" src={symbol(worldIndex)} alt="" />
				<p><span>Dunia {worldIndex + 1}</span> {scene.title ?? ''}</p>
			</div>
		</div>

		<!-- the question, as a popup over the scene -->
		{#if asking && question}
			<div class="scrim" class:away={popupAway} bind:this={scrim}>
				<div class="popup" role="dialog" aria-modal="true" aria-label="Soalan pertarungan" tabindex="-1" bind:this={popup} oninput={refit} onclick={refit} onkeyup={refit}>
					<header class="p-head">
						<p class="who"><img src={symbol(worldIndex)} alt="" /> {boss ? scene.boss : (scene.foe ?? 'Musuh')}</p>
						<p class="hearts" aria-label="Hati: {heartsText(story.hearts ?? 0)} daripada 6">
							{#each heartIcons(story.hearts ?? 0) as h, i (i)}<img src={storyArt(`ui/heart_${h}.webp`)} alt="" />{/each}
						</p>
					</header>

					{#if boss && story.elements}
						<div class="elements" role="radiogroup" aria-label="Pilih elemen serangan (Alt+1 hingga Alt+5)">
							{#each ELEMENTS as el, i (el)}
								<button
									type="button"
									role="radio"
									aria-checked={story.element === el}
									class:on={story.element === el}
									disabled={step !== 'question'}
									title="Alt+{i + 1}"
									onclick={() => chooseElement(el)}
								>
									<img src={elementIcon(el)} alt="" /><span>{ELEMENT_NAME[el]}</span>
								</button>
							{/each}
						</div>
					{/if}

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

					{#if step === 'result' && result && !animating}
						<div class="verdict" role="status">
							<p>
								Belum tepat. {boss ? scene.boss : 'Musuh'} menyerang balas: −1½ hati. Lihat jawapan yang betul.
								<span class="left">Hati: {heartsText(story.hearts ?? 0)} / 6</span>
							</p>
							<button type="button" class="btn btn--sun" onclick={next}>Teruskan <Icon name="next" size={18} /></button>
						</div>
					{/if}
				</div>
			</div>
		{/if}

		{#if step === 'result' && result?.correct && !animating}
			<aside class="toast" role="status">
				<p>
					Betul! {boss ? 'Serangan mengena.' : 'Musuh ditewaskan.'}{result.reward?.change > 0 ? ' +½ hati' : ''}
				</p>
				<button type="button" class="btn btn--sun" onclick={next}>Teruskan <Icon name="next" size={18} /></button>
			</aside>
		{/if}

		<div class="tools">
			<FullscreenToggle light />
			<SoundToggle light />
			<span class="score"><strong>{(game.score ?? 0).toLocaleString('ms-MY')}</strong> mata</span>
		</div>
	</div>
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
	/* ---- the whole screen is the game */
	.arena {
		position: fixed;
		inset: 0;
		z-index: 40;
		display: grid;
		place-items: center;
		background: #04070d;
		overflow: hidden;
	}
	.frame {
		position: relative;
		width: min(100vw, calc(100dvh * var(--ar, 1.7778)));
		max-height: 100dvh;
	}
	.frame :global(.stage) {
		border-radius: 0;
	}
	.tools {
		position: fixed;
		left: max(0.6rem, env(safe-area-inset-left, 0px));
		bottom: max(0.6rem, env(safe-area-inset-bottom, 0px));
		z-index: 30;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}
	.tools :global(.btn) {
		min-height: 2.5rem;
		min-width: 2.5rem;
		padding: 0.4rem;
	}
	.score {
		padding: 0.35rem 0.8rem;
		border-radius: 999px;
		background: rgb(8 14 32 / 0.72);
		border: 2px solid #d9a441;
		color: #fff4d8;
		font-weight: 800;
		font-size: 0.85rem;
		white-space: nowrap;
	}

	/* ---- the question popup */
	.scrim {
		position: fixed;
		inset: 0;
		z-index: 20;
		display: grid;
		place-items: center;
		padding: 0.75rem 0.75rem 3.8rem;
		background: radial-gradient(ellipse at 50% 45%, rgb(8 14 32 / 0.55), rgb(8 14 32 / 0.8));
		transition:
			opacity 260ms ease,
			visibility 0s 260ms;
	}
	/* Upright phones and tablets: the battlefield across the top, the question under it (so the fight
	   stays in view), and a soft, dark copy of the painting in the rest of the screen. */
	@media (max-aspect-ratio: 10/9) {
		.arena {
			place-items: start center;
			padding-top: env(safe-area-inset-top, 0px);
		}
		.arena::before {
			content: '';
			position: absolute;
			inset: -6%;
			background: var(--backdrop) center / cover;
			filter: blur(18px) brightness(0.35) saturate(1.15);
			/* its own layer: the blur is drawn once, not again whenever the game above it changes */
			transform: translateZ(0);
		}
		/* On a tall screen the scene sits in the middle while nothing is asked, and glides to the top to make
		   room for a question below it. */
		.frame {
			z-index: 1;
			box-shadow: 0 1rem 2.4rem rgb(0 0 0 / 0.55);
			transition: translate 420ms cubic-bezier(0.2, 0.8, 0.2, 1);
		}
		.arena:not(.asking) .frame {
			translate: 0 max(0px, calc((100dvh - env(safe-area-inset-top, 0px) - 100vw / var(--ar, 1.7778)) / 2));
		}
		.scrim {
			top: calc(env(safe-area-inset-top, 0px) + 100vw / var(--ar, 1.7778));
			place-items: start center;
			padding-top: 0.8rem;
			background: none;
		}
	}
	.scrim.away {
		opacity: 0;
		visibility: hidden;
		pointer-events: none;
	}
	.popup {
		display: grid;
		gap: 0.7rem;
		width: min(46rem, 100%);
		max-height: 100%;
		padding: 0.8rem;
		overflow: auto;
		scrollbar-width: none;
		-ms-overflow-style: none;
		border-radius: 22px;
		background: linear-gradient(180deg, #13284f, #0a1530);
		box-shadow:
			0 0 0 3px #d9a441,
			0 0 0 6px #5a3b10,
			0 24px 60px rgb(0 0 0 / 0.55);
		animation: pop-up 340ms var(--spring, cubic-bezier(0.34, 1.56, 0.64, 1)) both;
		outline: none;
	}
	.popup::-webkit-scrollbar {
		display: none;
	}
	@media (max-height: 700px) {
		.scrim {
			padding-top: 0.5rem;
		}
		.popup {
			gap: 0.45rem;
			padding: 0.55rem;
		}
		.paper {
			gap: 0.6rem;
			padding: 0.7rem 0.85rem;
		}
		.elements img {
			width: min(2.3rem, 100%);
		}
		.elements button {
			padding: 0.25rem 0.2rem 0.3rem;
			font-size: 0.75rem;
		}
	}
	@keyframes pop-up {
		from {
			opacity: 0;
			transform: translateY(18px) scale(0.94);
		}
	}
	.p-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.8rem;
		padding: 0 0.3rem;
	}
	.who {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		color: #fff4d8;
		font: 700 1.05rem/1 var(--font-pixel, var(--font-display));
	}
	.who img {
		width: 1.8rem;
		height: 1.8rem;
	}
	.hearts {
		display: flex;
		gap: 0.15rem;
		margin: 0;
	}
	.hearts img {
		width: 1.35rem;
		height: auto;
	}
	.elements {
		display: flex;
		justify-content: center;
		gap: 0.5rem;
	}
	.elements button {
		display: grid;
		flex: 1 1 0;
		justify-items: center;
		gap: 0.1rem;
		min-width: 0;
		max-width: 5.4rem;
		padding: 0.35rem 0.2rem 0.4rem;
		border: 2px solid transparent;
		border-radius: 14px;
		background: rgb(255 255 255 / 0.06);
		color: #fff4d8;
		font-weight: 800;
		font-size: 0.82rem;
		cursor: pointer;
		transition:
			transform 160ms var(--spring, ease),
			background 160ms;
	}
	.elements img {
		width: min(2.9rem, 100%);
		height: auto;
		aspect-ratio: 1;
	}
	.elements button.on {
		border-color: #ffd27a;
		background: rgb(255 210 120 / 0.18);
		transform: translateY(-3px);
		box-shadow: 0 0 18px rgb(255 210 120 / 0.45);
	}
	.elements button:focus-visible {
		outline: 3px solid #fff;
	}
	.paper {
		display: grid;
		gap: 0.9rem;
		padding: 1rem 1.1rem;
		border-radius: 14px;
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
		background: rgb(200 40 50 / 0.22);
		color: #ffe1e1;
		font-weight: 800;
	}
	.verdict p {
		margin: 0;
	}
	.verdict .left {
		display: block;
		color: #ffd27a;
		font-size: 0.9rem;
	}
	.toast {
		position: fixed;
		left: 50%;
		bottom: max(3.8rem, calc(env(safe-area-inset-bottom, 0px) + 3.2rem));
		z-index: 25;
		display: flex;
		align-items: center;
		gap: 0.9rem;
		max-width: calc(100vw - 1.5rem);
		padding: 0.6rem 0.8rem 0.6rem 1.1rem;
		border: 3px solid #d9a441;
		border-radius: 999px;
		background: linear-gradient(180deg, rgb(20 90 50 / 0.96), rgb(12 60 36 / 0.96));
		color: #d9ffe8;
		font-weight: 800;
		transform: translateX(-50%);
		box-shadow: 0 14px 34px rgb(0 0 0 / 0.5);
		animation: toast-up 300ms var(--ease-out) both;
	}
	.toast p {
		margin: 0;
	}
	@keyframes toast-up {
		from {
			opacity: 0;
			transform: translate(-50%, 14px);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.popup,
		.toast {
			animation: none;
		}
		.scrim {
			transition: none;
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
	/* The words of a story card come in one after another, slowly enough to be read and enjoyed. */
	.title-card > :not(img),
	.unlock > :not(.orbs),
	.nameplate > *,
	.caption p {
		animation: words-in 700ms cubic-bezier(0.2, 0.8, 0.2, 1) both;
		animation-delay: calc(250ms + var(--n, 0) * 280ms);
	}
	.overlay > :nth-child(2),
	.nameplate > :nth-child(2) {
		--n: 1;
	}
	.overlay > :nth-child(3),
	.nameplate > :nth-child(3) {
		--n: 2;
	}
	.overlay > :nth-child(4),
	.nameplate > :nth-child(4) {
		--n: 3;
	}
	.overlay > :nth-child(5) {
		--n: 4;
	}
	.overlay > :nth-child(6) {
		--n: 5;
	}
	.nameplate > * {
		animation-delay: calc(3.1s + var(--n, 0) * 280ms);
	}
	@keyframes words-in {
		from {
			opacity: 0;
			transform: translateY(0.9rem);
		}
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
	/* The painting, cropped in (its own title plate and minimap in the corners stay out of view),
	   darkened and softened behind the two who are about to fight. */
	.reveal-bg {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
		/* close in on the boss's arena: the painting's title plate and minimap stay out of view */
		transform-origin: 66% 42%;
		transform: scale(1.35);
		filter: brightness(0.42) saturate(1.1) blur(3px);
		animation: awaken 3.6s ease-out both;
	}
	/* the boss's own light behind it, and a dark floor under both */
	.reveal-aura {
		position: absolute;
		right: -6cqw;
		top: 4%;
		width: 66cqw;
		height: 96%;
		border-radius: 50%;
		background: radial-gradient(closest-side, color-mix(in srgb, var(--aura) 45%, transparent), color-mix(in srgb, var(--aura) 12%, transparent) 62%, transparent);
		animation:
			glow-in 1.2s 2.2s ease-out both,
			aura-pulse 3.4s ease-in-out 3.4s infinite;
	}
	.reveal-ground {
		position: absolute;
		inset: auto 0 0;
		height: 28%;
		background: linear-gradient(180deg, transparent, rgb(5 8 15 / 0.75));
	}
	.reveal-hero {
		position: absolute;
		left: 3cqw;
		bottom: 2%;
		z-index: 1;
		height: 52%;
		width: auto;
		filter: drop-shadow(0 0.6cqw 1cqw rgb(0 0 0 / 0.6)) brightness(0.92);
		animation: hero-in 900ms 2.4s cubic-bezier(0.2, 0.9, 0.3, 1) both;
	}
	.reveal-boss {
		position: absolute;
		right: 3cqw;
		bottom: 3%;
		z-index: 1;
		height: 82%;
		width: auto;
		max-width: 60cqw;
		object-fit: contain;
		object-position: bottom right;
		filter: drop-shadow(0 0 2.4cqw color-mix(in srgb, var(--aura) 55%, transparent)) drop-shadow(0 1cqw 1.2cqw rgb(0 0 0 / 0.5));
		animation:
			rise-boss 1.4s 2.2s cubic-bezier(0.2, 0.9, 0.3, 1) both,
			boss-breathe 4.5s ease-in-out 3.6s infinite;
	}
	.reveal-boss.flip {
		scale: -1 1;
	}
	@keyframes rise-boss {
		from {
			opacity: 0;
			transform: translateY(6cqw) scale(0.9);
			filter: brightness(2.4) drop-shadow(0 0 3cqw var(--aura));
		}
	}
	@keyframes boss-breathe {
		50% {
			transform: translateY(-0.8cqw);
		}
	}
	@keyframes hero-in {
		from {
			opacity: 0;
			transform: translateX(-6cqw);
		}
	}
	@keyframes glow-in {
		from {
			opacity: 0;
			transform: scale(0.6);
		}
	}
	@keyframes aura-pulse {
		50% {
			opacity: 0.65;
		}
	}
	/* the boss's name in the open sky above the hero, clear of both */
	.nameplate {
		position: absolute;
		left: 4cqw;
		top: 4cqw;
		z-index: 2;
		display: grid;
		justify-items: start;
		gap: 0.3rem;
		max-width: 38cqw;
		padding: 1.2cqw 1.8cqw;
		border-left: 0.6cqw solid #d9a441;
		border-radius: 0 1cqw 1cqw 0;
		background: linear-gradient(90deg, rgb(5 8 15 / 0.85), rgb(5 8 15 / 0.35));
		text-align: left;
		animation: plate-in 900ms 2.7s cubic-bezier(0.2, 0.9, 0.3, 1) both;
	}
	.nameplate h2 {
		font-size: clamp(1.2rem, 4.6cqw, 3rem);
	}
	.nameplate p:not(.kicker) {
		font-weight: 700;
		font-size: clamp(0.7rem, 1.6cqw, 1rem);
		line-height: 1.3;
	}
	.boss-reveal .skip {
		margin-top: 0.6cqw;
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
	/* The curtain between worlds fades away as one piece once the new world is ready. */
	.curtain {
		position: absolute;
		inset: 0;
		z-index: 13;
		display: grid;
		place-content: center;
		justify-items: center;
		gap: 0.8cqw;
		container-type: inline-size;
		background: radial-gradient(ellipse at 50% 45%, #15213f, #05080f 70%);
		color: #fff4d8;
		transition:
			opacity 700ms ease,
			visibility 0s linear 700ms;
	}
	.curtain.up {
		opacity: 0;
		visibility: hidden;
		pointer-events: none;
	}
	.curtain-emblem {
		width: clamp(56px, 12cqw, 140px);
		filter: drop-shadow(0 0 2cqw rgb(255 210 120 / 0.55));
		animation: curtain-glow 1.6s ease-in-out infinite;
	}
	.curtain p {
		display: grid;
		justify-items: center;
		font: 700 clamp(1rem, 3.4cqw, 2rem) / 1.1 var(--font-pixel);
	}
	.curtain p span {
		color: #ffd27a;
		font-size: 0.55em;
		letter-spacing: 0.12em;
		text-transform: uppercase;
	}
	@keyframes curtain-glow {
		50% {
			transform: scale(1.06);
			filter: drop-shadow(0 0 3.5cqw rgb(255 210 120 / 0.8));
		}
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
			max-width: 52cqw;
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
	/* the boss stirs, clear and close, then the world dims as the two fighters step forward */
	@keyframes awaken {
		from {
			transform: scale(1.5);
			filter: brightness(0.35) saturate(1.1) blur(0);
		}
		12% {
			filter: brightness(1) saturate(1.1) blur(0);
		}
		62% {
			transform: scale(1.38);
			filter: brightness(1) saturate(1.1) blur(0);
		}
	}
	@keyframes plate-in {
		from {
			opacity: 0;
			transform: translateX(-8%);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.curtain-emblem {
			animation: none;
		}
		.overlay,
		.overlay *,
		.reveal-bg {
			animation-duration: 1ms !important;
			animation-iteration-count: 1 !important;
		}
	}
</style>
