<!--
	Arkib Negara: the statement typed on an old file card on the archivist's desk, and two rubber stamps,
	BENAR and PALSU. Press a stamp onto the card (tap it, or drag it on); it thumps down in ink. Semak sends
	the verdict.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import { dragTap } from '$lib/questions/drag';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	const locked = $derived(isLocked(p));
	let stamped = $state<boolean | null>(null);
	const verdict = $derived<boolean | null>(p.mine !== undefined ? p.mine : p.reveal ? p.reveal.correct : stamped);
	const right = $derived<boolean | null>(p.reveal ? p.reveal.correct : null);
	let thump = $state(0);

	function stamp(value: boolean) {
		if (locked) return;
		stamped = value;
		thump++;
		play('kick');
	}
	const ref = Math.floor(1000 + Math.random() * 8999);
	import { asset } from '../assets';
	// the archive's shelves of files behind the desk
	const SHELVES = asset('hist/archive');
</script>

<div class="desk" style:--shelves={SHELVES ? `url(${SHELVES.src})` : 'none'}>
	<div class="card" data-zone="card">
		<p class="head">ARKIB NEGARA · FAIL {ref}</p>
		<p class="text">{p.question.prompt}</p>
		{#if verdict !== null}
			{#key thump}
				<span class="ink" class:true={verdict} class:false={!verdict}>{verdict ? 'BENAR' : 'PALSU'}</span>
			{/key}
			{#if right !== null}<Mark ok={verdict === right} size={16} />{/if}
		{/if}
	</div>
	{#if right !== null && verdict !== right}
		<p class="should">Sebenarnya: <strong>{right ? 'BENAR' : 'PALSU'}</strong></p>
	{/if}
	{#if !locked}
		<div class="stamps">
			{#each [true, false] as value (value)}
				<button
					type="button"
					class="stamp"
					class:true={value}
					class:false={!value}
					class:on={stamped === value}
					aria-pressed={stamped === value}
					{@attach dragTap({ enabled: () => !locked, tap: () => stamp(value), drop: (zone) => zone === 'card' && stamp(value) })}
				>
					<span class="handle" aria-hidden="true"></span>
					<span class="face">{value ? 'BENAR' : 'PALSU'}</span>
				</button>
			{/each}
		</div>
	{/if}
</div>
{#if !locked}
	<Checks tip={stamped === null ? 'Cop dokumen ini: BENAR atau PALSU?' : 'Dokumen sudah dicop. Semak bila pasti.'} ready={stamped !== null} dirty={stamped !== null} onreset={() => (stamped = null)} oncheck={() => p.onanswer?.(stamped)} />
{/if}

<style>
	.desk {
		background-image: linear-gradient(rgb(40 30 20 / 0.55), rgb(60 40 20 / 0.75)), var(--shelves) !important;
		background-size: cover !important;
		background-position: center !important;
	}
	.desk {
		display: grid;
		gap: 0.8rem;
		justify-items: center;
		padding: 1rem 0.7rem;
		border-radius: var(--r-lg);
		background:
			repeating-linear-gradient(92deg, rgb(255 255 255 / 0.04) 0 4px, transparent 4px 16px),
			linear-gradient(180deg, #6b4423, #4f3018);
		box-shadow: inset 0 0 0 3px #3a2210;
	}
	.card {
		position: relative;
		width: min(100%, 26rem);
		min-height: 9rem;
		padding: 0.8rem 1rem 1.2rem;
		border-radius: 3px;
		background:
			repeating-linear-gradient(180deg, transparent 0 25px, rgb(90 140 200 / 0.2) 25px 26px),
			#fbf6e8;
		box-shadow: 0 8px 16px rgb(0 0 0 / 0.35);
		rotate: -1deg;
	}
	.card:global(.zone-hover) {
		outline: 3px dashed #e0a21a;
	}
	.head {
		color: #8a2a2a;
		font: 700 0.72rem 'Courier New', monospace;
		letter-spacing: 0.08em;
	}
	.text {
		margin-top: 0.4rem;
		color: #2a2014;
		font: 700 1.05rem/1.5 'Courier New', 'Courier', monospace;
	}
	.ink {
		position: absolute;
		right: 0.8rem;
		bottom: 0.6rem;
		padding: 0.15rem 0.6rem;
		border: 4px double currentColor;
		border-radius: 6px;
		font: 700 1.6rem/1 var(--font-display);
		letter-spacing: 0.08em;
		rotate: -12deg;
		opacity: 0.85;
		mix-blend-mode: multiply;
		animation: thump 0.35s cubic-bezier(0.2, 1.8, 0.4, 1);
	}
	.ink.true {
		color: #1d7a45;
	}
	.ink.false {
		color: #b42828;
	}
	.should {
		padding: 0.4rem 0.8rem;
		border-radius: var(--r-md);
		background: #fff1e6;
		color: #8a3b12;
		font-weight: 700;
	}
	.stamps {
		display: flex;
		gap: 1.4rem;
	}
	.stamp {
		display: grid;
		justify-items: center;
		padding: 0;
		border: 0;
		background: transparent;
		cursor: grab;
		touch-action: none;
		transition: transform var(--t-state) var(--spring);
	}
	.stamp:hover,
	.stamp.on {
		transform: translateY(-4px);
	}
	.stamp:global(.dragging) {
		z-index: 50;
	}
	.handle {
		width: 1.4rem;
		height: 2.2rem;
		border-radius: 0.7rem 0.7rem 0.2rem 0.2rem;
		background: linear-gradient(90deg, #5a3a1a, #9a6a3a, #5a3a1a);
	}
	.face {
		padding: 0.35rem 0.9rem;
		border-radius: 6px;
		color: #fff;
		font: 700 1rem var(--font-display);
		letter-spacing: 0.06em;
		box-shadow: 0 4px 0 rgb(0 0 0 / 0.3);
	}
	.true .face {
		background: #1d7a45;
	}
	.false .face {
		background: #b42828;
	}
	@keyframes thump {
		from {
			transform: scale(2.2);
			opacity: 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.ink {
			animation: none;
		}
	}
</style>
