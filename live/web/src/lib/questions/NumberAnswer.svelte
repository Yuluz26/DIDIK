<!-- Nombor: a big keypad, easier for small fingers than the phone keyboard. Typing works too. -->
<script lang="ts">
	import type { Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';

	let {
		unit = '',
		disabled = false,
		mine = undefined,
		reveal = null,
		onanswer
	}: { unit?: string; disabled?: boolean; mine?: number | string; reveal?: Reveal | null; onanswer?: (answer: string) => void } = $props();

	let value = $state('');
	const shown = $derived(mine !== undefined ? String(mine) : value);
	const KEYS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '0', ','];

	function press(key: string) {
		if (disabled || reveal) return;
		play('tap');
		if (key === 'del') value = value.slice(0, -1);
		else if (key === '-') value = value.startsWith('-') ? value.slice(1) : `-${value}`;
		else if (key === ',' && (value.includes(',') || !value)) return;
		else if (value.replace('-', '').length < 9) value += key;
	}

	function submit() {
		if (value && value !== '-' && !disabled) onanswer?.(value);
	}

	function onkey(event: KeyboardEvent) {
		if (disabled || reveal) return;
		if (/^[0-9]$/.test(event.key)) press(event.key);
		else if (event.key === ',' || event.key === '.') press(',');
		else if (event.key === '-') press('-');
		else if (event.key === 'Backspace') press('del');
		else if (event.key === 'Enter') submit();
	}
</script>

<svelte:window onkeydown={onkey} />

<div class="number">
	<output class="display" aria-live="polite">{shown || ' '}{#if unit}<span class="unit">{unit}</span>{/if}</output>
	{#if !disabled && !reveal}
		<div class="pad">
			{#each KEYS as key (key)}
				<button type="button" class="key" onclick={() => press(key)} aria-label={key === '-' ? 'Tanda negatif' : key === ',' ? 'Titik perpuluhan' : key}>{key}</button>
			{/each}
		</div>
		<div class="row">
			<button type="button" class="btn btn--plain" onclick={() => press('del')} aria-label="Padam satu digit"><Icon name="back" /> Padam</button>
			<button type="button" class="btn btn--big" disabled={!value || value === '-'} onclick={submit}>Hantar <Icon name="next" /></button>
		</div>
	{/if}
	{#if reveal}
		<p class="answer">Jawapan: <strong>{reveal.correct}{reveal.unit ? ` ${reveal.unit}` : ''}</strong>
			{#if reveal.tolerance}<span class="also">(± {reveal.tolerance} diterima)</span>{/if}</p>
	{/if}
</div>

<style>
	.number {
		display: grid;
		gap: 0.8rem;
		max-width: 26rem;
		margin-inline: auto;
		width: 100%;
	}
	.display {
		display: flex;
		align-items: baseline;
		justify-content: center;
		gap: 0.5rem;
		min-height: 4.2rem;
		padding: 0.5rem 1rem;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: inset 0 -4px 0 var(--line);
		font: 600 2.4rem/1.2 var(--font-display);
		font-variant-numeric: tabular-nums;
	}
	.unit {
		color: var(--ink-2);
		font-size: 1.2rem;
	}
	.pad {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.55rem;
	}
	.key {
		min-height: 3.5rem;
		border: 0;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: 0 4px 0 var(--line);
		font: 600 1.6rem var(--font-display);
		cursor: pointer;
		transition: transform var(--t-press) var(--ease-out), box-shadow var(--t-press);
	}
	.key:hover {
		transform: translateY(-2px);
	}
	.key:active {
		transform: translateY(3px);
		box-shadow: 0 1px 0 var(--line);
	}
	.row {
		display: flex;
		justify-content: space-between;
		gap: 0.75rem;
	}
	.answer {
		text-align: center;
		font-size: 1.15rem;
	}
	.also {
		color: var(--ink-2);
		font-size: 0.95rem;
	}
</style>
