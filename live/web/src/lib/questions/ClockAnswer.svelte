<!--
	Laraskan jam: a round clock to set to a time. Drag a hand round the face (the minute hand moves in
	steps of five minutes, the hour hand to the hours), or use the buttons under it, which also work with a
	keyboard. The hour hand leans towards the next hour as the minutes pass, as a real clock does. There is
	no digital readout while answering: reading the clock is the skill. Semak sends the hour and minute.
-->
<script lang="ts">
	import type { Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';

	let {
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: {
		disabled?: boolean;
		mine?: { h: number; m: number };
		reveal?: Reveal | null;
		onanswer?: (answer: { h: number; m: number }) => void;
	} = $props();

	let h = $state(12);
	let m = $state(0);
	const locked = $derived(disabled || !!reveal || mine !== undefined);
	const time = $derived<{ h: number; m: number }>(mine ?? (reveal && mine === undefined ? reveal.correct : { h, m }));
	const right = $derived<{ h: number; m: number } | null>(reveal ? reveal.correct : null);
	const ok = $derived(!!right && time.h === right.h && time.m === right.m);
	const minuteAngle = $derived(time.m * 6);
	const hourAngle = $derived(((time.h % 12) + time.m / 60) * 30);
	const say = (t: { h: number; m: number }) => `${t.h}.${String(t.m).padStart(2, '0')}`;

	let face = $state<SVGSVGElement>();
	let dragging: 'h' | 'm' | null = null;

	function angleAt(event: PointerEvent): number {
		const box = face!.getBoundingClientRect();
		const x = event.clientX - (box.left + box.width / 2);
		const y = event.clientY - (box.top + box.height / 2);
		return ((Math.atan2(x, -y) * 180) / Math.PI + 360) % 360;
	}

	function setFrom(event: PointerEvent) {
		const a = angleAt(event);
		if (dragging === 'm') {
			const next = (Math.round(a / 30) * 5) % 60;
			if (next !== m) play('tick');
			m = next;
		} else if (dragging === 'h') {
			const next = Math.round(a / 30) % 12 || 12;
			if (next !== h) play('tick');
			h = next;
		}
	}

	function grab(hand: 'h' | 'm', event: PointerEvent) {
		if (locked) return;
		dragging = hand;
		face?.setPointerCapture(event.pointerId);
		setFrom(event);
	}

	function step(hand: 'h' | 'm', by: number) {
		if (locked) return;
		play('tap');
		if (hand === 'h') h = ((((h - 1 + by) % 12) + 12) % 12) + 1;
		else m = (((m + by * 5) % 60) + 60) % 60;
	}
</script>

<div class="clock-q">
	<svg
		bind:this={face}
		class="face"
		class:ok={right && mine !== undefined && ok}
		class:off={right && mine !== undefined && !ok}
		viewBox="0 0 200 200"
		role="img"
		aria-label={locked ? `Jam menunjukkan pukul ${say(time)}` : 'Jam. Seret jarum, atau guna butang di bawah.'}
		onpointermove={(e) => dragging && setFrom(e)}
		onpointerup={() => (dragging = null)}
		onpointercancel={() => (dragging = null)}
	>
		<circle cx="100" cy="100" r="96" class="rim" />
		<circle cx="100" cy="100" r="86" class="dial" />
		{#each Array.from({ length: 60 }, (_, i) => i) as i (i)}
			<line x1="100" y1={i % 5 ? 18 : 16} x2="100" y2={i % 5 ? 22 : 26} class:major={i % 5 === 0} class="tick" transform="rotate({i * 6} 100 100)" />
		{/each}
		{#each Array.from({ length: 12 }, (_, i) => i + 1) as n (n)}
			<text x={100 + 62 * Math.sin((n * Math.PI) / 6)} y={100 - 62 * Math.cos((n * Math.PI) / 6)} class="num">{n}</text>
		{/each}
		<!-- the hands: wide invisible strokes make them easy to catch with a finger -->
		<g transform="rotate({hourAngle} 100 100)" class="hand-g" class:live={!locked}>
			<line x1="100" y1="108" x2="100" y2="54" class="hand hour" />
			<line x1="100" y1="100" x2="100" y2="50" class="grab" onpointerdown={(e) => grab('h', e)} role="presentation" />
		</g>
		<g transform="rotate({minuteAngle} 100 100)" class="hand-g" class:live={!locked}>
			<line x1="100" y1="112" x2="100" y2="28" class="hand minute" />
			<line x1="100" y1="100" x2="100" y2="24" class="grab" onpointerdown={(e) => grab('m', e)} role="presentation" />
		</g>
		<circle cx="100" cy="100" r="6" class="pin" />
	</svg>

	{#if !reveal && mine === undefined && !locked}
		<div class="steps">
			<div class="pair hour-c" role="group" aria-label="Jarum jam (pendek)">
				<span class="label">Jarum pendek</span>
				<button type="button" class="step" onclick={() => step('h', -1)} aria-label="Jam undur"><Icon name="minus" size={20} /></button>
				<button type="button" class="step" onclick={() => step('h', 1)} aria-label="Jam maju"><Icon name="plus" size={20} /></button>
			</div>
			<div class="pair minute-c" role="group" aria-label="Jarum minit (panjang)">
				<span class="label">Jarum panjang</span>
				<button type="button" class="step" onclick={() => step('m', -1)} aria-label="Minit undur lima"><Icon name="minus" size={20} /></button>
				<button type="button" class="step" onclick={() => step('m', 1)} aria-label="Minit maju lima"><Icon name="plus" size={20} /></button>
			</div>
		</div>
		<button type="button" class="btn btn--big check" onclick={() => onanswer?.({ h, m })}>Semak <Icon name="check" /></button>
	{/if}

	{#if right}
		<p class="answer" class:ok={mine === undefined || ok}>
			Jawapan betul: <strong>pukul {say(right)}</strong>
			{#if mine !== undefined && !ok}<span class="mine">Jam kamu: pukul {say(mine)}</span>{/if}
		</p>
	{/if}
</div>

<style>
	.clock-q {
		display: grid;
		justify-items: center;
		gap: 0.8rem;
	}
	.face {
		width: min(100%, 17rem);
		height: auto;
		touch-action: none;
		filter: drop-shadow(0 8px 14px rgb(110 80 160 / 0.18));
	}
	.rim {
		fill: #ffb3c7;
	}
	.face.ok .rim {
		fill: var(--good);
	}
	.face.off .rim {
		fill: var(--almost);
	}
	.dial {
		fill: #fffaf0;
	}
	.tick {
		stroke: #c9b8e0;
		stroke-width: 1.5;
		stroke-linecap: round;
	}
	.tick.major {
		stroke: #8a72b8;
		stroke-width: 3;
	}
	.num {
		fill: #3a2268;
		font: 600 17px 'Fredoka Variable', ui-rounded, sans-serif;
		text-anchor: middle;
		dominant-baseline: central;
	}
	.hand {
		stroke-linecap: round;
		pointer-events: none;
	}
	.hour {
		stroke: #e0567f;
		stroke-width: 8;
	}
	.minute {
		stroke: #3d7fd6;
		stroke-width: 5;
	}
	.grab {
		stroke: transparent;
		stroke-width: 26;
		stroke-linecap: round;
	}
	.hand-g.live .grab {
		cursor: grab;
	}
	.hand-g:not(.live) .grab {
		pointer-events: none;
	}
	.pin {
		fill: #3a2268;
	}
	.steps {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.6rem;
	}
	.pair {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0.25rem 0.3rem 0.25rem 0.8rem;
		border-radius: 999px;
		background: #fff;
		box-shadow: 0 3px 0 #e6dbf6;
	}
	.label {
		font-weight: 800;
		font-size: 0.88rem;
	}
	.hour-c .label {
		color: #c0395f;
	}
	.minute-c .label {
		color: #2e64ad;
	}
	.step {
		display: grid;
		place-items: center;
		width: 2.75rem;
		height: 2.75rem;
		border: 0;
		border-radius: 50%;
		background: #f3eefc;
		cursor: pointer;
	}
	.step:active {
		transform: scale(0.92);
	}
	.check {
		width: min(100%, 16rem);
	}
	.answer {
		padding: 0.6rem 0.9rem;
		border-radius: var(--r-md);
		background: var(--almost-soft);
		color: var(--on-almost-soft);
		font-weight: 800;
		text-align: center;
	}
	.answer.ok {
		background: var(--good-soft);
		color: var(--on-good-soft);
	}
	.mine {
		display: block;
		font-weight: 700;
	}
</style>
