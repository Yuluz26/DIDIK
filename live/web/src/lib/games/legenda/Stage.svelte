<!--
	The battle stage: the world's backdrop, the hero on the left, the enemy on the right, the effects
	between them and the HUD on top, in one 16:9 box that scales with its width.

	Poses are separate drawings (static/story/), switched on cue and moved with the Web Animations
	API: an attack is wind-up, strike, the element's burst and its 12-frame impact on the target, a
	flash and a shake; a counterattack is the boss's telegraph, lunge and strike on the hero. The HUD
	shows the server's hearts and boss bars, but holds the old number until the hit in the animation
	lands, so what a child sees and what the server decided always agree by the end of the strike.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import Particles from './Particles.svelte';
	import {
		ELEMENT_TINT,
		WORLD_ART,
		battleBg,
		bossArt,
		fxSheet,
		fxStill,
		heartIcons,
		heroArt,
		reducedMotion,
		sleep,
		type Element,
		type Pose
	} from './data';

	interface Friend {
		id: string;
		hero: string | null;
		hearts: number;
	}

	let {
		world,
		hero,
		heroName = '',
		hearts,
		maxHearts = 12,
		foe = null,
		boss = null,
		enemy = 'idle',
		friends = [],
		mode = 'battle',
		dim = false
	}: {
		world: number;
		hero: string;
		heroName?: string;
		hearts: number;
		maxHearts?: number;
		/** A road enemy: its name and which of the five it is. */
		foe?: { name: string; index: number; total: number } | null;
		/** The boss: its name and bars. */
		boss?: { name: string; hp: number; max: number } | null;
		/** Where the enemy is: arriving, standing, gone (cleared), or beaten (the boss falls). */
		enemy?: 'none' | 'enter' | 'idle' | 'gone' | 'beaten';
		friends?: Friend[];
		/** 'battle' (still camera), 'travel' (the camera pans along as the heroes walk) or 'scenery'. */
		mode?: 'battle' | 'travel' | 'scenery';
		dim?: boolean;
	} = $props();

	const art = $derived(WORLD_ART[world]);
	let still = $state(false);
	let busy = $state(false);
	let heroPose = $state<Pose>('idle');
	let bossPose = $state('idle');
	let shownHearts = $state(12);
	let shownBoss = $state(5);
	let fallen = $state(false);
	let cheering = $state(false);
	let pops = $state<{ id: number; text: string; x: number; y: number; tone: string }[]>([]);
	let popId = 0;

	let stageEl: HTMLDivElement;
	let heroEl: HTMLDivElement;
	let enemyEl = $state<HTMLDivElement>();
	let flashEl: HTMLDivElement;
	let burstEl: HTMLImageElement;
	let sheetEl: HTMLDivElement;
	let air: Particles;

	$effect(() => {
		if (!busy) shownHearts = hearts;
	});
	$effect(() => {
		if (!busy) shownBoss = boss?.hp ?? 0;
	});

	onMount(() => {
		still = reducedMotion();
	});

	// Hero and enemy centres on the stage (fractions of its width and height), for effects.
	const HERO_AT = { x: 0.22, y: 0.62 };
	const ENEMY_AT = $derived({ x: boss ? 0.7 : 0.74, y: boss ? 0.46 : 0.55 });

	function pop(text: string, at: { x: number; y: number }, tone: 'hurt' | 'heal' | 'hit' | 'weak') {
		const id = ++popId;
		pops = [...pops, { id, text, x: at.x, y: at.y, tone }];
		setTimeout(() => (pops = pops.filter((p) => p.id !== id)), 1400);
	}

	function move(el: HTMLElement | undefined, frames: Keyframe[], ms: number, easing = 'ease-out'): Promise<void> {
		if (!el || still) return sleep(still ? Math.min(ms, 120) : ms);
		return el.animate(frames, { duration: ms, easing, fill: 'forwards' }).finished.then(() => undefined, () => undefined);
	}

	function shake(strength = 1) {
		if (still || !stageEl) return;
		const d = 0.6 * strength;
		stageEl.animate(
			[
				{ transform: 'translate(0,0)' },
				{ transform: `translate(${-d}cqw, ${d * 0.5}cqw)` },
				{ transform: `translate(${d}cqw, ${-d * 0.4}cqw)` },
				{ transform: `translate(${-d * 0.6}cqw, ${d * 0.3}cqw)` },
				{ transform: 'translate(0,0)' }
			],
			{ duration: 360, easing: 'ease-out' }
		);
	}

	function flash(colour = '#ffffff', strength = 0.75) {
		if (!flashEl) return;
		flashEl.style.background = colour;
		flashEl.animate([{ opacity: still ? strength * 0.4 : strength }, { opacity: 0 }], { duration: still ? 200 : 320, easing: 'ease-out' });
	}

	/** The element's own burst: the HD still swelling and the 12-frame impact sheet, on the target. */
	async function impact(el: Element, at: { x: number; y: number }, size: number, filter = '', mirror = false) {
		const tint = ELEMENT_TINT[el];
		air?.burst(at.x, at.y, [tint[0], tint[1], '#ffffff'], still ? 0 : 54);
		if (burstEl) {
			burstEl.src = fxStill(el);
			burstEl.style.left = `${at.x * 100}%`;
			burstEl.style.top = `${at.y * 100}%`;
			burstEl.style.width = `${size}cqw`;
			burstEl.style.filter = filter;
			burstEl.animate(
				[
					{ opacity: 0, transform: `translate(-50%,-50%) scale(${mirror ? -0.35 : 0.35}, 0.35) rotate(-18deg)` },
					{ opacity: 1, offset: 0.25, transform: `translate(-50%,-50%) scale(${mirror ? -1 : 1}, 1) rotate(0deg)` },
					{ opacity: 0, transform: `translate(-50%,-50%) scale(${mirror ? -1.35 : 1.35}, 1.35) rotate(10deg)` }
				],
				{ duration: still ? 380 : 720, easing: 'cubic-bezier(.2,.8,.2,1)' }
			);
		}
		if (sheetEl && !still) {
			sheetEl.style.backgroundImage = `url(${fxSheet(el)})`;
			sheetEl.style.left = `${at.x * 100}%`;
			sheetEl.style.top = `${at.y * 100}%`;
			sheetEl.style.filter = filter;
			sheetEl.style.opacity = '1';
			for (let frame = 0; frame < 12; frame++) {
				sheetEl.style.backgroundPosition = `${(frame % 4) * 33.333}% ${Math.floor(frame / 4) * 50}%`;
				await sleep(34);
			}
			sheetEl.style.opacity = '0';
		}
	}

	/** A projectile: the element still flying from one side to the other, small and spinning. */
	function fly(el: Element, from: { x: number; y: number }, to: { x: number; y: number }, filter = '') {
		if (still || !stageEl) return sleep(80);
		const img = document.createElement('img');
		img.src = fxStill(el);
		img.alt = '';
		img.className = 'bolt';
		img.style.filter = filter;
		stageEl.appendChild(img);
		const dx = (to.x - from.x) * 100;
		const dy = (to.y - from.y) * 100;
		return img
			.animate(
				[
					{ left: `${from.x * 100}%`, top: `${from.y * 100}%`, transform: 'translate(-50%,-50%) scale(0.25) rotate(0deg)', opacity: 0.4 },
					{ offset: 0.2, opacity: 1 },
					{ left: `${(from.x + dx / 100) * 100}%`, top: `${(from.y + dy / 100) * 100}%`, transform: 'translate(-50%,-50%) scale(0.5) rotate(320deg)', opacity: 1 }
				],
				{ duration: 340, easing: 'ease-in' }
			)
			.finished.then(
				() => img.remove(),
				() => img.remove()
			);
	}

	// ------------------------------------------------------------ the moves (called by the player screen)

	/** A right answer: the hero strikes with an element (or a plain blade on the road). */
	export async function attack(element: Element | null, opts: { weak?: boolean; finishing?: boolean; healed?: boolean } = {}) {
		busy = true;
		const el: Element = element ?? 'angin';
		const casting = element === 'petir' || element === 'air' || element === 'tanah';
		heroPose = 'ready';
		await move(heroEl, [{ transform: 'translateX(0)' }, { transform: 'translateX(-1.2cqw)' }], 200);
		heroPose = casting ? 'cast' : 'attack';
		if (casting) {
			flash(ELEMENT_TINT[el][1], 0.25);
			await fly(el, { x: HERO_AT.x + 0.06, y: HERO_AT.y - 0.06 }, ENEMY_AT);
		} else {
			await move(heroEl, [{ transform: 'translateX(-1.2cqw)' }, { transform: 'translateX(26cqw)' }], 230, 'cubic-bezier(.5,0,.9,.4)');
		}
		flash('#ffffff', 0.7);
		shake(opts.finishing ? 1.8 : 1.1);
		if (art.poses.includes('hurt')) bossPose = 'hurt';
		void move(
			enemyEl,
			[
				{ transform: 'translateX(0) rotate(0)', filter: 'brightness(1)' },
				{ transform: 'translateX(2.4cqw) rotate(3deg)', filter: 'brightness(2.4)', offset: 0.2 },
				{ transform: 'translateX(1.2cqw) rotate(1deg)', filter: 'brightness(1)', offset: 0.5 },
				{ transform: 'translateX(0) rotate(0)', filter: 'brightness(1)' }
			],
			520
		);
		const done = impact(el, ENEMY_AT, element ? 34 : 24, element ? '' : 'saturate(0) brightness(1.6)');
		if (boss) shownBoss = boss.hp;
		pop(opts.weak ? 'KELEMAHAN!' : boss ? '−1 bar' : 'Kena!', { x: ENEMY_AT.x, y: ENEMY_AT.y - 0.26 }, opts.weak ? 'weak' : 'hit');
		if (!casting) await move(heroEl, [{ transform: 'translateX(26cqw)' }, { transform: 'translateX(0)' }], 320, 'ease-in-out');
		await done;
		heroPose = 'idle';
		bossPose = 'idle';
		shownHearts = hearts;
		if (opts.healed) pop('+½ ♥', { x: HERO_AT.x, y: HERO_AT.y - 0.32 }, 'heal');
		await sleep(250);
		busy = false;
	}

	/** A wrong answer: the enemy's unavoidable counterattack. */
	export async function counter() {
		busy = true;
		const el = art.strikes;
		const filter = art.strikeFilter ?? '';
		if (art.poses.includes('special')) bossPose = 'special';
		await move(
			enemyEl,
			[
				{ transform: 'scale(1)', filter: 'brightness(1)' },
				{ transform: 'scale(1.05)', filter: `brightness(1.5) drop-shadow(0 0 2cqw ${art.aura})` }
			],
			360
		);
		if (art.poses.includes('attack')) bossPose = 'attack';
		void move(
			enemyEl,
			[
				{ transform: 'scale(1.05) translateX(0)', filter: `brightness(1.5) drop-shadow(0 0 2cqw ${art.aura})` },
				{ transform: 'scale(1.08) translateX(-9cqw)', filter: 'brightness(1.2)', offset: 0.35 },
				{ transform: 'scale(1) translateX(0)', filter: 'brightness(1)' }
			],
			700,
			'cubic-bezier(.3,0,.3,1)'
		);
		await fly(el, { x: ENEMY_AT.x - 0.1, y: ENEMY_AT.y }, HERO_AT, filter);
		heroPose = 'hurt';
		flash('#ff4a4a', 0.5);
		shake(1.5);
		void move(heroEl, [{ transform: 'translateX(0)' }, { transform: 'translateX(-4cqw)', offset: 0.3 }, { transform: 'translateX(0)' }], 620);
		const done = impact(el, HERO_AT, 26, filter, true);
		shownHearts = hearts;
		pop('−1½ ♥', { x: HERO_AT.x, y: HERO_AT.y - 0.32 }, 'hurt');
		await done;
		await sleep(380);
		bossPose = 'idle';
		heroPose = hearts > 0 ? 'idle' : 'hurt';
		busy = false;
	}

	/** A friend in the same fight hit the boss: a flash on the boss, no change to this child's hero. */
	export function friendHit(element: Element) {
		flash(ELEMENT_TINT[element][0], 0.3);
		void impact(element, ENEMY_AT, 22);
	}

	export async function enter() {
		await move(enemyEl, [{ opacity: 0, transform: 'translateX(18cqw) scale(0.9)' }, { opacity: 1, transform: 'translateX(0) scale(1)' }], 620, 'cubic-bezier(.2,.9,.3,1.2)');
	}

	export function celebrate() {
		cheering = true;
		heroPose = 'victory';
	}

	export function fall() {
		fallen = true;
		heroPose = 'hurt';
	}

	export function reset() {
		fallen = false;
		cheering = false;
		heroPose = 'idle';
		bossPose = 'idle';
	}

	const bossSrc = $derived(bossArt(world, enemy === 'beaten' ? 'defeat' : bossPose));
	const halfHearts = $derived(heartIcons(shownHearts, maxHearts));
	const lowBoss = $derived(!!boss && shownBoss <= 2 && shownBoss > 0);
</script>

<div class="stage mode-{mode}" class:still class:dim bind:this={stageEl} style:--aura={art.aura} style:--light-top={art.light[0]} style:--light-bottom={art.light[1]}>
	<div class="backdrop">
		<img src={battleBg(world)} alt="" draggable="false" />
	</div>
	<div class="light" aria-hidden="true"></div>

	{#if friends.length}
		<div class="friends" aria-hidden="true">
			{#each friends.slice(0, 2) as friend, i (friend.id)}
				{#if friend.hero}
					<img class="friend" style:--i={i} src={heroArt(friend.hero, 'idle')} alt="" draggable="false" />
				{/if}
			{/each}
		</div>
	{/if}

	<div class="actor hero" class:fallen class:cheering bind:this={heroEl}>
		<span class="shadow"></span>
		<img src={heroArt(hero, heroPose)} alt={heroName} draggable="false" />
	</div>

	{#if enemy !== 'none'}
		<div
			class="actor enemy enemy-{enemy}"
			class:boss={!!boss}
			class:foe={!boss}
			class:low={lowBoss}
			style:--boss-w="{art.bossSize * 100}cqw"
			bind:this={enemyEl}
		>
			<span class="shadow"></span>
			<img src={bossSrc} alt={boss?.name ?? foe?.name ?? ''} draggable="false" />
		</div>
	{/if}

	<img class="burst" bind:this={burstEl} alt="" aria-hidden="true" />
	<div class="sheet" bind:this={sheetEl} aria-hidden="true"></div>
	<Particles bind:this={air} motes={art.motes} calm={mode !== 'battle'} />
	<div class="flash" bind:this={flashEl} aria-hidden="true"></div>

	{#each pops as p (p.id)}
		<span class="pop pop-{p.tone}" style:left="{p.x * 100}%" style:top="{p.y * 100}%">{p.text}</span>
	{/each}

	{#if mode === 'battle'}
		<div class="hud hud-hero">
			<img class="face" src={heroArt(hero, 'portrait')} alt="" />
			<div>
				<p class="name">{heroName}</p>
				<p class="hearts" aria-label="Hati: {shownHearts / 2} daripada {maxHearts / 2}">
					{#each halfHearts as h, i (i)}<img src="/story/ui/heart_{h}.webp" alt="" />{/each}
				</p>
			</div>
		</div>
		{#if boss || foe}
			<div class="hud hud-enemy" class:boss={!!boss}>
				<p class="name">{boss?.name ?? foe?.name}</p>
				{#if boss}
					<p class="bars" aria-label="Boss: {shownBoss} daripada {boss.max} bar">
						{#each Array(boss.max) as _, i (i)}<span class:on={i < shownBoss}></span>{/each}
					</p>
				{:else if foe}
					<p class="foe-count">Musuh {foe.index} / {foe.total}</p>
				{/if}
			</div>
		{/if}
	{/if}
</div>

<style>
	.stage {
		position: relative;
		container-type: inline-size;
		aspect-ratio: 16 / 9;
		width: 100%;
		overflow: hidden;
		border-radius: 14px;
		background: #0b1622;
		isolation: isolate;
		user-select: none;
	}
	.backdrop {
		position: absolute;
		inset: -2%;
	}
	.backdrop img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		animation: drift 18s ease-in-out infinite alternate;
	}
	.mode-travel .backdrop img {
		animation: travel 3.2s linear infinite;
		transform-origin: 30% 60%;
	}
	.dim .backdrop img {
		filter: brightness(0.55) saturate(0.9);
	}
	@keyframes drift {
		from {
			transform: scale(1.04) translateX(0);
		}
		to {
			transform: scale(1.08) translateX(-1.5%);
		}
	}
	@keyframes travel {
		from {
			transform: scale(1.18) translateX(4%);
		}
		to {
			transform: scale(1.18) translateX(-4%);
		}
	}
	.light {
		position: absolute;
		inset: 0;
		background:
			linear-gradient(180deg, var(--light-top), transparent 45%, var(--light-bottom)),
			radial-gradient(ellipse at 74% 55%, color-mix(in srgb, var(--aura) 18%, transparent), transparent 55%);
		pointer-events: none;
	}

	.actor {
		position: absolute;
		bottom: 7%;
		display: grid;
		place-items: end center;
		will-change: transform;
	}
	.actor img {
		position: relative;
		width: 100%;
		height: 100%;
		object-fit: contain;
		object-position: bottom center;
		filter: drop-shadow(0 0.4cqw 0.6cqw rgb(0 0 0 / 0.45));
	}
	.shadow {
		position: absolute;
		bottom: -1.2cqw;
		left: 50%;
		width: 70%;
		height: 3cqw;
		transform: translateX(-50%);
		border-radius: 50%;
		background: radial-gradient(rgb(0 0 0 / 0.42), transparent 70%);
	}
	.hero {
		left: 7%;
		width: 24cqw;
		height: 28cqw;
		z-index: 3;
	}
	.hero img {
		animation: breathe 2.4s ease-in-out infinite;
		transform-origin: bottom center;
	}
	.mode-travel .hero img {
		animation: walk 0.42s ease-in-out infinite;
	}
	.hero.fallen img {
		filter: grayscale(0.85) brightness(0.7);
		transform: rotate(-10deg) translateY(1.5cqw);
		animation: none;
	}
	.hero.cheering img {
		animation: hop 0.9s ease-in-out infinite;
	}
	.friends {
		position: absolute;
		left: 1%;
		bottom: 18%;
		z-index: 2;
		display: flex;
	}
	.friend {
		width: 13cqw;
		height: 15cqw;
		object-fit: contain;
		object-position: bottom;
		margin-left: calc(var(--i) * -4cqw);
		filter: brightness(0.92) drop-shadow(0 0.3cqw 0.5cqw rgb(0 0 0 / 0.4));
		animation: breathe 2.8s ease-in-out infinite;
		animation-delay: calc(var(--i) * -0.7s);
	}
	.enemy {
		right: 1%;
		z-index: 2;
	}
	/* The boss fills most of the stage's height: a legend should loom over the heroes. */
	.enemy.boss {
		bottom: 2%;
		width: var(--boss-w);
		height: 53cqw;
	}
	.enemy.foe {
		width: calc(var(--boss-w) * 0.72);
		height: 36cqw;
		right: 5%;
	}
	.enemy.foe img {
		filter: brightness(0.5) saturate(1.5) drop-shadow(0 0 1.4cqw var(--aura)) drop-shadow(0 0 0.4cqw var(--aura));
		opacity: 0.92;
	}
	.enemy img {
		animation: loom 3.2s ease-in-out infinite;
		transform-origin: bottom center;
	}
	.enemy.low img {
		animation-duration: 1.6s;
		filter: drop-shadow(0 0 1.6cqw var(--aura)) drop-shadow(0 0.4cqw 0.6cqw rgb(0 0 0 / 0.45));
	}
	.enemy-enter {
		opacity: 0;
	}
	.enemy-gone img {
		animation: vanish 0.9s ease-in forwards;
	}
	.enemy-beaten img {
		animation: sink 1.6s ease-in forwards;
	}
	@keyframes breathe {
		50% {
			transform: scaleY(1.018) translateY(-0.2cqw);
		}
	}
	@keyframes walk {
		50% {
			transform: translateY(-0.9cqw) rotate(1.5deg);
		}
	}
	@keyframes hop {
		40% {
			transform: translateY(-2.4cqw);
		}
	}
	@keyframes loom {
		50% {
			transform: scale(1.015) translateY(-0.5cqw);
		}
	}
	@keyframes vanish {
		to {
			opacity: 0;
			transform: scale(0.75) translateY(-3cqw);
			filter: blur(6px) brightness(2);
		}
	}
	@keyframes sink {
		to {
			opacity: 0.25;
			transform: translateY(6cqw) scale(0.94);
			filter: grayscale(0.8) brightness(0.6);
		}
	}

	.burst {
		position: absolute;
		z-index: 4;
		pointer-events: none;
		opacity: 0;
		transform: translate(-50%, -50%);
	}
	.sheet {
		position: absolute;
		z-index: 4;
		width: 26cqw;
		aspect-ratio: 1;
		transform: translate(-50%, -50%);
		background-size: 400% 300%;
		opacity: 0;
		pointer-events: none;
		mix-blend-mode: screen;
	}
	.stage :global(.bolt) {
		position: absolute;
		z-index: 4;
		width: 16cqw;
		pointer-events: none;
	}
	.flash {
		position: absolute;
		inset: 0;
		z-index: 6;
		opacity: 0;
		pointer-events: none;
		mix-blend-mode: screen;
	}

	.pop {
		position: absolute;
		z-index: 7;
		transform: translate(-50%, 0);
		font: 700 clamp(1rem, 3.4cqw, 2.4rem) / 1 var(--font-pixel, var(--font-display));
		color: #fff;
		-webkit-text-stroke: 0.25cqw #1a1020;
		paint-order: stroke fill;
		text-shadow: 0 0.3cqw 0 rgb(0 0 0 / 0.4);
		white-space: nowrap;
		animation: float-up 1.3s ease-out forwards;
		pointer-events: none;
	}
	.pop-hurt {
		color: #ff6b6b;
	}
	.pop-heal {
		color: #7dffa8;
	}
	.pop-weak {
		color: #ffe066;
		font-size: clamp(1.1rem, 4cqw, 2.8rem);
	}
	@keyframes float-up {
		0% {
			opacity: 0;
			transform: translate(-50%, 1.5cqw) scale(0.6);
		}
		15% {
			opacity: 1;
			transform: translate(-50%, 0) scale(1.15);
		}
		100% {
			opacity: 0;
			transform: translate(-50%, -6cqw) scale(1);
		}
	}

	.hud {
		position: absolute;
		top: max(2.4cqw, 6px);
		z-index: 8;
		display: flex;
		align-items: center;
		gap: 1cqw;
		padding: 0.7cqw 1.4cqw 0.7cqw 0.7cqw;
		border: 0.25cqw solid #d9a441;
		border-radius: 1.2cqw;
		background: linear-gradient(180deg, rgb(16 34 72 / 0.92), rgb(9 20 46 / 0.92));
		box-shadow: 0 0 0 0.18cqw #5a3b10, 0 0.6cqw 1.4cqw rgb(0 0 0 / 0.35);
		color: #fff4d8;
	}
	.hud p {
		margin: 0;
	}
	.hud-hero {
		left: max(2.4cqw, 6px);
	}
	.face {
		width: max(6cqw, 26px);
		height: max(6cqw, 26px);
		border-radius: 50%;
		border: 0.25cqw solid #d9a441;
		object-fit: cover;
		object-position: 50% 8%;
		background: #23407a;
	}
	.name {
		font: 700 clamp(0.7rem, 1.9cqw, 1.3rem) / 1.1 var(--font-pixel, var(--font-display));
		letter-spacing: 0.02em;
	}
	.hearts {
		display: flex;
		gap: 0.2cqw;
		margin-top: 0.3cqw;
	}
	.hearts img {
		width: max(2.6cqw, 13px);
		height: auto;
	}
	.hud-enemy {
		right: max(2.4cqw, 6px);
		flex-direction: column;
		align-items: flex-end;
		gap: 0.5cqw;
		padding: 0.8cqw 1.4cqw;
		background: linear-gradient(180deg, rgb(80 14 22 / 0.92), rgb(46 8 16 / 0.92));
	}
	.bars {
		display: flex;
		gap: 0.4cqw;
	}
	.bars span {
		width: max(4.6cqw, 16px);
		height: max(1.5cqw, 7px);
		border-radius: 0.4cqw;
		border: 0.18cqw solid #ffd8a0;
		background: rgb(0 0 0 / 0.5);
		transition:
			background 300ms,
			transform 300ms;
	}
	.bars span.on {
		background: linear-gradient(180deg, #ff6b5a, #c8102e);
		box-shadow: 0 0 0.8cqw rgb(255 80 60 / 0.6);
	}
	.foe-count {
		font-weight: 800;
		font-size: clamp(0.6rem, 1.5cqw, 1rem);
		color: #ffd8a0;
	}

	.still .backdrop img,
	.still .actor img,
	.still .friend {
		animation: none !important;
	}
</style>
