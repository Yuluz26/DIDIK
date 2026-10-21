<!--
	Isi tempat kosong. With a word bank, tap a word to fill the next gap (tap a filled gap to clear
	it). Without one, the gaps are small text boxes in the sentence.
-->
<script lang="ts">
	import type { Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';

	let {
		parts,
		blanks,
		bank = undefined,
		disabled = false,
		mine = undefined,
		reveal = null,
		allRight = false,
		onanswer
	}: {
		parts: (string | { blank: number })[];
		blanks: number;
		bank?: string[];
		disabled?: boolean;
		mine?: string[];
		reveal?: Reveal | null;
		allRight?: boolean;
		onanswer?: (answer: string[]) => void;
	} = $props();

	// A new component is made for every question (keyed by its id), so the first count is the count.
	// svelte-ignore state_referenced_locally
	let filled = $state<string[]>(Array(blanks).fill(''));
	// svelte-ignore state_referenced_locally
	let used = $state<number[]>(Array(blanks).fill(-1));
	const values = $derived(mine ?? filled);
	const locked = $derived(disabled || !!reveal || mine !== undefined);
	const correct = $derived<string[]>(reveal ? reveal.correct : []);
	const complete = $derived(filled.every((w) => w.trim()));

	function choose(word: string, index: number) {
		if (locked) return;
		const gap = filled.findIndex((w) => !w);
		if (gap < 0) return;
		play('pop');
		filled[gap] = word;
		used[gap] = index;
	}

	function clear(gap: number) {
		if (locked || !bank) return;
		play('tap');
		filled[gap] = '';
		used[gap] = -1;
	}
</script>

<p class="sentence">
	{#each parts as part, i (i)}
		{#if typeof part === 'string'}
			<span>{part}</span>
		{:else}
			{@const gap = part.blank}
			{@const ok = reveal ? allRight || values[gap]?.trim().toLowerCase() === String(correct[gap]).toLowerCase() : null}
			{#if bank || locked}
				<button type="button" class="gap" class:full={!!values[gap]} class:ok={ok === true} class:off={ok === false} disabled={locked} onclick={() => clear(gap)}>
					{values[gap] || ' '}
				</button>
			{:else}
				<label class="visually-hidden" for="gap-{gap}">Tempat kosong {gap + 1}</label>
				<input id="gap-{gap}" class="gap-input" bind:value={filled[gap]} autocomplete="off" autocapitalize="off" spellcheck="false" maxlength="40" />
			{/if}
		{/if}
	{/each}
</p>

{#if bank && !locked}
	<div class="bank">
		{#each bank as word, i (i)}
			<button type="button" class="word" disabled={used.includes(i)} onclick={() => choose(word, i)}>{word}</button>
		{/each}
	</div>
{/if}

{#if !locked}
	<div class="row">
		<button type="button" class="btn btn--big" disabled={!complete} onclick={() => onanswer?.(filled.map((w) => w.trim()))}>Hantar <Icon name="next" /></button>
	</div>
{/if}

{#if reveal}
	<p class="answer">Jawapan: <strong>{correct.join(', ')}</strong></p>
{/if}

<style>
	.sentence {
		font: 600 clamp(1.3rem, 1.1rem + 1vw, 1.8rem) / 2 var(--font-display);
	}
	.gap {
		display: inline-block;
		min-width: 5.5rem;
		min-height: 2.6rem;
		margin: 0 0.2rem;
		padding: 0 0.8rem;
		border: 0;
		border-bottom: 4px solid var(--sun-deep);
		border-radius: 0.6rem 0.6rem 0.3rem 0.3rem;
		background: #fff3cf;
		font: inherit;
		line-height: 2.6rem;
		vertical-align: middle;
		cursor: pointer;
	}
	.gap.full {
		background: var(--card);
		animation: pop-in 320ms var(--spring);
	}
	.gap.ok {
		border-bottom-color: var(--good);
		background: var(--good-soft);
	}
	.gap.off {
		border-bottom-color: var(--almost);
		background: var(--almost-soft);
	}
	.gap:disabled {
		cursor: default;
	}
	.gap-input {
		width: 8rem;
		margin: 0 0.2rem;
		padding: 0.1rem 0.5rem;
		border: 0;
		border-bottom: 4px solid var(--sun-deep);
		border-radius: 0.6rem 0.6rem 0.3rem 0.3rem;
		background: #fff3cf;
		font: inherit;
		text-align: center;
	}
	.gap-input:focus {
		outline: 3px solid var(--sky);
	}
	.bank {
		display: flex;
		flex-wrap: wrap;
		gap: 0.55rem;
		margin-top: 0.9rem;
	}
	.word {
		min-height: 3rem;
		padding: 0.4rem 1.1rem;
		border: 0;
		border-radius: var(--r-pill);
		background: var(--card);
		box-shadow: 0 4px 0 var(--line);
		font: 600 1.2rem var(--font-display);
		cursor: pointer;
		transition: transform var(--t-state) var(--spring), opacity var(--t-state);
	}
	.word:not(:disabled):hover {
		transform: translateY(-3px) rotate(-2deg);
	}
	.word:disabled {
		opacity: 0.3;
		cursor: default;
	}
	.row {
		display: flex;
		justify-content: flex-end;
		margin-top: 1rem;
	}
	.answer {
		margin-top: 0.6rem;
		font-size: 1.1rem;
	}
</style>
