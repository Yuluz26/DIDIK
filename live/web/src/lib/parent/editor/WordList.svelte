<!--
	A short list of words: the answers a typed question accepts, or the extra words in a word bank.
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';

	let {
		words = $bindable(),
		legend,
		placeholder,
		addLabel,
		max,
		min = 0,
		field,
		err
	}: {
		words: string[];
		legend: string;
		placeholder: string;
		addLabel: string;
		max: number;
		min?: number;
		field: string;
		err: (...path: (string | number)[]) => string | undefined;
	} = $props();
</script>

<fieldset class="words">
	<legend>{legend}</legend>
	{#if words.length}
		<ul>
			{#each words as _, i (i)}
				<li>
					<input class="input" bind:value={words[i]} maxlength="60" {placeholder} aria-label="{legend} {i + 1}" aria-invalid={!!err(field, i)} />
					<button type="button" class="tool" onclick={() => words.splice(i, 1)} disabled={words.length <= min} aria-label="Buang {words[i] || 'perkataan'}">
						<Icon name="close" size={18} />
					</button>
					{#if err(field, i)}<p class="field-error">{err(field, i)}</p>{/if}
				</li>
			{/each}
		</ul>
	{/if}
	{#if words.length < max}
		<button type="button" class="add-row" onclick={() => words.push('')}><Icon name="plus" size={18} /> {addLabel}</button>
	{/if}
	{#if err(field)}<p class="field-error">{err(field)}</p>{/if}
</fieldset>

<style>
	fieldset {
		display: grid;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		border: 0;
		min-width: 0;
	}
	legend {
		padding: 0;
		margin-bottom: 0.5rem;
		font-weight: 800;
		font-size: 0.95rem;
	}
	ul {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(13rem, 1fr));
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	li {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		align-items: center;
		gap: 0.3rem;
	}
	li .field-error {
		grid-column: 1 / -1;
	}
</style>
