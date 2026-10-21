<!-- The question itself: its kind, the words, an optional picture, and "Bacakan" to hear it. -->
<script lang="ts">
	import type { PublicQuestion } from '$lib/types';
	import { canSpeak, speak } from '$lib/speech';
	import Icon from '$ui/Icon.svelte';

	let {
		question,
		index = null,
		total = null,
		big = false
	}: { question: PublicQuestion; index?: number | null; total?: number | null; big?: boolean } = $props();

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
		<h2 class="prompt">{question.prompt}</h2>
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
		color: var(--brand-deep);
		font-weight: 800;
		font-size: 0.9rem;
		cursor: pointer;
		transition: transform var(--t-state) var(--spring);
	}
	.read:hover {
		transform: scale(1.06);
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
