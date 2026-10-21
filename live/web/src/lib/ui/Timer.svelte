<!--
	The question clock: a bar that drains and the seconds left. Every device reads the same server
	deadline (corrected by the measured clock offset), so friends see the same time.
-->
<script lang="ts">
	import type { Clock } from '$lib/types';
	import { play } from '$lib/sound';

	let {
		clock,
		offset = 0,
		total = 20,
		ticks = false,
		compact = false
	}: { clock: Clock | undefined; offset?: number; total?: number; ticks?: boolean; compact?: boolean } = $props();

	let left = $state(0);

	$effect(() => {
		const current = clock;
		let lastWhole = -1;
		const update = () => {
			if (!current) {
				left = 0;
				return;
			}
			if (current.paused) {
				left = (current.left ?? 0) / 1000;
				return;
			}
			left = Math.max(0, ((current.deadline ?? 0) - (Date.now() + offset)) / 1000);
			const whole = Math.ceil(left);
			if (ticks && whole !== lastWhole && whole > 0 && whole <= 5) play('tick');
			lastWhole = whole;
		};
		update();
		const id = setInterval(update, 100);
		return () => clearInterval(id);
	});

	const ratio = $derived(total > 0 ? Math.min(1, left / total) : 0);
	const urgent = $derived(left > 0 && left <= Math.min(5, total * 0.25));
	const shown = $derived(left >= 60 ? `${Math.floor(left / 60)}:${String(Math.floor(left % 60)).padStart(2, '0')}` : `${Math.ceil(left)}`);
</script>

<div class="timer" class:urgent class:compact class:paused={clock?.paused} role="timer" aria-label="Masa tinggal {Math.ceil(left)} saat">
	<div class="track"><div class="fill" style:transform="scaleX({ratio})"></div></div>
	<span class="secs" aria-hidden="true">{clock?.paused ? 'Rehat' : shown}</span>
</div>

<style>
	.timer {
		display: flex;
		align-items: center;
		gap: 0.7rem;
		width: 100%;
	}
	.track {
		flex: 1;
		height: 0.8rem;
		border-radius: var(--r-pill);
		background: rgb(31 45 39 / 0.1);
		overflow: hidden;
	}
	.compact .track {
		height: 0.55rem;
	}
	.fill {
		height: 100%;
		border-radius: inherit;
		background: var(--sun);
		transform-origin: left center;
		transition:
			transform 0.1s linear,
			background-color var(--t-state);
	}
	.urgent .fill {
		background: var(--coral);
	}
	.secs {
		min-width: 2.6rem;
		padding: 0.15rem 0.6rem;
		border-radius: var(--r-pill);
		background: var(--card);
		box-shadow: 0 2px 0 var(--line);
		font: 600 1.1rem/1.3 var(--font-display);
		text-align: center;
		font-variant-numeric: tabular-nums;
	}
	.urgent .secs {
		color: var(--coral-deep);
		animation: pulse 1s ease-in-out infinite;
	}
	.paused .secs {
		color: var(--ink-2);
	}
	@keyframes pulse {
		50% {
			transform: scale(1.12);
		}
	}
</style>
