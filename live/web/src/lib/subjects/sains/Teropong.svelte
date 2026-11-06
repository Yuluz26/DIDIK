<!--
	Teropong Angkasa: a night sky with the answers hidden among the stars as faint glows. Drag the
	telescope's lens across the sky (or tap anywhere) to bring what is under it into view; tap an answer
	in the lens to lock on to it. Semak sends the one locked on.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Sticker from '$ui/Sticker.svelte';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked, stickerFor } from '../kit.svelte';

	let p: GameProps = $props();

	const choices = $derived(p.question.choices ?? []);
	const locked = $derived(isLocked(p));
	let chosen = $state<string | null>(null);
	const pick = $derived<string | null>(p.mine !== undefined ? p.mine : p.reveal ? p.reveal.correct[0] : chosen);
	const right = $derived<string | null>(p.reveal ? p.reveal.correct[0] : null);

	// where each answer hangs in the sky: spread out, the same every time for the same number of answers
	const SPOTS = [
		[22, 30],
		[72, 24],
		[48, 58],
		[18, 74],
		[80, 70],
		[50, 18]
	];
	let lens = $state({ x: 88, y: 42 });
	let sky: HTMLDivElement;
	const R = 17; // the lens's radius, in percent of the sky's width

	function aim(event: PointerEvent) {
		if (locked) return;
		const box = sky.getBoundingClientRect();
		lens = { x: ((event.clientX - box.left) / box.width) * 100, y: ((event.clientY - box.top) / box.height) * 100 };
	}
	let dragging = false;
	const near = (x: number, y: number) => Math.hypot(x - lens.x, (y - lens.y) * 0.75) < R;

	function choose(id: string, x: number, y: number) {
		if (locked) return;
		chosen = id;
		lens = { x, y };
		play('pop');
	}
	const LOOK = ['#ffd27a', '#9fd3ff', '#ffb0d0', '#c3ffb0', '#e1c4ff', '#ffe9a8'];
</script>

<div class="obs">
	<div
		class="sky"
		bind:this={sky}
		role="application"
		aria-label="Langit malam. Gerakkan kanta teropong untuk mencari jawapan."
		onpointerdown={(e) => {
			dragging = true;
			aim(e);
		}}
		onpointermove={(e) => dragging && aim(e)}
		onpointerup={() => (dragging = false)}
		onpointerleave={() => (dragging = false)}
	>
		<span class="stars" aria-hidden="true"></span>
		<span class="moon" aria-hidden="true"><Sticker key="sabit" size={40} alt="" /></span>
		{#each choices as c, i (c.id)}
			{@const [x, y] = SPOTS[i % SPOTS.length]}
			{@const seen = locked || near(x, y) || pick === c.id}
			{@const ok = right ? c.id === right : null}
			<button
				type="button"
				class="body"
				class:seen
				class:on={pick === c.id}
				class:ok={ok === true && (pick === c.id || !p.mine)}
				class:off={ok === false && pick === c.id}
				style:left="{x}%"
				style:top="{y}%"
				style:--glow={LOOK[i % LOOK.length]}
				disabled={locked}
				onpointerdown={(e) => e.stopPropagation()}
				onclick={() => choose(c.id, x, y)}
				aria-label={c.text}
			>
				<span class="orb">{#if c.sticker ?? stickerFor(c.text)}<Sticker key={c.sticker ?? stickerFor(c.text) ?? ''} size={34} alt="" />{/if}</span>
				<span class="name">{c.text}</span>
				{#if right && (pick === c.id || c.id === right)}<Mark ok={c.id === right} />{/if}
			</button>
		{/each}
		{#if !locked}
			<span class="lens" style:left="{lens.x}%" style:top="{lens.y}%" style:--r="{R * 2}%" aria-hidden="true"><i></i></span>
		{/if}
	</div>
	<div class="scope" aria-hidden="true"><Sticker key="teropong" size={58} alt="" /><span>Teropong DIDIK · 120×</span></div>
	{#if !locked}
		<Checks tip={chosen ? 'Sasaran dikunci. Semak bila pasti.' : 'Seret kanta teropong untuk meninjau langit, kemudian ketik jawapan.'} ready={!!chosen} dirty={!!chosen} onreset={() => (chosen = null)} oncheck={() => p.onanswer?.(chosen)} />
	{/if}
</div>

<style>
	.obs {
		display: grid;
		gap: 0.6rem;
	}
	.sky {
		position: relative;
		aspect-ratio: 4 / 3;
		overflow: hidden;
		border-radius: var(--r-lg);
		background: radial-gradient(circle at 70% 110%, #3a2a6b, #0b0a1f 60%, #05050f);
		box-shadow: inset 0 0 0 3px #1c1838;
		touch-action: none;
		cursor: crosshair;
	}
	.stars {
		position: absolute;
		inset: 0;
		background:
			radial-gradient(1px 1px at 10% 20%, #fff, transparent),
			radial-gradient(1px 1px at 30% 70%, #fff, transparent),
			radial-gradient(1.5px 1.5px at 60% 15%, #fff, transparent),
			radial-gradient(1px 1px at 85% 40%, #dfe8ff, transparent),
			radial-gradient(1px 1px at 45% 85%, #fff, transparent),
			radial-gradient(1px 1px at 92% 88%, #fff, transparent),
			radial-gradient(1.5px 1.5px at 5% 55%, #fff, transparent),
			radial-gradient(1px 1px at 70% 60%, #fff, transparent);
		animation: twinkle 3s ease-in-out infinite;
	}
	.moon {
		position: absolute;
		right: 6%;
		top: 6%;
		opacity: 0.8;
	}
	.body {
		position: absolute;
		z-index: 1;
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		translate: -50% -50%;
		padding: 0;
		border: 0;
		background: transparent;
		color: #fff;
		cursor: pointer;
	}
	.orb {
		display: grid;
		place-items: center;
		width: 2.2rem;
		height: 2.2rem;
		border-radius: 50%;
		background: radial-gradient(circle, var(--glow), transparent 70%);
		opacity: 0.45;
		filter: blur(3px);
		transition:
			opacity 0.25s,
			filter 0.25s,
			transform 0.25s;
	}
	.orb :global(img) {
		opacity: 0;
		transition: opacity 0.25s;
	}
	.name {
		max-width: 7rem;
		padding: 0.1rem 0.45rem;
		border-radius: 6px;
		background: rgb(0 0 0 / 0.55);
		font: 700 0.85rem/1.15 var(--font-body);
		text-align: center;
		opacity: 0;
		transition: opacity 0.25s;
	}
	.seen .orb {
		opacity: 1;
		filter: none;
		transform: scale(1.25);
	}
	.seen .orb :global(img),
	.seen .name {
		opacity: 1;
	}
	.on .orb {
		box-shadow:
			0 0 0 3px #ffd23f,
			0 0 18px #ffd23f;
	}
	.on .name {
		background: #ffd23f;
		color: #2a1f00;
	}
	.ok .name {
		background: var(--good);
		color: #fff;
	}
	.off .name {
		background: var(--almost);
		color: #fff;
	}
	.lens {
		position: absolute;
		width: var(--r);
		aspect-ratio: 1;
		translate: -50% -50%;
		border-radius: 50%;
		box-shadow:
			0 0 0 3px rgb(200 220 255 / 0.8),
			0 0 0 9999px rgb(0 0 10 / 0.35);
		pointer-events: none;
		transition:
			left 0.12s linear,
			top 0.12s linear;
	}
	.lens i {
		position: absolute;
		inset: 0;
		background:
			linear-gradient(transparent calc(50% - 1px), rgb(200 220 255 / 0.4) calc(50% - 1px) calc(50% + 1px), transparent calc(50% + 1px)),
			linear-gradient(90deg, transparent calc(50% - 1px), rgb(200 220 255 / 0.4) calc(50% - 1px) calc(50% + 1px), transparent calc(50% + 1px));
		border-radius: 50%;
	}
	.scope {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		color: var(--ink-2);
		font: 700 0.85rem var(--font-display);
	}
	@keyframes twinkle {
		50% {
			opacity: 0.6;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.stars {
			animation: none;
		}
	}
</style>
