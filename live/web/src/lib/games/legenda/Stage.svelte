<!--
	The battlefield: the world's painting (the hero's path on the left, the boss's arena on the right, the
	title plate and minimap as painted), with the live parts laid over it in the same places: six hearts, the
	boss's name and five bars, and the five elements. The hero, the boss and the two small enemies are
	separate layers cut from the painting, so they can act while the scene stays still.

	Poses are separate drawings (static/story/), switched on cue and moved with the Web Animations API:
	an attack is a wind-up, the element flying across the scene, its burst and 12-frame impact on the
	target, a flash and a shake; a counterattack is the enemy's lunge and strike on the hero. The HUD shows
	the server's hearts and boss bars, but holds the old number until the hit in the animation lands.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import Particles from './Particles.svelte';
	import {
		ELEMENTS,
		ELEMENT_NAME,
		ELEMENT_TINT,
		WORLD_ART,
		battleBg,
		bossArt,
		elementIcon,
		field,
		FX_ANCHOR,
		fxSlash,
		fxStill,
		heartIcons,
		heroArt,
		heroWeaponArt,
		ARMED_POSES,
		minionArt,
		reducedMotion,
		sleep,
		symbol,
		type Element,
		type Pose,
		storyArt
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
		dim = false,
		elements = null,
		weapon = null
	}: {
		world: number;
		hero: string;
		heroName?: string;
		hearts: number;
		maxHearts?: number;
		/** A road enemy: which of the five it is (the two small enemies take turns). */
		foe?: { name: string; index: number; total: number } | null;
		/** The boss: its name and bars. */
		boss?: { name: string; hp: number; max: number; subtitle?: string } | null;
		/** Where the enemy is: arriving, standing, gone (cleared), or beaten (the boss falls). */
		enemy?: 'none' | 'enter' | 'idle' | 'gone' | 'beaten';
		friends?: Friend[];
		/** 'battle' (still), 'travel' (the hero walks the path) or 'scenery' (no HUD, under a card). */
		mode?: 'battle' | 'travel' | 'scenery';
		dim?: boolean;
		/** The element dock: unlocked at the boss, which is selected, and what a tap does. */
		elements?: { unlocked: boolean; selected: string; disabled: boolean; onpick: (el: Element) => void } | null;
		/** The element whose weapon the hero holds (the one the server has confirmed); null before the elements unlock. */
		weapon?: Element | null;
	} = $props();

	const art = $derived(WORLD_ART[world]);
	const lay = $derived(field(world));
	// The hero's figure height on the scene, and the effects' centres, as fractions of the scene. The pose
	// pictures carry room above the figure for the tallest pose (all six share one scale and ground), so
	// the picture's box is that much taller than the figure.
	const FIGURE_H = 0.23;
	const HERO_H = FIGURE_H * 1.17;
	const heroAt = $derived({ x: lay.hero.x, y: lay.hero.y - FIGURE_H * 0.55 });
	const minion = $derived(foe && foe.index % 2 === 0 ? lay.minB : lay.minA);
	const target = $derived(boss ? lay.boss : minion);
	const enemyAt = $derived({ x: target.x + target.w / 2, y: target.y + target.h * (boss ? 0.42 : 0.5) });
	// Which side of the hero the enemy stands on: -1 left, 1 right. The boss is on the right; a small enemy
	// may be on either side, and the two face each other (the sprites are drawn facing right).
	const side = $derived(foe && !boss ? (enemyAt.x < heroAt.x ? -1 : 1) : 1);

	let still = $state(false);
	let busy = $state(false);
	let heroPose = $state<Pose>('idle');
	// The weapon sprite when the pose shows one; a missing file falls back to the base sprite.
	let weaponFailed = $state<string | null>(null);
	const armed = $derived(!!weapon && ARMED_POSES.includes(heroPose) && weaponFailed !== `${hero}/${weapon}`);
	const heroSrc = $derived(armed && weapon ? heroWeaponArt(hero, weapon) : heroArt(hero, heroPose));
	let shownHearts = $state(12);
	let shownBoss = $state(5);
	let fallen = $state(false);
	let cheering = $state(false);
	let hit = $state(false);
	let lunge = $state(0);
	let pops = $state<{ id: number; text: string; x: number; y: number; tone: string }[]>([]);
	let popId = 0;

	let stageEl: HTMLDivElement;
	let heroEl: HTMLDivElement;
	let bossEl = $state<HTMLDivElement>();
	let minionEl = $state<HTMLDivElement>();
	// Whichever of the two is fighting now: the boss at the boss, a small enemy on the road.
	const enemyEl = $derived(boss ? bossEl : minionEl);
	let camEl = $state<HTMLDivElement>();
	let flashEl: HTMLDivElement;
	let fxEl: HTMLDivElement;
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

	function pop(text: string, at: { x: number; y: number }, tone: 'hurt' | 'heal' | 'hit' | 'weak') {
		const id = ++popId;
		pops = [...pops, { id, text, x: at.x, y: at.y, tone }];
		setTimeout(() => (pops = pops.filter((p) => p.id !== id)), 1400);
	}

	function move(el: HTMLElement | undefined, frames: Keyframe[], ms: number, easing = 'ease-out'): Promise<void> {
		if (!el || still) return sleep(still ? Math.min(ms, 120) : ms);
		return el.animate(frames, { duration: ms, easing, fill: 'forwards' }).finished.then(() => undefined, () => undefined);
	}

	// The camera: the world layers (not the HUD) lean in toward a point and back out.
	let zoomed = 1;
	async function zoomIn(at: { x: number; y: number }, k: number, ms: number) {
		if (!camEl || still) return;
		camEl.style.transformOrigin = `${at.x * 100}% ${at.y * 100}%`;
		zoomed = k;
		await camEl.animate([{ transform: 'scale(1)' }, { transform: `scale(${k})` }], { duration: ms, easing: 'cubic-bezier(.3,.7,.3,1)', fill: 'forwards' }).finished.then(() => undefined, () => undefined);
	}
	async function zoomOut(ms: number) {
		if (!camEl || still) return;
		await camEl.animate([{ transform: `scale(${zoomed})` }, { transform: 'scale(1)' }], { duration: ms, easing: 'ease-in-out', fill: 'forwards' }).finished.then(() => undefined, () => undefined);
		for (const a of camEl.getAnimations()) a.cancel();
		zoomed = 1;
	}

	function shake(strength = 1) {
		if (still || !stageEl) return;
		const d = 0.5 * strength;
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

	/**
	 * The element's attack effect, frame by frame: the 12 supplied frames play on the target at about 12 fps
	 * (a 4 by 3 sheet, frame 314 by 418), with sparks and a glow. `mirror` turns it to face the other way
	 * (the enemy's counterattack on the hero). With reduced motion only the strongest frame shows.
	 */
	async function impact(el: Element, at: { x: number; y: number }, size: number, filter = '', mirror = false) {
		const tint = ELEMENT_TINT[el];
		air?.burst(at.x, at.y, [tint[0], tint[1], '#ffffff'], still ? 0 : 54);
		if (!fxEl) return;
		const height = (size * 418) / 314;
		const down = FX_ANCHOR[el] ?? 0.5;
		fxEl.style.backgroundImage = `url(${fxSlash(el)})`;
		fxEl.style.left = `${at.x * 100}%`;
		fxEl.style.top = `${at.y * 100}%`;
		fxEl.style.width = `${size}cqw`;
		fxEl.style.height = `${height}cqw`;
		fxEl.style.filter = filter;
		fxEl.style.transform = `translate(-50%, -${down * 100}%) scaleX(${mirror ? -1 : 1})`;
		fxEl.style.opacity = '1';
		const show = (frame: number) => {
			fxEl.style.backgroundPosition = `${(frame % 4) * 33.3333}% ${Math.floor(frame / 4) * 50}%`;
		};
		if (still) {
			show(5);
			await sleep(420);
		} else {
			for (let frame = 0; frame < 12; frame++) {
				show(frame);
				await sleep(frame < 6 ? 72 : 84);
			}
		}
		fxEl.style.opacity = '0';
	}

	/** A projectile: the element still flying from one place to another, small and spinning. */
	function fly(el: Element, from: { x: number; y: number }, to: { x: number; y: number }, filter = '', size = 14) {
		if (still || !stageEl) return sleep(80);
		const img = document.createElement('img');
		img.src = fxStill(el);
		img.alt = '';
		img.className = 'bolt';
		img.style.filter = filter;
		img.style.width = `${size}cqw`;
		(camEl ?? stageEl).appendChild(img);
		return img
			.animate(
				[
					{ left: `${from.x * 100}%`, top: `${from.y * 100}%`, transform: 'translate(-50%,-50%) scale(0.25) rotate(0deg)', opacity: 0.4 },
					{ offset: 0.2, opacity: 1 },
					{ left: `${to.x * 100}%`, top: `${to.y * 100}%`, transform: 'translate(-50%,-50%) scale(0.55) rotate(320deg)', opacity: 1 }
				],
				{ duration: 420, easing: 'ease-in' }
			)
			.finished.then(
				() => img.remove(),
				() => img.remove()
			);
	}

	// ------------------------------------------------------------ the moves (called by the player screen)

	/** A right answer: the hero gathers, slides in (or casts), and the element's frames play on the target. */
	export async function attack(element: Element | null, opts: { weak?: boolean; finishing?: boolean; healed?: boolean } = {}) {
		busy = true;
		const el: Element = element ?? 'angin';
		const blade = !element || element === 'api' || element === 'angin' || element === 'air';
		heroPose = 'ready';
		if (element) flash(ELEMENT_TINT[el][1], 0.22);
		await move(heroEl, [{ transform: 'translateX(-50%)' }, { transform: `translateX(calc(-50% - ${1.2 * side}cqw))` }], 140);
		heroPose = blade ? 'attack' : 'cast';
		// How far the hero slides toward the target: a share of the gap, never more than a fifth of the scene.
		const gap = Math.abs(enemyAt.x - heroAt.x) * 100;
		const slide = blade ? Math.min(gap * 0.4, 20) * side : 0;
		await move(heroEl, [{ transform: `translateX(calc(-50% - ${1.2 * side}cqw))` }, { transform: `translateX(calc(-50% + ${slide}cqw))` }], 180, 'cubic-bezier(.5,0,.9,.4)');
		hit = true;
		const done = impact(el, enemyAt, boss ? 34 : 26, '', side < 0);
		// The target reacts a few frames in, as the effect reaches it.
		await sleep(still ? 80 : 330);
		flash('#ffffff', 0.6);
		shake(opts.finishing ? 1.8 : 1.1);
		void move(
			enemyEl,
			[
				{ transform: 'translateX(0) rotate(0)', filter: 'brightness(1)' },
				{ transform: 'translateX(1.4cqw) rotate(1.5deg)', filter: 'brightness(2.4)', offset: 0.2 },
				{ transform: 'translateX(0.7cqw) rotate(0.6deg)', filter: 'brightness(1)', offset: 0.5 },
				{ transform: 'translateX(0) rotate(0)', filter: 'brightness(1)' }
			],
			240 + 280
		);
		if (boss) shownBoss = boss.hp;
		pop(opts.weak ? 'KELEMAHAN!' : boss ? '−1 bar' : 'Kena!', { x: enemyAt.x, y: enemyAt.y - 0.2 }, opts.weak ? 'weak' : 'hit');
		await done;
		heroPose = 'ready';
		if (slide) await move(heroEl, [{ transform: `translateX(calc(-50% + ${slide}cqw))` }, { transform: 'translateX(-50%)' }], 180, 'ease-in-out');
		hit = false;
		heroPose = 'idle';
		shownHearts = hearts;
		if (opts.healed) pop('+½ ♥', { x: heroAt.x, y: heroAt.y - 0.14 }, 'heal');
		await sleep(200);
		busy = false;
	}

	/** A wrong answer: the enemy's unavoidable counterattack. */
	export async function counter() {
		busy = true;
		const el = art.strikes;
		const filter = art.strikeFilter ?? '';
		// the camera leans in toward the two of them (a little less when the boss is far across the scene)
		void zoomIn({ x: (enemyAt.x + heroAt.x) / 2, y: (enemyAt.y + heroAt.y) / 2 }, boss ? 1.1 : 1.2, 560);
		await move(
			enemyEl,
			[
				{ transform: 'scale(1)', filter: 'brightness(1)' },
				{ transform: 'scale(1.05)', filter: `brightness(1.5) drop-shadow(0 0 2cqw ${art.aura})` }
			],
			360
		);
		lunge = 1;
		const from = { x: enemyAt.x - side * target.w * 0.25, y: enemyAt.y };
		await fly(el, from, heroAt, filter, boss ? 16 : 11);
		heroPose = 'hurt';
		flash('#ff4a4a', 0.5);
		shake(1.5);
		void move(heroEl, [{ transform: 'translateX(-50%)' }, { transform: `translateX(calc(-50% - ${3 * side}cqw))`, offset: 0.3 }, { transform: 'translateX(-50%)' }], 620);
		const done = impact(el, heroAt, 22, filter, side > 0);
		shownHearts = hearts;
		pop('−1½ ♥', { x: heroAt.x, y: heroAt.y - 0.14 }, 'hurt');
		await done;
		await sleep(380);
		lunge = 0;
		heroPose = hearts > 0 ? 'idle' : 'hurt';
		await zoomOut(420);
		busy = false;
	}

	/** A friend in the same fight hit the boss: a flash on the boss, no change to this child's hero. */
	export function friendHit(element: Element) {
		flash(ELEMENT_TINT[element][0], 0.3);
		void impact(element, enemyAt, 20);
	}

	export async function enter() {
		await move(enemyEl, [{ opacity: 0, transform: `translateX(${-8 * side}cqw)` }, { opacity: 1, transform: 'translateX(0)' }], 620, 'cubic-bezier(.2,.9,.3,1.2)');
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
	}

	const halfHearts = $derived(heartIcons(shownHearts, maxHearts));
	const lowBoss = $derived(!!boss && shownBoss <= 2 && shownBoss > 0);
	const pct = (v: number) => `${(v * 100).toFixed(3)}%`;
	// The paintings carry a "Story Mode" plate in the top left (about 4..250 by 4..100 of 1536 pixels across);
	// the game's own name covers it.
	const titlePlate = $derived({ x: 4 / 1536, y: (4 * lay.ar) / 1536, w: 246 / 1536, h: (96 * lay.ar) / 1536 });
	const place = (b: { x: number; y: number; w: number; h: number }) => `left:${pct(b.x)};top:${pct(b.y)};width:${pct(b.w)};height:${pct(b.h)}`;
	const dockCols = $derived(ELEMENTS.length);
</script>

<div
	class="stage mode-{mode}"
	class:still
	class:dim
	bind:this={stageEl}
	style:aspect-ratio={lay.ar}
	style:--aura={art.aura}
>
	<div class="world" bind:this={camEl}>
		<img class="field" src={battleBg(world)} alt="" draggable="false" />

		{#if friends.length}
			<div class="friends" aria-hidden="true">
				{#each friends.slice(0, 2) as friend, i (friend.id)}
					{#if friend.hero}
						<img
							class="friend"
							style:left={pct(Math.max(0.02, lay.hero.x - 0.1 - i * 0.07))}
							style:bottom={pct(1 - lay.hero.y - 0.02 * i)}
							style:height={pct(HERO_H * 0.78)}
							src={heroArt(friend.hero, 'idle')}
							alt=""
							draggable="false"
						/>
					{/if}
				{/each}
			</div>
		{/if}

		<!-- the boss stands in its arena the whole time, as in the painting; the small enemies fight on the road -->
		<div
			class="actor enemy boss enemy-{boss ? enemy : 'idle'}"
			class:low={lowBoss}
			class:lunge={!!boss && lunge === 1}
			class:hit={!!boss && hit}
			style={place(lay.boss)}
			bind:this={bossEl}
		>
			<img src={bossArt(world)} alt={boss?.name ?? ''} draggable="false" />
		</div>
		{#if foe && !boss && enemy !== 'none'}
			<div class="actor enemy foe enemy-{enemy}" class:lunge={lunge === 1} class:hit style="{place(minion)}; --side: {side}" bind:this={minionEl}>
				<img class:turned={side > 0} src={minionArt(world, foe.index % 2 === 0 ? 'b' : 'a')} alt={foe.name} draggable="false" />
			</div>
		{/if}

		<!-- the hero -->
		<div
			class="actor hero"
			class:fallen
			class:cheering
			class:has-weapon={armed}
			bind:this={heroEl}
			style:left={pct(lay.hero.x)}
			style:bottom={pct(1 - lay.hero.y)}
			style:height={pct(HERO_H)}
		>
			<span class="shadow"></span>
			<img
				class:armed
				class:turned={side < 0}
				src={heroSrc}
				alt={heroName}
				draggable="false"
				onerror={() => {
					if (armed && weapon) weaponFailed = `${hero}/${weapon}`;
				}}
			/>
		</div>

		<div class="fx" bind:this={fxEl} aria-hidden="true"></div>
		<Particles bind:this={air} motes={art.motes} calm />
		<div class="flash" bind:this={flashEl} aria-hidden="true"></div>

		{#each pops as p (p.id)}
			<span class="pop pop-{p.tone}" style:left={pct(p.x)} style:top={pct(p.y)}>{p.text}</span>
		{/each}
	</div>

	<!-- the game's name, over the plate the painting has in its corner -->
	<p class="hud plate" style={place(titlePlate)} aria-hidden="true"><span class="plate-a">Hikayat</span><span class="plate-b">Lima Alam</span></p>

	{#if mode !== 'scenery'}
		<!-- hearts, where the painting had its five -->
		<p class="hud hearts" style={place(lay.hearts)} aria-label="Hati: {shownHearts / 2} daripada {maxHearts / 2}">
			{#each halfHearts as h, i (i)}<img src={storyArt(`ui/heart_${h}.webp`)} alt="" />{/each}
		</p>

		<!-- the world, the enemy's name and its five bars, where the painting had them -->
		{#if boss || foe}
			<div class="hud panel" class:boss={!!boss} style={place(lay.panel)}>
				<img class="emblem" src={symbol(world)} alt="" />
				<div class="names">
					<p class="where">{boss ? (boss.subtitle ?? '') : ''}</p>
					<p class="who">{boss?.name ?? foe?.name}</p>
				</div>
				{#if boss}
					<p class="bars" aria-label="Boss: {shownBoss} daripada {boss.max} bar">
						{#each Array(boss.max) as _, i (i)}<span class:on={i < shownBoss}></span>{/each}
					</p>
				{:else if foe}
					<p class="foe-count">Musuh {foe.index} / {foe.total}</p>
				{/if}
			</div>
		{/if}

		<!-- the five elements, where the painting had them; locked until the road is cleared -->
		{#if elements}
			<div class="hud dock" class:locked={!elements.unlocked} style="{place(lay.dock)};--cols:{dockCols}" role="radiogroup" aria-label="Pilih elemen serangan">
				{#each ELEMENTS as el, i (el)}
					<button
						type="button"
						role="radio"
						aria-checked={elements.selected === el}
						aria-label="{ELEMENT_NAME[el]} (Alt+{i + 1})"
						class:on={elements.unlocked && elements.selected === el}
						disabled={!elements.unlocked || elements.disabled}
						onclick={() => elements.onpick(el)}
					>
						<img src={elementIcon(el)} alt="" />
						<span class="key">{i + 1}</span>
					</button>
				{/each}
			</div>
		{/if}
	{/if}
</div>

<style>
	.stage {
		position: relative;
		container-type: inline-size;
		width: 100%;
		overflow: hidden;
		border-radius: 14px;
		background: #0b1622;
		isolation: isolate;
		user-select: none;
	}
	.world {
		position: absolute;
		inset: 0;
		z-index: 1;
	}
	.field {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: fill;
	}
	.dim .field {
		filter: brightness(0.55) saturate(0.9);
	}

	.actor {
		position: absolute;
		will-change: transform;
	}
	.actor img {
		display: block;
		filter: drop-shadow(0 0.3cqw 0.4cqw rgb(0 0 0 / 0.4));
	}
	.hero {
		z-index: 4;
		transform: translateX(-50%);
		transform-origin: 50% 100%;
	}
	.hero.has-weapon {
		display: flex;
		align-items: flex-end;
		justify-content: center;
	}
	/* The weapon sprites are taller and carry the blade's flames, so they are drawn larger, standing on the same ground. */
	.hero img.armed {
		height: 109%;
		flex: none;
	}
	.hero img {
		height: 100%;
		width: auto;
		animation: breathe 2.4s ease-in-out infinite;
		transform-origin: bottom center;
	}
	.hero .shadow {
		position: absolute;
		bottom: -0.6cqw;
		left: 50%;
		width: 80%;
		height: 2cqw;
		transform: translateX(-50%);
		border-radius: 50%;
		background: radial-gradient(rgb(0 0 0 / 0.42), transparent 70%);
	}
	.mode-travel .hero {
		animation: walk-in 2.8s ease-out both;
	}
	.mode-travel .hero img {
		animation: step 0.42s ease-in-out infinite;
	}
	.hero.fallen img {
		filter: grayscale(0.85) brightness(0.7);
		transform: rotate(-10deg) translateY(1cqw);
		animation: none;
	}
	.hero.cheering img {
		animation: hop 0.9s ease-in-out infinite;
	}
	.friends {
		position: absolute;
		inset: 0;
		z-index: 3;
		pointer-events: none;
	}
	.friend {
		position: absolute;
		width: auto;
		filter: brightness(0.92) drop-shadow(0 0.3cqw 0.4cqw rgb(0 0 0 / 0.4));
		animation: breathe 2.8s ease-in-out infinite;
	}

	.enemy {
		z-index: 2;
		transform-origin: 50% 100%;
	}
	.enemy img {
		width: 100%;
		height: 100%;
		object-fit: fill;
	}
	.enemy.boss img {
		animation: loom 3.4s ease-in-out infinite;
		transform-origin: bottom center;
	}
	.enemy.foe {
		z-index: 3;
		transform: scale(1.5);
	}
	.enemy.foe img {
		animation: bob 1.6s ease-in-out infinite;
		transform-origin: bottom center;
	}
	.enemy.low img {
		animation-duration: 1.6s;
		filter: drop-shadow(0 0 1.6cqw var(--aura)) drop-shadow(0 0.3cqw 0.4cqw rgb(0 0 0 / 0.4));
	}
	.enemy.lunge {
		transition: transform 280ms ease-out;
		transform: translateX(-5cqw) scale(1.04);
	}
	.enemy.foe.lunge {
		transform: translateX(calc(-9cqw * var(--side, 1))) scale(1.5);
	}
	/* turned to face the other way: `scale` is its own property, so it does not fight the animations on `transform` */
	.hero img.turned,
	.enemy.foe img.turned {
		scale: -1 1;
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
	@keyframes walk-in {
		from {
			transform: translateX(calc(-50% - 20cqw));
			opacity: 0.2;
		}
		to {
			transform: translateX(-50%);
		}
	}
	@keyframes step {
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
			transform: scale(1.012) translateY(-0.3cqw);
		}
	}
	@keyframes bob {
		50% {
			transform: translateY(-0.6cqw) scale(1.03, 0.97);
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
			transform: translateY(4cqw) scale(0.96);
			filter: grayscale(0.8) brightness(0.6);
		}
	}

	.fx {
		position: absolute;
		z-index: 6;
		background-size: 400% 300%;
		background-repeat: no-repeat;
		opacity: 0;
		pointer-events: none;
		mix-blend-mode: screen;
		/* Some frames were cut flush with their cell: fade the edges so no rectangle shows. */
		-webkit-mask-image: radial-gradient(closest-side, #000 70%, transparent 100%);
		mask-image: radial-gradient(closest-side, #000 70%, transparent 100%);
	}
	.stage :global(.bolt) {
		position: absolute;
		z-index: 6;
		pointer-events: none;
	}
	.flash {
		position: absolute;
		inset: 0;
		z-index: 7;
		opacity: 0;
		pointer-events: none;
		mix-blend-mode: screen;
	}

	.pop {
		position: absolute;
		z-index: 8;
		transform: translate(-50%, 0);
		font: 700 clamp(1rem, 3.2cqw, 2.4rem) / 1 var(--font-pixel, var(--font-display));
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
		font-size: clamp(1.1rem, 3.8cqw, 2.8rem);
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

	/* ---- the live HUD, in the places the painting had its own */
	/* On a narrow screen the painting's HUD places are too small to read: the live HUD grows over the
	   painting (whose own HUD was painted out), from the corner it belongs to. */
	@container (max-width: 560px) {
		.hud.hearts {
			scale: 1.4;
			transform-origin: 0 0;
		}
		.hud.panel {
			scale: 1.4;
			transform-origin: 100% 0;
		}
		.hud.dock {
			scale: 1.2;
			transform-origin: 100% 100%;
		}
	}
	@container (min-width: 561px) and (max-width: 860px) {
		.hud.hearts,
		.hud.panel {
			scale: 1.15;
		}
		.hud.hearts {
			transform-origin: 0 0;
		}
		.hud.panel {
			transform-origin: 100% 0;
		}
	}
	.plate {
		display: grid;
		align-content: center;
		justify-items: center;
		gap: 0.15cqw;
		border-radius: 1cqw;
		background: linear-gradient(180deg, #3a2414, #22150c);
		box-shadow:
			inset 0 0 0 0.25cqw #d9a441,
			inset 0 0 0 0.45cqw #22150c,
			0 0.3cqw 0.8cqw rgb(0 0 0 / 0.45);
		color: #ffe7a8;
		text-align: center;
		line-height: 1;
	}
	.plate-a {
		font: 700 clamp(0.6rem, 2.1cqw, 1.9rem) / 1 var(--font-display);
		text-shadow: 0 0.2cqw 0 #7a4a12;
	}
	.plate-b {
		font: 700 clamp(0.4rem, 0.95cqw, 0.85rem) / 1 var(--font-display);
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: #f3d58a;
	}
	.hud {
		position: absolute;
		z-index: 9;
		margin: 0;
		color: #fff4d8;
	}
	.hearts {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.2cqw;
		padding: 0 0.3cqw;
		border-radius: 1cqw;
		background: linear-gradient(180deg, rgb(10 18 40 / 0.55), rgb(10 18 40 / 0.25));
	}
	.hearts img {
		height: 88%;
		width: auto;
		max-width: 16%;
		filter: drop-shadow(0 0.2cqw 0 rgb(0 0 0 / 0.45));
	}
	.panel {
		display: grid;
		grid-template-columns: auto 1fr;
		grid-template-rows: 1fr auto;
		column-gap: 1cqw;
		align-items: center;
		padding: 0.5cqw 1.2cqw;
		border: 0.22cqw solid #d9a441;
		border-radius: 1cqw;
		background: linear-gradient(180deg, rgb(24 16 12 / 0.94), rgb(14 9 6 / 0.94));
		box-shadow: 0 0 0 0.16cqw #5a3b10, 0 0.5cqw 1.2cqw rgb(0 0 0 / 0.4);
	}
	.emblem {
		grid-row: 1 / 3;
		height: 82%;
		width: auto;
	}
	.names {
		min-width: 0;
		text-align: left;
		line-height: 1.05;
	}
	.where {
		margin: 0;
		font: 700 clamp(0.5rem, 1.3cqw, 0.9rem) / 1 var(--font-pixel, var(--font-display));
		color: #ffd27a;
	}
	.who {
		margin: 0;
		font: 700 clamp(0.5rem, 1.45cqw, 1.1rem) / 1.1 var(--font-pixel, var(--font-display));
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}
	.bars {
		grid-column: 1 / 3;
		display: flex;
		gap: 0.4cqw;
		margin: 0.3cqw 0 0;
	}
	.bars span {
		flex: 1;
		height: max(1.3cqw, 6px);
		border-radius: 0.5cqw;
		border: 0.16cqw solid #ffd8a0;
		background: rgb(0 0 0 / 0.55);
		transition: background 300ms;
	}
	.bars span.on {
		background: linear-gradient(180deg, #ff6b5a, #c8102e);
		box-shadow: 0 0 0.8cqw rgb(255 80 60 / 0.6);
	}
	.foe-count {
		grid-column: 1 / 3;
		margin: 0.2cqw 0 0;
		font-weight: 800;
		font-size: clamp(0.55rem, 1.4cqw, 0.95rem);
		color: #ffd8a0;
	}
	.dock {
		display: grid;
		grid-template-columns: repeat(var(--cols), 1fr);
		align-items: center;
		gap: 0.6cqw;
	}
	.dock button {
		position: relative;
		display: grid;
		place-items: center;
		padding: 0;
		border: 0;
		border-radius: 50%;
		background: none;
		cursor: pointer;
		transition: transform 160ms var(--spring, ease);
	}
	.dock img {
		width: 100%;
		height: auto;
		filter: drop-shadow(0 0.3cqw 0.4cqw rgb(0 0 0 / 0.5));
	}
	.dock .key {
		position: absolute;
		bottom: -1.4cqw;
		left: 50%;
		transform: translateX(-50%);
		min-width: 2cqw;
		padding: 0 0.4cqw;
		border-radius: 0.5cqw;
		background: rgb(10 14 28 / 0.9);
		border: 0.15cqw solid #d9a441;
		font: 700 clamp(0.5rem, 1.3cqw, 0.85rem) / 1.3 var(--font-pixel, var(--font-display));
		text-align: center;
	}
	.dock button.on {
		transform: translateY(-0.8cqw) scale(1.12);
	}
	.dock button.on img {
		filter: drop-shadow(0 0 1.2cqw #ffd27a) drop-shadow(0 0 0.4cqw #fff);
	}
	.dock button:focus-visible {
		outline: 0.3cqw solid #fff;
		outline-offset: 0.2cqw;
	}
	.dock.locked img {
		filter: grayscale(1) brightness(0.55);
	}
	.dock button:disabled {
		cursor: default;
	}

	.still .actor img,
	.still .friend {
		animation: none !important;
	}
	@media (max-width: 520px) {
		.where {
			display: none;
		}
	}
</style>
