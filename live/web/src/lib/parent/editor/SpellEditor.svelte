<!--
	Susun huruf: one word (2 to 12 letters), a sticker that shows it, and how many extra letters to mix in.
	Picking a sticker while the word is empty writes the sticker's name, when it is one plain word.
-->
<script lang="ts">
	import { stickerOf } from '$lib/stickers';
	import StickerPicker from './StickerPicker.svelte';
	import { LIMITS, type Question } from './model';

	type Spell = Extract<Question, { type: 'spell' }>;
	let { question = $bindable(), err }: { question: Spell; err: (...path: (string | number)[]) => string | undefined } = $props();

	function picked(key: string | null) {
		const name = stickerOf(key)?.name.toLowerCase() ?? '';
		if (!question.word.trim() && /^[a-z]{2,12}$/.test(name)) question.word = name;
	}

	const letters = $derived(question.word.replace(/[^A-Za-z]/g, '').split(''));
	const bad = $derived(question.word.length > 0 && !/^[A-Za-z]+$/.test(question.word));
</script>

<div class="spell-ed">
	<div class="row">
		<label class="field word">
			<span>Perkataan</span>
			<input
				class="input"
				bind:value={question.word}
				maxlength="12"
				autocomplete="off"
				autocapitalize="off"
				spellcheck="false"
				placeholder="Contoh: kucing"
				aria-invalid={bad || !!err('word')}
			/>
			{#if err('word')}<span class="field-error">{err('word')}</span>
			{:else if bad}<span class="field-error">Huruf sahaja, tanpa jarak, nombor atau tanda.</span>{/if}
		</label>
		<div class="field">
			<span>Gambar petunjuk</span>
			<StickerPicker bind:value={question.sticker} label="Petunjuk" optional onpick={picked} />
		</div>
	</div>

	<label class="field decoys">
		<span>Huruf tambahan untuk mengelirukan</span>
		<select class="input" bind:value={question.decoys}>
			{#each Array.from({ length: LIMITS.decoys + 1 }, (_, i) => i) as n (n)}
				<option value={n}>{n === 0 ? 'Tiada (paling mudah)' : `${n} huruf`}</option>
			{/each}
		</select>
	</label>

	{#if letters.length}
		<div class="help preview">
			<span>Kanak-kanak melihat:</span>
			<span class="tiles" aria-hidden="true">
				{#each [...letters].sort() as ch, i (i)}<span class="tile-ch">{ch}</span>{/each}
				{#each Array.from({ length: question.decoys }, (_, i) => i) as i (i)}<span class="tile-ch extra">?</span>{/each}
			</span>
		</div>
	{/if}
	<p class="help">Huruf besar atau kecil ikut cara perkataan ditulis. Gambar soalan (di atas) pun boleh menjadi petunjuk.</p>
</div>

<style>
	.spell-ed {
		display: grid;
		gap: 0.9rem;
	}
	.row {
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto;
		align-items: start;
		gap: 0.9rem;
	}
	.word input {
		font: 600 1.2rem var(--font-display);
		letter-spacing: 0.08em;
	}
	.decoys select {
		width: auto;
	}
	.preview {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.5rem;
	}
	.tiles {
		display: flex;
		flex-wrap: wrap;
		gap: 0.25rem;
	}
	.tile-ch {
		display: grid;
		place-items: center;
		width: 2rem;
		height: 2.2rem;
		border-radius: 8px;
		background: #ffd36b;
		box-shadow: 0 3px 0 #d99a12;
		color: var(--ink);
		font: 600 1.1rem var(--font-display);
	}
	.tile-ch.extra {
		background: #e6e1f2;
		box-shadow: 0 3px 0 #b6acd0;
		color: var(--ink-3);
	}
	@media (max-width: 520px) {
		.row {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
