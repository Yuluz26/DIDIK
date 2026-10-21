<!-- Padankan: pairs of things that belong together, written side by side. -->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import { LIMITS, make, type Pair } from './model';

	let { pairs = $bindable(), err }: { pairs: Pair[]; err: (...path: (string | number)[]) => string | undefined } = $props();
</script>

<fieldset>
	<legend>Pasangan yang betul</legend>
	<p class="help">Kanak-kanak melihat kedua-dua lajur bercampur dan memadankannya.</p>
	<ol>
		{#each pairs as pair, i (pair.id)}
			<li>
				<input class="input" bind:value={pair.left} maxlength="60" placeholder="Kiri, contoh: Kucing" aria-label="Pasangan {i + 1}, kiri" aria-invalid={!!err('pairs', i, 'left')} />
				<span class="link" aria-hidden="true">↔</span>
				<input class="input" bind:value={pair.right} maxlength="60" placeholder="Kanan, contoh: Meow" aria-label="Pasangan {i + 1}, kanan" aria-invalid={!!err('pairs', i, 'right')} />
				<button type="button" class="tool" onclick={() => pairs.splice(i, 1)} disabled={pairs.length <= 2} aria-label="Buang pasangan {i + 1}"><Icon name="close" size={18} /></button>
				{#if err('pairs', i, 'left') || err('pairs', i, 'right')}<p class="field-error">{err('pairs', i, 'left') ?? err('pairs', i, 'right')}</p>{/if}
			</li>
		{/each}
	</ol>
	{#if pairs.length < LIMITS.pairs}
		<button type="button" class="add-row" onclick={() => pairs.push(make.pair())}><Icon name="plus" size={18} /> Tambah pasangan</button>
	{/if}
	{#if err('pairs')}<p class="field-error">{err('pairs')}</p>{/if}
</fieldset>

<style>
	fieldset {
		display: grid;
		gap: 0.6rem;
		margin: 0;
		padding: 0;
		border: 0;
		min-width: 0;
	}
	legend {
		padding: 0;
		font-weight: 800;
		font-size: 0.95rem;
	}
	ol {
		display: grid;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	li {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr) auto;
		align-items: center;
		gap: 0.4rem;
	}
	li .field-error {
		grid-column: 1 / -1;
	}
	.link {
		color: var(--ink-3);
		font-weight: 800;
	}
	/* On a phone each pair becomes its own small panel, so it is clear which two words belong together. */
	@media (max-width: 560px) {
		li {
			grid-template-columns: minmax(0, 1fr) auto;
			padding: 0.5rem;
			border-radius: var(--r-md);
			background: var(--paper-2);
		}
		.link {
			display: none;
		}
		li > .input:first-child {
			grid-column: 1 / -1;
		}
	}
</style>
