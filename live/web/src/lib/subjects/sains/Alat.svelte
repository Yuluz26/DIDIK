<!--
	Alat Pengukur: the answer is read off an instrument the child sets: a thermometer for °C, a measuring
	cylinder for ml or l, a ruler for cm, mm or m, a spring balance for kg or g, a dial gauge for anything
	else. Drag the instrument (or use − and +) to the reading; the exact number shows beside it and can be
	typed too. The instrument's range comes from the unit only, never from the answer.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	type Kind = 'thermo' | 'cylinder' | 'ruler' | 'scale' | 'gauge';
	const unit = $derived((p.question.unit ?? '').trim());
	const spec = $derived.by((): { kind: Kind; min: number; max: number; step: number; name: string } => {
		const u = unit.toLowerCase();
		if (/°?c$|celsius/.test(u)) return { kind: 'thermo', min: -10, max: 110, step: 1, name: 'Termometer' };
		if (u === 'ml') return { kind: 'cylinder', min: 0, max: 1000, step: 10, name: 'Silinder penyukat' };
		if (u === 'l' || u === 'liter' || u === 'litre') return { kind: 'cylinder', min: 0, max: 10, step: 0.5, name: 'Silinder penyukat' };
		if (u === 'cm') return { kind: 'ruler', min: 0, max: 30, step: 0.5, name: 'Pembaris' };
		if (u === 'mm') return { kind: 'ruler', min: 0, max: 300, step: 1, name: 'Pembaris' };
		if (u === 'm') return { kind: 'ruler', min: 0, max: 100, step: 1, name: 'Pita pengukur' };
		if (u === 'kg') return { kind: 'scale', min: 0, max: 100, step: 0.5, name: 'Neraca spring' };
		if (u === 'g') return { kind: 'scale', min: 0, max: 1000, step: 10, name: 'Neraca spring' };
		return { kind: 'gauge', min: 0, max: 1000, step: 1, name: 'Meter bacaan' };
	});

	const locked = $derived(isLocked(p));
	let value = $state<number | null>(null);
	const shown = $derived<number | null>(p.mine !== undefined ? Number(String(p.mine).replace(',', '.')) : p.reveal ? Number(p.reveal.correct) : value);
	const right = $derived<number | null>(p.reveal ? Number(p.reveal.correct) : null);
	const ok = $derived(right !== null && shown !== null ? Math.abs(shown - right) <= (p.reveal?.tolerance ?? 0) + 1e-9 : null);
	const frac = $derived(shown === null ? 0 : Math.max(0, Math.min(1, (shown - spec.min) / (spec.max - spec.min))));

	const snap = (v: number) => Math.round(Math.max(spec.min, Math.min(spec.max, v)) / spec.step) * spec.step;
	const fmt = (v: number) => (Number.isInteger(v) ? String(v) : v.toFixed(1));
	let track: HTMLDivElement;
	let holding = false;

	function at(event: PointerEvent) {
		if (locked) return;
		const box = track.getBoundingClientRect();
		const t = spec.kind === 'ruler' ? (event.clientX - box.left) / box.width : 1 - (event.clientY - box.top) / box.height;
		const next = snap(spec.min + Math.max(0, Math.min(1, t)) * (spec.max - spec.min));
		if (next !== value) {
			value = next;
			play('tick');
		}
	}
	function nudge(dir: number) {
		if (locked) return;
		value = snap((value ?? spec.min) + dir * spec.step);
		play('tick');
	}
	const ticks = $derived(Array.from({ length: 11 }, (_, i) => spec.min + ((spec.max - spec.min) * i) / 10));
</script>

<div class="bench {spec.kind}">
	<div
		class="instrument"
		bind:this={track}
		role="slider"
		tabindex={locked ? -1 : 0}
		aria-label={spec.name}
		aria-valuemin={spec.min}
		aria-valuemax={spec.max}
		aria-valuenow={shown ?? spec.min}
		onpointerdown={(e) => ((holding = true), at(e))}
		onpointermove={(e) => holding && at(e)}
		onpointerup={() => (holding = false)}
		onpointerleave={() => (holding = false)}
		onkeydown={(e) => (e.key === 'ArrowUp' || e.key === 'ArrowRight' ? nudge(1) : e.key === 'ArrowDown' || e.key === 'ArrowLeft' ? nudge(-1) : null)}
	>
		<div class="scale">
			{#each ticks as t (t)}<span style:--t={(t - spec.min) / (spec.max - spec.min)}>{fmt(t)}</span>{/each}
		</div>
		<div class="fill" style:--f={frac}></div>
		{#if spec.kind === 'thermo'}<span class="bulb" aria-hidden="true"></span>{/if}
		{#if spec.kind === 'scale'}<span class="hook" style:--f={frac} aria-hidden="true">⚖</span>{/if}
	</div>
	<div class="readout">
		<span class="name">{spec.name}</span>
		<div class="digits">
			{#if !locked}<button type="button" class="nudge" onclick={() => nudge(-1)} aria-label="Kurang"><Icon name="minus" /></button>{/if}
			{#if locked}
				<strong class:ok={ok === true} class:off={ok === false}>{shown === null ? '–' : fmt(shown)}</strong>
			{:else}
				<input
					type="number"
					inputmode="decimal"
					step={spec.step}
					value={value ?? ''}
					oninput={(e) => {
						const n = Number((e.currentTarget as HTMLInputElement).value);
						value = Number.isFinite(n) && (e.currentTarget as HTMLInputElement).value !== '' ? n : null;
					}}
					aria-label="Bacaan"
				/>
			{/if}
			<span class="unit">{unit}</span>
			{#if !locked}<button type="button" class="nudge" onclick={() => nudge(1)} aria-label="Tambah"><Icon name="plus" /></button>{/if}
		</div>
		{#if ok !== null}<span class="mark-row"><Mark {ok} size={16} /></span>{/if}
		{#if ok === false && right !== null}<p class="should">Bacaan betul: <strong>{fmt(right)} {unit}</strong></p>{/if}
	</div>
</div>
{#if !locked}
	<Checks tip="Seret alat atau taip bacaan." ready={value !== null} dirty={value !== null} onreset={() => (value = null)} oncheck={() => p.onanswer?.(value)} />
{/if}

<style>
	.bench {
		container-type: inline-size;
		display: grid;
		grid-template-columns: auto minmax(0, 1fr);
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #eef4f6, #dbe6ea);
		box-shadow: inset 0 0 0 3px #c1d1d8;
	}
	.bench.ruler {
		grid-template-columns: 1fr;
	}
	.instrument {
		position: relative;
		touch-action: none;
		cursor: ns-resize;
	}
	.instrument:focus-visible {
		outline: 3px solid var(--sky);
		outline-offset: 4px;
	}
	/* vertical instruments */
	.thermo .instrument,
	.cylinder .instrument,
	.scale .instrument,
	.gauge .instrument {
		width: 4.2rem;
		height: 16rem;
		margin-left: 2.2rem;
	}
	.scale-labels {
		display: none;
	}
	.scale {
		position: absolute;
		inset: 0;
	}
	.scale span {
		position: absolute;
		right: calc(100% + 0.3rem);
		bottom: calc(var(--t) * 100%);
		translate: 0 50%;
		color: #3a4a55;
		font: 700 0.68rem var(--font-body);
		white-space: nowrap;
	}
	.scale span::after {
		content: '';
		position: absolute;
		left: calc(100% + 0.15rem);
		top: 50%;
		width: 0.5rem;
		height: 2px;
		background: #3a4a55;
	}
	.thermo .instrument {
		width: 1.4rem;
		border-radius: 0.7rem 0.7rem 0 0;
		background: rgb(255 255 255 / 0.9);
		box-shadow: inset 0 0 0 2px #9fb3bd;
	}
	.thermo .fill {
		position: absolute;
		left: 0.35rem;
		right: 0.35rem;
		bottom: 0;
		height: calc(var(--f) * 100%);
		border-radius: 0.4rem 0.4rem 0 0;
		background: linear-gradient(180deg, #ff5b4a, #d62b1b);
		transition: height 0.15s;
	}
	.bulb {
		position: absolute;
		left: 50%;
		bottom: -1.6rem;
		width: 2.2rem;
		height: 2.2rem;
		translate: -50% 0;
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, #ff9b8f, #d62b1b);
		box-shadow: 0 0 0 2px #9fb3bd;
	}
	.cylinder .instrument {
		border: 3px solid rgb(150 180 195 / 0.95);
		border-top: 0;
		border-radius: 0 0 0.6rem 0.6rem;
		background: rgb(255 255 255 / 0.6);
	}
	.cylinder .fill {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		height: calc(var(--f) * 100%);
		background: linear-gradient(180deg, rgb(100 180 230 / 0.8), rgb(40 120 190 / 0.85));
		border-top: 4px solid rgb(180 220 245);
		border-radius: 0 0 0.4rem 0.4rem;
		transition: height 0.15s;
	}
	.scale .instrument {
		width: 2.4rem;
		border-radius: 0.6rem;
		background: linear-gradient(90deg, #c9d2d8, #f2f5f7, #c9d2d8);
		box-shadow: inset 0 0 0 2px #8fa3ae;
	}
	.scale .fill {
		position: absolute;
		left: 0.5rem;
		right: 0.5rem;
		top: 0;
		height: calc(var(--f) * 100%);
		background: repeating-linear-gradient(180deg, #8fa3ae 0 3px, transparent 3px 7px);
		transition: height 0.15s;
	}
	.hook {
		position: absolute;
		left: 50%;
		top: calc(var(--f) * 100%);
		translate: -50% 0;
		font-size: 1.4rem;
	}
	.gauge .instrument {
		width: 2rem;
		border-radius: 1rem;
		background: #23262f;
	}
	.gauge .fill {
		position: absolute;
		left: 0.3rem;
		right: 0.3rem;
		bottom: 0.3rem;
		height: calc(var(--f) * (100% - 0.6rem));
		border-radius: 0.7rem;
		background: linear-gradient(180deg, #7cf29a, #1fae55);
		transition: height 0.15s;
	}
	/* the ruler lies flat */
	.ruler .instrument {
		width: 100%;
		height: 4.4rem;
		margin-top: 0.4rem;
		border-radius: 6px;
		background: linear-gradient(180deg, #ffe58a, #f2c94c);
		box-shadow:
			inset 0 0 0 2px #c79a2a,
			0 4px 8px rgb(0 0 0 / 0.15);
		cursor: ew-resize;
	}
	.ruler .scale span {
		right: auto;
		left: calc(var(--t) * 100%);
		bottom: auto;
		top: 1.2rem;
		translate: -50% 0;
	}
	.ruler .scale span::after {
		left: 50%;
		top: -1.2rem;
		width: 2px;
		height: 0.9rem;
	}
	.ruler .fill {
		position: absolute;
		left: 0;
		bottom: 0.3rem;
		width: calc(var(--f) * 100%);
		height: 0.9rem;
		border-radius: 0 4px 4px 0;
		background: rgb(214 43 27 / 0.75);
		transition: width 0.15s;
	}
	.readout {
		display: grid;
		gap: 0.4rem;
		justify-items: center;
	}
	.name {
		color: #3a4a55;
		font: 700 0.85rem var(--font-display);
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	.digits {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0.4rem 0.6rem;
		border-radius: 10px;
		background: #1b2027;
		color: #7cf29a;
		box-shadow: inset 0 0 0 2px #39424e;
	}
	.digits input,
	.digits strong {
		width: 5.2rem;
		border: 0;
		background: transparent;
		color: #7cf29a;
		font: 700 1.8rem/1.1 'Courier New', monospace;
		text-align: center;
	}
	.digits strong.ok {
		color: #7cf29a;
	}
	.digits strong.off {
		color: #ffb07a;
	}
	.unit {
		font: 700 1.1rem var(--font-display);
	}
	.nudge {
		display: grid;
		place-items: center;
		width: 2.2rem;
		height: 2.2rem;
		border: 0;
		border-radius: 50%;
		background: #39424e;
		color: #fff;
		cursor: pointer;
	}
	/* on a phone the readout beside a cylinder or thermometer gets a little smaller rather than spill out */
	@container (max-width: 19.5rem) {
		.digits {
			gap: 0.2rem;
			padding: 0.35rem 0.4rem;
		}
		.digits input,
		.digits strong {
			width: 4rem;
			font-size: 1.45rem;
		}
		.unit {
			font-size: 0.95rem;
		}
		.nudge {
			width: 1.9rem;
			height: 1.9rem;
		}
	}
	@container (max-width: 17rem) {
		.name {
			letter-spacing: 0;
			font-size: 0.75rem;
		}
		.digits {
			gap: 0.1rem;
			padding: 0.3rem 0.3rem;
		}
		.digits input,
		.digits strong {
			width: 3rem;
			font-size: 1.15rem;
		}
		.nudge {
			width: 1.6rem;
			height: 1.6rem;
		}
	}
	.mark-row {
		position: relative;
		width: 1.6rem;
		height: 1.6rem;
	}
	.should {
		color: #8a3b12;
		font-weight: 700;
		text-align: center;
	}
</style>
