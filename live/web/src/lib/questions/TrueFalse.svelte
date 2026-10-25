<script lang="ts">
	import type { Reveal } from '$lib/types';
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';

	let {
		disabled = false,
		mine = undefined,
		reveal = null,
		stats = null,
		onanswer
	}: {
		disabled?: boolean;
		mine?: boolean;
		reveal?: Reveal | null;
		stats?: Record<string, number> | null;
		onanswer?: (answer: boolean) => void;
	} = $props();

	let chosen = $state<boolean | undefined>(undefined);
	const picked = $derived(mine ?? chosen);

	function tap(value: boolean) {
		if (disabled) return;
		play('tap');
		chosen = value;
		onanswer?.(value);
	}
</script>

<div class="tiles tf">
	{#each [true, false] as value, i (value)}
		{@const isRight = reveal ? reveal.correct === value : false}
		<button
			type="button"
			class="tile {value ? 't1' : 't0'}"
			class:picked={picked === value && !reveal}
			class:right={reveal && isRight}
			class:wrong={reveal && picked === value && !isRight}
			class:dim={reveal && !isRight && picked !== value}
			style:--i={i}
			disabled={disabled || !!reveal}
			onclick={() => tap(value)}
		>
			<span class="big-icon"><Icon name={value ? 'check' : 'close'} size={34} /></span>
			<span class="text">{value ? 'Betul' : 'Salah'}</span>
			{#if stats}<span class="count">{stats[value ? 'true' : 'false'] ?? 0}</span>{/if}
		</button>
	{/each}
</div>

<style>
	.tf .tile {
		flex-direction: column;
		justify-content: center;
		min-height: 8rem;
		text-align: center;
		font-size: 1.6rem;
	}
	.tf .text {
		flex: none;
	}
	.big-icon {
		display: grid;
		place-items: center;
		width: 3.4rem;
		height: 3.4rem;
		border-radius: var(--r-md);
		background: rgb(255 255 255 / 0.25);
	}
	.tf .count {
		position: absolute;
		top: 0.6rem;
		right: 0.6rem;
	}
</style>
