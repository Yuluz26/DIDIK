<!-- "Bersedia!" then 3, 2, 1, before the first question. -->
<script lang="ts">
	import type { Clock } from '$lib/types';
	import { play } from '$lib/sound';
	import Didi from './Didi.svelte';

	let { clock, offset = 0, title = '' }: { clock: Clock | undefined; offset?: number; title?: string } = $props();

	let n = $state(3);

	$effect(() => {
		const current = clock;
		let last = -1;
		const update = () => {
			const left = current?.paused ? (current.left ?? 0) : Math.max(0, (current?.deadline ?? 0) - (Date.now() + offset));
			const value = Math.min(3, Math.ceil(left / 1000));
			if (value !== last && value > 0) play('tick');
			if (value === 0 && last > 0) play('go');
			last = value;
			n = value;
		};
		update();
		const id = setInterval(update, 100);
		return () => clearInterval(id);
	});
</script>

<div class="countdown">
	<Didi mood="cheer" size={150} />
	<p class="ready">{title || 'Bersedia!'}</p>
	{#key n}
		<span class="n" aria-live="assertive">{n > 0 ? n : 'Mula!'}</span>
	{/key}
</div>

<style>
	.countdown {
		display: grid;
		justify-items: center;
		gap: 0.6rem;
		padding: 2rem 1rem;
		text-align: center;
	}
	.ready {
		font: 600 var(--fs-h2) var(--font-display);
	}
	.n {
		display: grid;
		place-items: center;
		min-width: 7rem;
		height: 7rem;
		padding: 0 1.2rem;
		border: 3px solid var(--edge, transparent);
		border-radius: var(--r-lg);
		background: var(--sun);
		box-shadow: 0 8px 0 var(--edge, var(--sun-deep));
		font: 600 3.6rem/1 var(--font-display);
		animation: pop-in 520ms var(--spring);
	}
</style>
