<!--
	Susun turutan: the items in their right order. Children see them shuffled and put them back.
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import { LIMITS, make, type Item } from './model';

	let { items = $bindable(), err }: { items: Item[]; err: (...path: (string | number)[]) => string | undefined } = $props();

	function move(index: number, by: number) {
		const [item] = items.splice(index, 1);
		items.splice(index + by, 0, item);
	}
</script>

<fieldset>
	<legend>Item dalam turutan yang betul</legend>
	<p class="help">Kanak-kanak akan melihat item ini bercampur, kemudian menyusunnya semula.</p>
	<ol>
		{#each items as item, i (item.id)}
			<li>
				<span class="n">{i + 1}</span>
				<input class="input" bind:value={item.text} maxlength="80" placeholder="Item {i + 1}" aria-label="Item {i + 1}" aria-invalid={!!err('items', i, 'text')} />
				<span class="moves">
					<button type="button" class="tool" onclick={() => move(i, -1)} disabled={i === 0} aria-label="Naikkan item {i + 1}"><Icon name="up" size={18} /></button>
					<button type="button" class="tool" onclick={() => move(i, 1)} disabled={i === items.length - 1} aria-label="Turunkan item {i + 1}"><Icon name="down" size={18} /></button>
					<button type="button" class="tool" onclick={() => items.splice(i, 1)} disabled={items.length <= 3} aria-label="Buang item {i + 1}"><Icon name="close" size={18} /></button>
				</span>
				{#if err('items', i, 'text')}<p class="field-error">{err('items', i, 'text')}</p>{/if}
			</li>
		{/each}
	</ol>
	{#if items.length < LIMITS.items}
		<button type="button" class="add-row" onclick={() => items.push(make.item())}><Icon name="plus" size={18} /> Tambah item</button>
	{/if}
	{#if err('items')}<p class="field-error">{err('items')}</p>{/if}
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
		grid-template-columns: auto minmax(0, 1fr) auto;
		align-items: center;
		gap: 0.5rem;
	}
	li .field-error {
		grid-column: 2 / -1;
	}
	.n {
		display: grid;
		place-items: center;
		width: 2rem;
		height: 2rem;
		border-radius: 50%;
		background: var(--brand-soft);
		color: var(--brand-deep);
		font: 600 1rem var(--font-display);
	}
	.moves {
		display: flex;
	}
</style>
