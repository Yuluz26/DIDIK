<!--
	Teropong Angkasa: an observatory under a real night sky (a panorama of the Milky Way). Each answer is a
	point of light somewhere in it; they all look alike until the telescope finds them. Drag the eyepiece
	across the sky (or tap a point of light, or use the arrow keys): the eyepiece shows that part of the sky
	magnified, and what is there comes into focus as it nears the cross-hairs, as its real picture (a
	planet from a spacecraft, a galaxy from Hubble) with its name. "Kunci sasaran" locks on to what is in
	focus; Semak sends it.

	Every answer is found the same way and looks the way it really does, so nothing shows which is right
	before the answer is in. The server gives this game only to questions whose answers are all things in
	the sky (lexicon "space"); words it does not know appear as an unnamed point of light, never as a
	planet they are not.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Checks from '../Checks.svelte';
	import GameImage from '../GameImage.svelte';
	import Mark from '../Mark.svelte';
	import { asset, find, type Entry } from '../assets';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	interface Body extends Entry {
		kind: string;
		wide?: boolean;
	}

	const choices = $derived(p.question.choices ?? []);
	const locked = $derived(isLocked(p));
	let chosen = $state<string | null>(null);
	const pick = $derived<string | null>(p.mine !== undefined ? p.mine : p.reveal ? p.reveal.correct[0] : chosen);
	const right = $derived<string | null>(p.reveal ? p.reveal.correct[0] : null);

	// Where each answer is in the sky (percent of its width and height), by its place in the list. The
	// server shuffles the list, so a place says nothing about an answer.
	const SPOTS = [
		[24, 28],
		[76, 26],
		[50, 49],
		[25, 65],
		[77, 61],
		[50, 24]
	];
	const ASPECT = 0.86; // the sky's height over its width
	const R = 20; // the eyepiece's radius, in percent of the sky's width
	const ZOOM = 2.3;
	const targets = $derived(choices.map((c, i) => ({ c, x: SPOTS[i % SPOTS.length][0], y: SPOTS[i % SPOTS.length][1], body: find<Body>('space', c.text) })));

	// The telescope starts pointed low, at empty sky above the horizon: nothing is in view.
	let aim = $state({ x: 50, y: 78 });
	let slewing = $state(false);
	let sky: HTMLDivElement;

	/** How far a target is from the cross-hairs, in eyepiece radii. */
	const away = (t: { x: number; y: number }) => Math.hypot(t.x - aim.x, (t.y - aim.y) * ASPECT) / R;
	const focused = $derived.by(() => {
		let best: (typeof targets)[number] | null = null;
		let least = 0.46;
		for (const t of targets) {
			const d = away(t);
			if (d < least) [best, least] = [t, d];
		}
		return best;
	});
	const chosenTarget = $derived(targets.find((t) => t.c.id === pick) ?? null);
	// the tube leans towards where it is pointed
	const lean = $derived((Math.atan2(aim.x - 50, (104 - aim.y) * ASPECT) * 180) / Math.PI);

	let last: string | null = null;
	$effect(() => {
		const now = focused?.c.id ?? null;
		if (now && now !== last && !locked) play('tick');
		last = now;
	});

	function point(x: number, y: number) {
		aim = { x: Math.max(4, Math.min(96, x)), y: Math.max(5, Math.min(84, y)) };
	}
	function follow(event: PointerEvent) {
		const box = sky.getBoundingClientRect();
		// under a finger the eyepiece would be hidden, so it rides a little above the touch
		const lift = event.pointerType === 'touch' ? 14 : 0;
		point(((event.clientX - box.left) / box.width) * 100, ((event.clientY - box.top) / box.height) * 100 - lift);
	}
	let dragging = false;
	function down(event: PointerEvent) {
		if (locked) return;
		dragging = true;
		slewing = false;
		if (chosen) chosen = null; // moving off lets go of the target
		try {
			sky.setPointerCapture(event.pointerId);
		} catch {
			// a pointer the browser no longer tracks: the moves it sends are still followed
		}
		follow(event);
	}
	function slewTo(t: (typeof targets)[number]) {
		if (locked) return;
		slewing = true;
		point(t.x, t.y);
		chosen = t.c.id;
		play('pop');
	}
	function lock() {
		if (locked || !focused) return;
		slewing = true;
		point(focused.x, focused.y);
		chosen = focused.c.id;
		play('pop');
	}
	function keys(event: KeyboardEvent) {
		if (locked) return;
		const step = { ArrowLeft: [-3, 0], ArrowRight: [3, 0], ArrowUp: [0, -3], ArrowDown: [0, 3] }[event.key];
		if (step) {
			event.preventDefault();
			slewing = false;
			if (chosen) chosen = null;
			point(aim.x + step[0], aim.y + step[1]);
		} else if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			lock();
		}
	}
	const SKY = asset('space/milkyway');
</script>

<div class="obs">
	<!-- svelte-ignore a11y_no_noninteractive_tabindex, a11y_no_noninteractive_element_interactions -->
	<div
		class="sky"
		class:locked
		bind:this={sky}
		role="application"
		tabindex={locked ? -1 : 0}
		aria-label="Langit malam. Seret untuk menghalakan teropong, atau guna kekunci anak panah. Enter mengunci sasaran dalam fokus."
		style:--sky={SKY ? `url(${SKY.src})` : 'none'}
		style:--ax={aim.x}
		style:--ay={aim.y}
		style:--z={ZOOM}
		style:--r="{R}cqw"
		onpointerdown={down}
		onpointermove={(e) => dragging && !locked && follow(e)}
		onpointerup={() => (dragging = false)}
		onpointercancel={() => (dragging = false)}
		onkeydown={keys}
	>
		{#if locked}
			<!-- the answer is in: every target shown where it was, as what it is -->
			{#each targets as t (t.c.id)}
				{@const ok = right ? t.c.id === right : null}
				<span
					class="found"
					class:wide={t.body?.wide}
					class:mine={pick === t.c.id}
					class:ok={ok === true && (pick === t.c.id || p.mine === undefined)}
					class:off={ok === false && pick === t.c.id}
					style:left="{t.x}%"
					style:top="{t.y}%"
				>
					<span class="pic">
						<GameImage name={t.body?.key} eager>
							{#snippet fallback()}<i class="point" aria-hidden="true"></i>{/snippet}
						</GameImage>
						{#if right && (pick === t.c.id || t.c.id === right)}<Mark ok={t.c.id === right} />{/if}
					</span>
					<span class="name">{t.c.text}</span>
				</span>
			{/each}
		{:else}
			{#each targets as t, i (t.c.id)}
				<button
					type="button"
					class="glint"
					class:on={chosen === t.c.id}
					style:left="{t.x}%"
					style:top="{t.y}%"
					style:--d="{(i * 0.37) % 1.6}s"
					onpointerdown={(e) => e.stopPropagation()}
					onclick={() => slewTo(t)}
					aria-label="{t.c.text}: halakan teropong ke sini"
					aria-pressed={chosen === t.c.id}
				><i aria-hidden="true"></i></button>
			{/each}

			<div class="lens" class:slewing class:held={!!chosen} style:left="{aim.x}%" style:top="{aim.y}%" aria-hidden="true">
				<span class="deep"></span>
				{#each targets as t (t.c.id)}
					{@const d = away(t)}
					{#if d < 1.5}
						{@const sharp = Math.max(0, Math.min(1, 1 - (d - 0.12) / 0.75))}
						<span
							class="obj"
							class:wide={t.body?.wide}
							style:left="{50 + ((t.x - aim.x) * ZOOM * 100) / (2 * R)}%"
							style:top="{50 + ((t.y - aim.y) * ASPECT * ZOOM * 100) / (2 * R)}%"
							style:filter="blur({((1 - sharp) * 5).toFixed(1)}px)"
							style:opacity={0.4 + sharp * 0.6}
						>
							<GameImage name={t.body?.key} eager>
								{#snippet fallback()}<i class="point"></i>{/snippet}
							</GameImage>
						</span>
					{/if}
				{/each}
				<span class="glass"></span>
				<span class="hairs"></span>
			</div>
		{/if}

		<svg class="ground" viewBox="0 0 400 60" preserveAspectRatio="none" aria-hidden="true">
			<path d="M0 60 V38 C40 30 70 34 104 30 C150 24 176 34 214 28 C256 22 300 32 332 26 C360 21 384 27 400 24 V60 Z" />
		</svg>
		<svg class="scope" viewBox="0 0 120 150" aria-hidden="true">
			<defs>
				<linearGradient id="tp-tube" x1="0" x2="1">
					<stop offset="0" stop-color="#8f96a6" /><stop offset="0.28" stop-color="#f6f8fb" /><stop offset="0.62" stop-color="#c9cfdb" /><stop offset="1" stop-color="#5d6474" />
				</linearGradient>
				<linearGradient id="tp-brass" x1="0" x2="1">
					<stop offset="0" stop-color="#7a5a18" /><stop offset="0.35" stop-color="#f3d27a" /><stop offset="0.7" stop-color="#b98a2c" /><stop offset="1" stop-color="#6a4c12" />
				</linearGradient>
				<linearGradient id="tp-dark" x1="0" x2="1">
					<stop offset="0" stop-color="#11151f" /><stop offset="0.4" stop-color="#3b4458" /><stop offset="1" stop-color="#0b0e16" />
				</linearGradient>
			</defs>
			<!-- tripod -->
			<path d="M60 112 L34 150 M60 112 L86 150 M60 112 V150" stroke="#1a1e2b" stroke-width="5" stroke-linecap="round" fill="none" />
			<path d="M60 112 L34 150 M60 112 L86 150" stroke="#4a5266" stroke-width="1.6" stroke-linecap="round" fill="none" />
			<g class="tube" style:rotate="{lean}deg">
				<rect x="49" y="18" width="22" height="88" rx="3" fill="url(#tp-tube)" />
				<rect x="46" y="6" width="28" height="20" rx="3" fill="url(#tp-dark)" />
				<ellipse cx="60" cy="7" rx="13" ry="3.2" fill="#0a0d18" stroke="#6b7690" stroke-width="0.8" />
				<rect x="47.5" y="46" width="25" height="5" rx="1.5" fill="url(#tp-brass)" />
				<rect x="47.5" y="86" width="25" height="5" rx="1.5" fill="url(#tp-brass)" />
				<rect x="73" y="52" width="6" height="30" rx="2" fill="url(#tp-dark)" />
				<rect x="54" y="104" width="12" height="12" rx="2" fill="url(#tp-brass)" />
				<rect x="56" y="114" width="8" height="8" rx="1.5" fill="url(#tp-dark)" />
			</g>
			<circle cx="60" cy="112" r="6.5" fill="url(#tp-brass)" stroke="#3c2c08" stroke-width="1" />
		</svg>
	</div>

	{#if !locked}
		<div class="hud">
			<p class="read" aria-live="polite">
				{#if chosenTarget}
					<span>Sasaran dikunci</span><strong>{chosenTarget.c.text}</strong>
				{:else if focused}
					<span>Dalam fokus{focused.body ? ` · ${focused.body.kind}` : ''}</span><strong>{focused.c.text}</strong>
				{:else}
					<span>Kanta mata</span><strong class="none">Tiada apa-apa dalam fokus</strong>
				{/if}
			</p>
			<button type="button" class="btn lock" disabled={!focused || chosen === focused.c.id} onclick={lock}>Kunci sasaran</button>
		</div>
		<Checks
			tip={chosen ? 'Semak bila pasti, atau seret teropong untuk mencari yang lain.' : focused ? 'Itu dia! Kunci sasaran jika ini jawapannya.' : 'Seret teropong merentasi langit, atau ketik satu titik cahaya.'}
			ready={!!chosen}
			dirty={!!chosen}
			onreset={() => ((chosen = null), (slewing = true), point(50, 78))}
			oncheck={() => p.onanswer?.(chosen)}
		/>
	{/if}
	<p class="scale">Gambar sebenar dari kapal angkasa dan teleskop. Saiz dan kedudukan di langit bukan mengikut skala.</p>
</div>

<style>
	.obs {
		display: grid;
		gap: 0.7rem;
	}
	.sky {
		position: relative;
		container-type: size;
		width: 100%;
		aspect-ratio: 100 / 86;
		overflow: hidden;
		border-radius: var(--r-lg);
		background:
			linear-gradient(180deg, rgb(4 6 18 / 0.55), rgb(4 6 18 / 0.15) 45%, rgb(10 14 34 / 0.5)),
			var(--sky) 50% 50% / auto 100% no-repeat,
			#05070f;
		box-shadow:
			inset 0 0 0 3px #1a2140,
			0 10px 26px rgb(8 12 40 / 0.35);
		touch-action: none;
		cursor: grab;
		user-select: none;
	}
	.sky.locked {
		cursor: default;
		touch-action: auto;
	}
	.sky:focus-visible {
		outline: 3px solid var(--sky-blue, #7cc4ff);
		outline-offset: 3px;
	}

	/* a point of light: every answer looks like this until the telescope finds it */
	.glint {
		position: absolute;
		display: grid;
		place-items: center;
		width: 2.9rem;
		height: 2.9rem;
		padding: 0;
		border: 0;
		border-radius: 50%;
		background: transparent;
		translate: -50% -50%;
		cursor: pointer;
	}
	.glint i {
		width: 0.42rem;
		height: 0.42rem;
		border-radius: 50%;
		background: #fff;
		box-shadow:
			0 0 6px 2px rgb(255 255 255 / 0.9),
			0 0 18px 6px rgb(160 200 255 / 0.55);
		animation: twinkle 2.4s ease-in-out infinite;
		animation-delay: var(--d);
	}
	.glint.on i {
		box-shadow:
			0 0 6px 2px #fff,
			0 0 0 5px rgb(255 210 63 / 0.55),
			0 0 22px 8px rgb(255 210 63 / 0.6);
	}
	.glint:focus-visible {
		outline: 2px solid #ffd23f;
	}
	@keyframes twinkle {
		50% {
			opacity: 0.45;
			transform: scale(0.75);
		}
	}

	/* the eyepiece: the same sky, magnified, with what is there coming into focus */
	.lens {
		position: absolute;
		width: calc(var(--r) * 2);
		aspect-ratio: 1;
		translate: -50% -50%;
		overflow: hidden;
		border-radius: 50%;
		background: #03040c;
		box-shadow:
			0 0 0 3px #0b0e18,
			0 0 0 6px #6c7488,
			0 0 0 8px #1b2030,
			0 10px 26px rgb(0 0 0 / 0.6);
		pointer-events: none;
	}
	.lens.slewing {
		transition:
			left 0.55s cubic-bezier(0.3, 0.9, 0.3, 1),
			top 0.55s cubic-bezier(0.3, 0.9, 0.3, 1);
	}
	.lens.held {
		box-shadow:
			0 0 0 3px #0b0e18,
			0 0 0 6px #ffd23f,
			0 0 0 8px #7a5a10,
			0 0 26px rgb(255 210 63 / 0.55);
	}
	.deep {
		position: absolute;
		inset: 0;
		background-image: var(--sky);
		background-repeat: no-repeat;
		background-size: calc(200cqh * var(--z)) calc(100cqh * var(--z));
		background-position:
			calc(var(--r) - var(--z) * ((200cqh - 100cqw) / 2 + var(--ax) * 1cqw))
			calc(var(--r) - var(--z) * var(--ay) * 1cqh);
		filter: brightness(1.25) contrast(1.08);
	}
	.obj {
		position: absolute;
		width: 64%;
		translate: -50% -50%;
		will-change: filter, opacity;
	}
	.obj.wide {
		width: 96%;
	}
	.obj :global(img) {
		width: 100%;
		filter: drop-shadow(0 0 10px rgb(120 160 255 / 0.25));
	}
	/* something the lexicon does not know: an unnamed star, never a planet it is not */
	.point {
		display: block;
		width: 22%;
		aspect-ratio: 1;
		margin: 39%;
		border-radius: 50%;
		background: #fff;
		box-shadow:
			0 0 10px 4px #fff,
			0 0 30px 12px rgb(170 200 255 / 0.7);
	}
	.glass {
		position: absolute;
		inset: 0;
		border-radius: 50%;
		background:
			radial-gradient(circle at 32% 26%, rgb(255 255 255 / 0.16), transparent 30%),
			radial-gradient(circle, transparent 58%, rgb(0 0 0 / 0.55) 92%, #000 100%);
		box-shadow: inset 0 0 0 2px rgb(120 170 255 / 0.25);
	}
	.hairs {
		position: absolute;
		inset: 0;
		background:
			linear-gradient(90deg, transparent calc(50% - 0.5px), rgb(255 255 255 / 0.35) calc(50% - 0.5px) calc(50% + 0.5px), transparent calc(50% + 0.5px)),
			linear-gradient(0deg, transparent calc(50% - 0.5px), rgb(255 255 255 / 0.35) calc(50% - 0.5px) calc(50% + 0.5px), transparent calc(50% + 0.5px));
		mask: radial-gradient(circle, transparent 0 13%, #000 14% 46%, transparent 47%);
	}

	/* the observatory's own ground and instrument */
	.ground {
		position: absolute;
		left: 0;
		bottom: 0;
		width: 100%;
		height: 13%;
		fill: #04060d;
		pointer-events: none;
	}
	.scope {
		position: absolute;
		left: 50%;
		bottom: -1%;
		width: 24%;
		translate: -50% 0;
		overflow: visible;
		filter: drop-shadow(0 4px 8px rgb(0 0 0 / 0.6));
		pointer-events: none;
	}
	.tube {
		transform-origin: 60px 112px;
		transform-box: view-box;
		transition: rotate 0.35s ease-out;
	}

	/* once answered: each target as what it is */
	.found {
		position: absolute;
		display: grid;
		justify-items: center;
		gap: 0.15rem;
		width: 21cqw;
		translate: -50% -42%;
	}
	.found.wide {
		width: 30cqw;
	}
	.pic {
		position: relative;
		display: grid;
		place-items: center;
		width: 100%;
		border-radius: 50%;
	}
	.found :global(img) {
		width: 100%;
	}
	.found:not(.wide) .pic {
		aspect-ratio: 1;
	}
	.found.mine .pic {
		outline: 3px solid #ffd23f;
		outline-offset: 3px;
	}
	.found.ok .pic {
		outline: 3px solid var(--good);
		outline-offset: 3px;
		box-shadow: 0 0 22px rgb(60 220 140 / 0.6);
	}
	.found.off .pic {
		outline: 3px solid var(--almost);
		outline-offset: 3px;
	}
	.pic :global(.mark) {
		position: absolute;
		top: -0.3rem;
		right: -0.3rem;
	}
	.name {
		max-width: 100%;
		padding: 0.1rem 0.45rem;
		border-radius: 999px;
		background: rgb(5 8 20 / 0.82);
		color: #fff;
		font: 700 0.78rem/1.25 var(--font-body);
		text-align: center;
		overflow-wrap: anywhere;
	}
	.found.ok .name {
		background: var(--good);
	}
	.found.off .name {
		background: var(--almost);
	}

	/* the read-out under the sky */
	.hud {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		padding: 0.5rem 0.6rem 0.5rem 0.9rem;
		border-radius: var(--r-md);
		background: linear-gradient(180deg, #1b2238, #10162a);
		box-shadow: inset 0 0 0 2px #2b3558;
		color: #dfe8ff;
	}
	.read {
		display: grid;
		flex: 1;
		min-width: 0;
		line-height: 1.2;
	}
	.read span {
		color: #8fa3d6;
		font: 700 0.68rem var(--font-display);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}
	.read strong {
		font: 600 1.05rem var(--font-display);
		overflow-wrap: anywhere;
	}
	.read .none {
		color: #9aa6c4;
		font-size: 0.92rem;
		font-weight: 500;
	}
	.lock {
		flex: none;
		min-height: 2.75rem;
		--edge: #8a6412;
		background: linear-gradient(180deg, #ffd96a, #f0b429);
		color: #2c1d00;
	}
	.lock:disabled {
		opacity: 0.45;
	}
	.scale {
		color: var(--ink-3);
		font-size: 0.74rem;
		line-height: 1.3;
		text-align: center;
	}
	@media (prefers-reduced-motion: reduce) {
		.glint i {
			animation: none;
		}
		.lens.slewing,
		.tube {
			transition: none;
		}
	}
</style>
