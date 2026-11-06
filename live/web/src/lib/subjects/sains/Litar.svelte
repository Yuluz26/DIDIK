<!--
	Litar Elektrik: a battery, wires and a bulb on a board, with a gap in the circuit. Put one answer in the
	gap (drag it, or tap it), then close the switch to check. Only a right answer lights the bulb, once the
	answer is shown: the bulb never gives it away before.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import { dragTap } from '$lib/questions/drag';
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
	const lit = $derived(!!right && pick === right);
	const inGap = $derived(choices.find((c) => c.id === pick));

	function put(id: string) {
		if (locked) return;
		chosen = id;
		play('pop');
	}
</script>

<div class="bench">
	<div class="board" class:lit>
		<svg viewBox="0 0 320 170" class="wires" aria-hidden="true">
			<path d="M60 120 V40 H140" />
			<path d="M180 40 H260 V120 H205" />
			<path d="M115 120 H60" />
		</svg>
		<div class="battery" aria-hidden="true"><span>+</span><span>−</span></div>
		<div class="bulb" aria-hidden="true">
			<span class="glass"><span class="filament"></span></span>
			<span class="base"></span>
		</div>
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="gap" class:filled={!!inGap} data-zone="gap">
			{#if inGap}
				<span class="thing">
					{#if inGap.sticker ?? stickerFor(inGap.text)}<Sticker key={inGap.sticker ?? stickerFor(inGap.text) ?? ''} size={30} alt="" />{/if}
					<span>{inGap.text}</span>
					{#if right}<Mark ok={inGap.id === right} />{/if}
				</span>
			{:else}
				<span class="hint">Masukkan bahan</span>
			{/if}
		</div>
		<span class="switch" class:closed={locked} aria-hidden="true"></span>
	</div>
	{#if right && pick !== right}
		<p class="should">Yang menyalakan mentol: <strong>{choices.find((c) => c.id === right)?.text}</strong></p>
	{/if}
	{#if !locked}
		<ul class="tray" aria-label="Bahan untuk diuji">
			{#each choices as c (c.id)}
				<li>
					<button
						type="button"
						class="item"
						class:on={chosen === c.id}
						aria-pressed={chosen === c.id}
						{@attach dragTap({ enabled: () => !locked, home: () => (chosen === c.id ? 'gap' : 'tray'), tap: () => put(c.id), drop: (zone) => zone === 'gap' && put(c.id) })}
					>
						{#if c.sticker ?? stickerFor(c.text)}<Sticker key={c.sticker ?? stickerFor(c.text) ?? ''} size={40} alt="" />{/if}
						<span>{c.text}</span>
					</button>
				</li>
			{/each}
		</ul>
		<Checks tip={chosen ? 'Tutup suis untuk menguji.' : 'Seret atau ketik satu bahan ke dalam litar.'} label="Tutup suis" ready={!!chosen} dirty={!!chosen} onreset={() => (chosen = null)} oncheck={() => p.onanswer?.(chosen)} />
	{/if}
</div>

<style>
	.bench {
		display: grid;
		gap: 0.7rem;
	}
	.board {
		position: relative;
		aspect-ratio: 32 / 17;
		border-radius: var(--r-lg);
		background:
			radial-gradient(circle at 1px 1px, rgb(0 0 0 / 0.12) 1px, transparent 1.5px) 0 0 / 16px 16px,
			linear-gradient(180deg, #2f6b4f, #24533d);
		box-shadow:
			inset 0 0 0 3px #1b3e2d,
			0 8px 18px rgb(20 50 35 / 0.25);
	}
	.wires {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
	}
	.wires path {
		fill: none;
		stroke: #e8a33a;
		stroke-width: 5;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
	.lit .wires path {
		stroke: #ffd36b;
		filter: drop-shadow(0 0 4px #ffd36b);
	}
	.battery {
		position: absolute;
		left: 13%;
		top: 60%;
		display: grid;
		grid-template-columns: 1fr 1fr;
		width: 15%;
		height: 20%;
		border-radius: 6px;
		overflow: hidden;
		box-shadow: 0 3px 6px rgb(0 0 0 / 0.35);
	}
	.battery span {
		display: grid;
		place-items: center;
		color: #fff;
		font: 700 1rem var(--font-display);
	}
	.battery span:first-child {
		background: #d63a2c;
	}
	.battery span:last-child {
		background: #2a2d34;
	}
	.bulb {
		position: absolute;
		left: 50%;
		top: 6%;
		display: grid;
		justify-items: center;
		translate: -50% 0;
	}
	.glass {
		position: relative;
		display: grid;
		place-items: center;
		width: 3.2rem;
		height: 3.2rem;
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, rgb(255 255 255 / 0.9), rgb(220 230 240 / 0.5));
		box-shadow: inset 0 0 0 2px rgb(255 255 255 / 0.6);
		transition:
			background 0.4s,
			box-shadow 0.4s;
	}
	.filament {
		width: 1rem;
		height: 0.8rem;
		border: 2px solid #8b8f99;
		border-bottom: 0;
		border-radius: 50% 50% 0 0;
	}
	.lit .glass {
		background: radial-gradient(circle, #fffbe0, #ffd84d 60%, #ffb000);
		box-shadow: 0 0 40px 16px rgb(255 214 77 / 0.7);
	}
	.lit .filament {
		border-color: #fff;
	}
	.base {
		width: 1.6rem;
		height: 0.9rem;
		border-radius: 0 0 4px 4px;
		background: repeating-linear-gradient(180deg, #b8bec8 0 3px, #868d98 3px 5px);
	}
	.gap {
		position: absolute;
		left: 37%;
		top: 58%;
		display: grid;
		place-items: center;
		width: 28%;
		min-height: 30%;
		border: 3px dashed #ffd36b;
		border-radius: 10px;
		background: rgb(0 0 0 / 0.18);
	}
	.gap.filled {
		border-style: solid;
		background: rgb(255 255 255 / 0.9);
	}
	.gap:global(.zone-hover) {
		background: rgb(255 211 107 / 0.35);
	}
	.hint {
		color: #ffe6ad;
		font-weight: 800;
		font-size: 0.8rem;
		text-align: center;
	}
	.thing {
		position: relative;
		display: grid;
		justify-items: center;
		padding: 0.2rem;
		color: var(--ink);
		font: 700 0.8rem/1.1 var(--font-body);
		text-align: center;
	}
	.switch {
		position: absolute;
		right: 12%;
		top: 67%;
		width: 2.6rem;
		height: 0.5rem;
		border-radius: 3px;
		background: #c9ced6;
		transform-origin: 0 50%;
		rotate: -30deg;
		transition: rotate 0.3s var(--spring, ease-out);
	}
	.switch.closed {
		rotate: 0deg;
	}
	.should {
		padding: 0.5rem 0.8rem;
		border-radius: var(--r-md);
		background: var(--almost-soft, #fff1e6);
		color: var(--on-almost-soft, #8a3b12);
		font-weight: 700;
	}
	.tray {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.item {
		display: grid;
		justify-items: center;
		gap: 0.15rem;
		min-width: 5rem;
		padding: 0.4rem 0.6rem;
		border: 0;
		border-radius: var(--r-md);
		background: #fff;
		color: var(--ink);
		font: 700 0.9rem/1.1 var(--font-body);
		box-shadow:
			0 4px 0 #e2d6c4,
			0 6px 12px rgb(31 45 39 / 0.08);
		cursor: grab;
		touch-action: none;
	}
	.item.on {
		outline: 3px solid #f0a400;
		outline-offset: 2px;
	}
	.item:global(.dragging) {
		z-index: 50;
	}
</style>
