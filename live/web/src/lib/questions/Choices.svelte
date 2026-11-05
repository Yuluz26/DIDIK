<!--
	Pilihan tunggal and "pilih semua yang betul". One tap answers a single-choice question; a
	multi-choice question collects taps and sends with Hantar. Keys 1 to 6 work on a keyboard.
-->
<script lang="ts">
	import type { Choice, Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';
	import Sticker from '$ui/Sticker.svelte';

	let {
		choices,
		multiple = false,
		pick = 1,
		disabled = false,
		mine = undefined,
		reveal = null,
		stats = null,
		onanswer
	}: {
		choices: Choice[];
		multiple?: boolean;
		pick?: number;
		disabled?: boolean;
		mine?: string | string[];
		reveal?: Reveal | null;
		stats?: Record<string, number> | null;
		onanswer?: (answer: string | string[]) => void;
	} = $props();

	const LETTERS = 'ABCDEF';
	let chosen = $state<string[]>([]);
	const picked = $derived(new Set(mine === undefined ? chosen : Array.isArray(mine) ? mine : [mine]));
	const right = $derived(new Set<string>(reveal ? reveal.correct : []));

	function tap(id: string) {
		if (disabled) return;
		play('tap');
		if (!multiple) {
			chosen = [id];
			onanswer?.(id);
			return;
		}
		chosen = chosen.includes(id) ? chosen.filter((c) => c !== id) : [...chosen, id];
	}

	function onkey(event: KeyboardEvent) {
		if (disabled || (event.target as HTMLElement)?.closest('input, textarea')) return;
		const index = Number(event.key) - 1;
		if (index >= 0 && index < choices.length) tap(choices[index].id);
		if (multiple && event.key === 'Enter' && chosen.length) onanswer?.(chosen);
	}
</script>

<svelte:window onkeydown={onkey} />

<div class="tiles-wrap">
<div class="tiles" class:pics={choices.some((c) => c.sticker)} class:long={!choices.some((c) => c.sticker) && choices.some((c) => c.text.length > 12)} class:one-col={!choices.some((c) => c.sticker) && choices.some((c) => c.text.length > 38)}>
	{#each choices as choice, i (choice.id)}
		{@const isRight = right.has(choice.id)}
		<button
			type="button"
			class="tile t{i}"
			class:picked={picked.has(choice.id) && !reveal}
			class:right={reveal && isRight}
			class:wrong={reveal && picked.has(choice.id) && !isRight}
			class:dim={reveal && !isRight && !picked.has(choice.id)}
			style:--i={i}
			disabled={disabled || !!reveal}
			aria-pressed={multiple ? picked.has(choice.id) : undefined}
			onclick={() => tap(choice.id)}
		>
			<span class="letter">{LETTERS[i]}</span>
			{#if choice.sticker}<span class="tile-pic"><Sticker key={choice.sticker} size={64} alt="" eager /></span>{/if}
			<span class="text">{choice.text}</span>
			{#if stats}<span class="count">{stats[choice.id] ?? 0}</span>{/if}
			{#if reveal && (isRight || picked.has(choice.id))}
				<span class="mark"><Icon name={isRight ? 'check' : 'close'} size={20} /></span>
			{:else if multiple && picked.has(choice.id)}
				<span class="mark"><Icon name="check" size={20} /></span>
			{/if}
		</button>
	{/each}
</div>
</div>

{#if multiple && !disabled && !reveal}
	<div class="send">
		<span class="hint">Pilih {pick} jawapan</span>
		<button type="button" class="btn btn--big" disabled={!chosen.length} onclick={() => onanswer?.(chosen)}>
			Hantar <Icon name="next" />
		</button>
	</div>
{/if}

<style>
	/* options with pictures: two to a row even on a small phone, the picture on top, the word under it,
	   the letter in the corner */
	.tiles.pics {
		grid-template-columns: repeat(2, minmax(0, 1fr));
	}
	.tiles.pics :global(.tile) {
		flex-direction: column;
		justify-content: center;
		gap: 0.3rem;
		min-height: 7rem;
		padding: 0.9rem 0.5rem 0.6rem;
		text-align: center;
	}
	.tiles.pics :global(.tile .letter) {
		position: absolute;
		top: 0.45rem;
		left: 0.45rem;
		width: 1.7rem;
		height: 1.7rem;
		font-size: 0.85rem;
	}
	.tile-pic {
		filter: drop-shadow(0 4px 4px rgb(0 0 0 / 0.18));
	}
	.send {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		margin-top: 1rem;
	}
	.hint {
		color: var(--ink-2);
		font-weight: 800;
	}
</style>
