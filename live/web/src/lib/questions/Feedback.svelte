<!--
	What a child hears after an answer. Right: a cheer. Wrong: "Hampir!" and the right answer shown
	in the question above. Never a red cross that punishes.
-->
<script lang="ts">
	import Didi from '$ui/Didi.svelte';

	let {
		correct,
		fraction = 0,
		missed = false,
		points = null,
		unit = 'mata',
		extra = ''
	}: { correct: boolean; fraction?: number; missed?: boolean; points?: number | null; unit?: string; extra?: string } = $props();

	const CHEERS = ['Betul!', 'Hebat!', 'Bagus!', 'Tepat sekali!', 'Pandainya!'];
	const cheer = CHEERS[Math.floor(Math.random() * CHEERS.length)];
	const title = $derived(correct ? cheer : missed ? 'Masa tamat' : fraction > 0 ? 'Hampir betul!' : 'Hampir!');
	const line = $derived(
		correct
			? extra
			: missed
				? 'Tak apa, soalan seterusnya pasti boleh.'
				: fraction > 0
					? `Sebahagian jawapan kamu betul (${Math.round(fraction * 100)}%).`
					: 'Lihat jawapan yang betul, kemudian cuba lagi.'
	);
</script>

<div class="feedback" class:good={correct} role="status">
	<Didi mood={correct ? 'cheer' : 'hint'} size={84} />
	<div class="words">
		<p class="title">{title}</p>
		{#if line}<p class="line">{line}</p>{/if}
	</div>
	{#if points !== null && points > 0}
		<span class="points">+{points.toLocaleString('ms-MY')} <small>{unit}</small></span>
	{/if}
</div>

<style>
	.feedback {
		display: flex;
		align-items: center;
		gap: 0.9rem;
		padding: 0.7rem 1.1rem 0.7rem 0.6rem;
		border-radius: var(--r-lg);
		background: var(--almost-soft);
		color: var(--on-almost-soft);
		animation: pop-in 460ms var(--spring);
	}
	.feedback.good {
		background: var(--good-soft);
		color: var(--on-good-soft);
	}
	.words {
		flex: 1;
		min-width: 0;
	}
	.title {
		font: 600 1.6rem/1.1 var(--font-display);
	}
	.line {
		margin-top: 0.15rem;
		font-weight: 700;
	}
	.points {
		flex: none;
		padding: 0.3rem 0.8rem;
		border-radius: var(--r-pill);
		background: #fff;
		color: var(--good);
		font: 600 1.4rem var(--font-display);
		animation: pop-in 520ms var(--spring) 120ms both;
	}
	small {
		font: 800 0.75rem var(--font-body);
		color: var(--ink-3);
	}
</style>
