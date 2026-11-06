<!--
	The foot of a subject game while it is played: a line saying what to do next, "Mula semula" to undo
	everything, and "Semak" to send the answer once it is complete. Hidden once the answer is in.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Icon from '$ui/Icon.svelte';

	let {
		tip = '',
		ready,
		dirty = true,
		label = 'Semak',
		onreset,
		oncheck
	}: { tip?: string; ready: boolean; dirty?: boolean; label?: string; onreset?: () => void; oncheck: () => void } = $props();
</script>

{#if tip}<p class="tip" aria-live="polite">{tip}</p>{/if}
<div class="row">
	{#if onreset}
		<button type="button" class="btn btn--plain" disabled={!dirty} onclick={() => (onreset?.(), play('tap'))}>
			<Icon name="shuffle" /> Mula semula
		</button>
	{/if}
	<button type="button" class="btn btn--big check" disabled={!ready} onclick={oncheck}>
		{label} <Icon name="check" />
	</button>
</div>

<style>
	.tip {
		color: var(--ink-2);
		font-weight: 800;
		text-align: center;
	}
	.row {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 0.6rem;
	}
	.check {
		flex: 1;
		max-width: 16rem;
		margin-left: auto;
	}
</style>
