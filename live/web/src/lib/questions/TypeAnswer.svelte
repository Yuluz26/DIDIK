<!-- Taip jawapan. Case, accents, spacing and one slip of the finger are forgiven by the server. -->
<script lang="ts">
	import type { Reveal } from '$lib/types';
	import Icon from '$ui/Icon.svelte';

	let {
		maxLength = 60,
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: { maxLength?: number; disabled?: boolean; mine?: string; reveal?: Reveal | null; onanswer?: (answer: string) => void } = $props();

	let text = $state('');
	const value = $derived(mine ?? text);

	function submit(event: Event) {
		event.preventDefault();
		if (text.trim() && !disabled) onanswer?.(text.trim());
	}
</script>

<form class="type" onsubmit={submit}>
	<label class="visually-hidden" for="typed-answer">Jawapan kamu</label>
	<input
		id="typed-answer"
		class="input big"
		value={value}
		oninput={(e) => (text = (e.target as HTMLInputElement).value)}
		maxlength={maxLength}
		autocomplete="off"
		autocapitalize="off"
		spellcheck="false"
		placeholder="Taip jawapan di sini"
		disabled={disabled || !!reveal}
	/>
	{#if !disabled && !reveal}
		<button class="btn btn--big" disabled={!text.trim()}>Hantar <Icon name="next" /></button>
	{/if}
</form>

{#if reveal}
	<p class="answer">Jawapan: <strong>{reveal.correct}</strong>
		{#if reveal.accepted && reveal.accepted.length > 1}<span class="also">(juga diterima: {reveal.accepted.slice(1).join(', ')})</span>{/if}
	</p>
{/if}

<style>
	.type {
		display: flex;
		flex-wrap: wrap;
		gap: 0.75rem;
	}
	.big {
		flex: 1 1 14rem;
		min-height: 4rem;
		font: 600 1.5rem var(--font-display);
		text-align: center;
	}
	.answer {
		margin-top: 0.8rem;
		font-size: 1.15rem;
	}
	.also {
		color: var(--ink-2);
		font-size: 0.95rem;
	}
</style>
