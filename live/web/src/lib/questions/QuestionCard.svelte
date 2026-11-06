<!-- The question itself: its kind, the words, an optional picture, and "Bacakan" to hear it. -->
<script lang="ts">
	import type { PublicQuestion } from '$lib/types';
	import { canSpeak, speak } from '$lib/speech';
	import Icon from '$ui/Icon.svelte';
	import { isDiagram } from '$lib/diagrams';
	import DiagramFigure from '$ui/DiagramFigure.svelte';
	import Sticker from '$ui/Sticker.svelte';

	let {
		question,
		index = null,
		total = null,
		big = false
	}: { question: PublicQuestion; index?: number | null; total?: number | null; big?: boolean } = $props();

	// a sticker sits beside the words; a diagram or photo goes under them, as large as it needs
	const sticker = $derived(question.picture && !isDiagram(question.picture) ? question.picture : null);
	const diagram = $derived(isDiagram(question.picture) ? question.picture : null);

	function readAloud() {
		const options = question.choices?.map((c) => c.text).join(', ');
		speak(options ? `${question.prompt}. ${options}` : question.prompt);
	}
</script>

<section class="question" class:big aria-live="polite">
	<div class="meta">
		{#if index !== null && total !== null}<span class="chip">Soalan {index + 1} / {total}</span>{/if}
		<span class="chip">{question.label}</span>
		{#if canSpeak()}
			<button type="button" class="read" onclick={readAloud}><Icon name="speak" size={18} /> Bacakan</button>
		{/if}
	</div>
	{#key question.id}
		<div class="prompt-row" class:with-pic={!!sticker}>
			<h2 class="prompt">{question.prompt}</h2>
			{#if sticker}<span class="pic" aria-hidden="true"><Sticker key={sticker} size={big ? 120 : 84} alt="" eager /></span>{/if}
		</div>
		{#if diagram && question.type !== 'diagram'}<DiagramFigure key={diagram} max={big ? 320 : 220} />{/if}
	{/key}
	{#if question.image}
		<img class="picture" src={question.image} alt="" loading="eager" />
	{/if}
</section>

<style>
	.question {
		display: grid;
		gap: 0.8rem;
	}
	.meta {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.45rem;
	}
	.read {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		margin-left: auto;
		padding: 0.3rem 0.75rem;
		border: 0;
		border-radius: var(--r-pill);
		background: var(--brand-soft);
		color: var(--on-brand-soft);
		font-weight: 800;
		font-size: 0.9rem;
		cursor: pointer;
		transition: transform var(--t-state) var(--spring);
	}
	.read:hover {
		transform: scale(1.06);
	}
	.prompt-row.with-pic {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		align-items: center;
		gap: 0.8rem;
	}
	.pic {
		filter: drop-shadow(0 6px 8px rgb(31 45 39 / 0.18));
		animation: pop-in var(--t-enter) var(--spring);
	}
	.prompt {
		font-size: clamp(1.45rem, 1.1rem + 1.6vw, 2.2rem);
		line-height: 1.18;
		animation: rise-in var(--t-enter) var(--ease-out);
	}
	.big .prompt {
		font-size: clamp(1.8rem, 1rem + 2.6vw, 3.2rem);
	}
	.picture {
		justify-self: center;
		max-height: min(34vh, 320px);
		width: auto;
		border-radius: var(--r-md);
		box-shadow: var(--card-shadow);
		animation: pop-in var(--t-enter) var(--spring);
	}
</style>
