<!--
	Mesin Masa: a brass time machine with four number wheels (a year, or any number up to 9999). Roll each
	wheel up or down (tap its arrows, or swipe on it); a vortex swirls behind. Pull the lever (Semak) to
	travel to that number.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	const WHEELS = 4;
	const locked = $derived(isLocked(p));
	let digits = $state<number[]>(Array(WHEELS).fill(0));
	let touched = $state(false);
	const asNumber = (ds: number[]) => Number(ds.join(''));
	const toDigits = (n: number) => String(Math.max(0, Math.round(n))).padStart(WHEELS, '0').slice(-WHEELS).split('').map(Number);
	const shown = $derived<number[]>(p.mine !== undefined ? toDigits(Number(p.mine)) : p.reveal ? toDigits(Number(p.reveal.correct)) : digits);
	const right = $derived<number | null>(p.reveal ? Number(p.reveal.correct) : null);
	const ok = $derived(right !== null ? Math.abs(asNumber(shown) - right) <= (p.reveal?.tolerance ?? 0) : null);
	const unit = $derived(p.question.unit ?? '');

	function roll(i: number, dir: number) {
		if (locked) return;
		const next = [...digits];
		next[i] = (next[i] + dir + 10) % 10;
		digits = next;
		touched = true;
		play('tick');
	}
	let swipe: { i: number; y: number } | null = null;
</script>

<div class="machine" class:go={ok === true}>
	<span class="vortex" aria-hidden="true"></span>
	<div class="panel">
		<p class="plate">MESIN MASA · DESTINASI</p>
		<div class="wheels">
			{#each shown as d, i (i)}
				<div
					class="wheel"
					role="spinbutton"
					tabindex={locked ? -1 : 0}
					aria-label="Digit {i + 1}"
					aria-valuenow={d}
					aria-valuemin={0}
					aria-valuemax={9}
					onpointerdown={(e) => (swipe = { i, y: e.clientY })}
					onpointerup={(e) => {
						if (swipe && Math.abs(e.clientY - swipe.y) > 14) roll(i, e.clientY < swipe.y ? 1 : -1);
						swipe = null;
					}}
					onkeydown={(e) => (e.key === 'ArrowUp' ? roll(i, 1) : e.key === 'ArrowDown' ? roll(i, -1) : null)}
				>
					{#if !locked}<button type="button" class="arrow" onclick={() => roll(i, 1)} aria-label="Naik"><Icon name="up" size={16} /></button>{/if}
					<span class="drum">
						<i class="ghost">{(d + 9) % 10}</i>
						{#key d}<b>{d}</b>{/key}
						<i class="ghost">{(d + 1) % 10}</i>
					</span>
					{#if !locked}<button type="button" class="arrow down" onclick={() => roll(i, -1)} aria-label="Turun"><Icon name="up" size={16} /></button>{/if}
				</div>
			{/each}
			{#if unit}<span class="unit">{unit}</span>{/if}
		</div>
		{#if ok !== null}<span class="mark"><Mark {ok} size={16} /></span>{/if}
	</div>
	{#if ok === false && right !== null}<p class="should">Destinasi yang betul: <strong>{right} {unit}</strong></p>{/if}
</div>
{#if !locked}
	<Checks tip="Putar roda nombor, kemudian tarik tuas." label="Tarik tuas" ready={touched} dirty={touched} onreset={() => ((digits = Array(WHEELS).fill(0)), (touched = false))} oncheck={() => p.onanswer?.(asNumber(digits))} />
{/if}

<style>
	.machine {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.6rem;
		padding: 1.4rem 0.6rem;
		overflow: hidden;
		border-radius: var(--r-lg);
		background: #140f2b;
		box-shadow: inset 0 0 0 3px #2b2150;
	}
	.vortex {
		position: absolute;
		inset: -40%;
		background: repeating-conic-gradient(from 0deg, #3a2a7a 0 12deg, #1b1240 12deg 24deg, #5b3fb0 24deg 30deg, #1b1240 30deg 42deg);
		opacity: 0.55;
		animation: swirl 14s linear infinite;
		mask-image: radial-gradient(circle, #000 20%, transparent 70%);
	}
	.go .vortex {
		animation-duration: 1.2s;
		opacity: 0.9;
	}
	.panel {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.6rem;
		padding: 0.8rem 0.9rem;
		border-radius: 14px;
		background: linear-gradient(180deg, #e9c46a, #b8892c);
		box-shadow:
			inset 0 0 0 3px #7a5414,
			0 10px 24px rgb(0 0 0 / 0.5);
	}
	.plate {
		padding: 0.15rem 0.6rem;
		border-radius: 4px;
		background: #2b1a0a;
		color: #f6dc8c;
		font: 700 0.72rem 'Courier New', monospace;
		letter-spacing: 0.12em;
	}
	.wheels {
		display: flex;
		align-items: center;
		gap: 0.35rem;
	}
	.wheel {
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		touch-action: none;
	}
	.wheel:focus-visible {
		outline: 3px solid #fff;
		outline-offset: 3px;
		border-radius: 8px;
	}
	.drum {
		display: grid;
		justify-items: center;
		width: 3.1rem;
		height: 5.2rem;
		overflow: hidden;
		border-radius: 8px;
		background: linear-gradient(180deg, #2a2a30, #f5f1e6 30%, #fffdf6 50%, #f5f1e6 70%, #2a2a30);
		box-shadow: inset 0 0 0 2px #4a3a1a;
	}
	.drum b {
		color: #1b1206;
		font: 700 2.4rem/1.6rem 'Courier New', monospace;
		margin-block: 0.3rem;
		animation: tumble 0.2s ease-out;
	}
	.ghost {
		color: rgb(30 20 6 / 0.35);
		font: 700 1.2rem/1.6rem 'Courier New', monospace;
		font-style: normal;
	}
	.arrow {
		display: grid;
		place-items: center;
		width: 2.4rem;
		height: 1.8rem;
		border: 0;
		border-radius: 6px;
		background: #5a3a14;
		color: #f6dc8c;
		cursor: pointer;
	}
	.arrow.down :global(svg) {
		rotate: 180deg;
	}
	.unit {
		margin-left: 0.2rem;
		color: #2b1a0a;
		font: 700 1.2rem var(--font-display);
	}
	.mark {
		position: relative;
		width: 1.4rem;
		height: 1.4rem;
	}
	.should {
		position: relative;
		padding: 0.4rem 0.8rem;
		border-radius: var(--r-md);
		background: #fff1e6;
		color: #8a3b12;
		font-weight: 700;
	}
	@keyframes swirl {
		to {
			rotate: 360deg;
		}
	}
	@keyframes tumble {
		from {
			transform: translateY(-60%);
			opacity: 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.vortex,
		.drum b {
			animation: none;
		}
	}
</style>
