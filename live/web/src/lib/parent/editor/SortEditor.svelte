<!--
	Isih kumpulan: two or three baskets, each with a name and a sticker, and three to eight things, each
	with its words, a sticker if wanted, and the basket it belongs in.
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import { stickerOf } from '$lib/stickers';
	import StickerPicker from './StickerPicker.svelte';
	import { LIMITS, make, type Question } from './model';

	type Sort = Extract<Question, { type: 'sort' }>;
	let { question = $bindable(), err }: { question: Sort; err: (...path: (string | number)[]) => string | undefined } = $props();

	const TINTS = ['#ffe3ec', '#dff4ff', '#e6f8d8'];

	function removeGroup(index: number) {
		const [gone] = question.groups.splice(index, 1);
		question.items.forEach((item) => item.group === gone.id && (item.group = question.groups[0].id));
	}

	function named(index: number, key: string | null) {
		const item = question.items[index];
		if (!item.text.trim() && key) item.text = stickerOf(key)?.name ?? '';
	}

	function groupNamed(index: number, key: string | null) {
		const group = question.groups[index];
		if (!group.name.trim() && key) group.name = stickerOf(key)?.name ?? '';
	}
</script>

<div class="sort-ed">
	<fieldset>
		<legend>Bakul (kumpulan)</legend>
		<ol class="groups">
			{#each question.groups as group, g (group.id)}
				<li style:--tint={TINTS[g % 3]}>
					<StickerPicker bind:value={group.sticker} label="Gambar bakul {g + 1}" optional compact onpick={(key) => groupNamed(g, key)} />
					<input class="input" bind:value={group.name} maxlength="30" placeholder={['Contoh: Darat', 'Contoh: Laut', 'Contoh: Udara'][g]} aria-label="Nama bakul {g + 1}" aria-invalid={!!err('groups', g, 'name')} />
					<button type="button" class="tool" onclick={() => removeGroup(g)} disabled={question.groups.length <= 2} aria-label="Buang bakul {g + 1}"><Icon name="close" size={18} /></button>
					{#if err('groups', g, 'name')}<p class="field-error">{err('groups', g, 'name')}</p>{/if}
				</li>
			{/each}
		</ol>
		{#if question.groups.length < LIMITS.groups}
			<button type="button" class="add-row" onclick={() => question.groups.push(make.group())}><Icon name="plus" size={18} /> Tambah bakul ketiga</button>
		{/if}
	</fieldset>

	<fieldset>
		<legend>Benda untuk diisih</legend>
		<p class="help">Tulis nama benda, pilih gambarnya, kemudian ketik bakul yang betul untuknya.</p>
		<ol class="things">
			{#each question.items as item, i (item.id)}
				<li>
					<StickerPicker bind:value={item.sticker} label="Gambar benda {i + 1}" optional compact onpick={(key) => named(i, key)} />
					<input class="input" bind:value={item.text} maxlength="40" placeholder="Benda {i + 1}" aria-label="Benda {i + 1}" aria-invalid={!!err('items', i, 'text')} />
					<button type="button" class="tool" onclick={() => question.items.splice(i, 1)} disabled={question.items.length <= 3} aria-label="Buang benda {i + 1}"><Icon name="close" size={18} /></button>
					<div class="belongs" role="group" aria-label="Bakul untuk benda {i + 1}">
						{#each question.groups as group, g (group.id)}
							<button type="button" class="chip-g" style:--tint={TINTS[g % 3]} aria-pressed={item.group === group.id} onclick={() => (item.group = group.id)}>
								{group.name || `Bakul ${g + 1}`}
							</button>
						{/each}
					</div>
					{#if err('items', i, 'text')}<p class="field-error">{err('items', i, 'text')}</p>{/if}
				</li>
			{/each}
		</ol>
		{#if question.items.length < LIMITS.things}
			<button type="button" class="add-row" onclick={() => question.items.push(make.thing(question.groups[question.items.length % question.groups.length].id))}>
				<Icon name="plus" size={18} /> Tambah benda
			</button>
		{/if}
		{#if err('items')}<p class="field-error">{err('items')}</p>{/if}
		{#if err('groups')}<p class="field-error">{err('groups')}</p>{/if}
	</fieldset>
</div>

<style>
	.sort-ed {
		display: grid;
		gap: 1.1rem;
	}
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
	.groups li {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr) auto;
		align-items: center;
		gap: 0.5rem;
		padding: 0.4rem;
		border-radius: var(--r-md);
		background: var(--tint);
	}
	.things li {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr) auto;
		align-items: center;
		gap: 0.45rem 0.5rem;
		padding-bottom: 0.5rem;
		border-bottom: 2px solid var(--paper-2);
	}
	li .field-error,
	.belongs {
		grid-column: 2 / -1;
	}
	.belongs {
		display: flex;
		flex-wrap: wrap;
		gap: 0.35rem;
	}
	.chip-g {
		min-height: 2.4rem;
		padding: 0 0.85rem;
		border: 2px solid transparent;
		border-radius: 999px;
		background: var(--paper);
		color: var(--ink-2);
		font-weight: 800;
		cursor: pointer;
	}
	.chip-g[aria-pressed='true'] {
		border-color: var(--ink);
		background: var(--tint);
		color: var(--ink);
	}
</style>
