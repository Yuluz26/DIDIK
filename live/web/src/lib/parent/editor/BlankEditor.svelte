<!--
	Isi tempat kosong: a sentence with the missing words in [brackets], a preview of what children
	see, and extra words for the word bank so the answer is not simply the only word left.
-->
<script lang="ts">
	import { LIMITS, sentenceParts } from './model';
	import WordList from './WordList.svelte';

	let {
		sentence = $bindable(),
		distractors = $bindable(),
		wordBank = $bindable(),
		id,
		err
	}: {
		sentence: string;
		distractors: string[];
		wordBank: boolean;
		id: string;
		err: (...path: (string | number)[]) => string | undefined;
	} = $props();

	const parts = $derived(sentenceParts(sentence));
	const blanks = $derived(parts.filter((p) => 'answers' in p).length);
</script>

<div class="blank-editor">
	<label class="field">
		<span>Ayat</span>
		<textarea
			class="input"
			rows="2"
			bind:value={sentence}
			maxlength="300"
			placeholder="Contoh: Adik [minum] susu setiap pagi."
			aria-describedby="blank-help-{id}"
			aria-invalid={!!err('sentence')}
		></textarea>
	</label>
	<p class="help" id="blank-help-{id}">
		Letak jawapan dalam [kurungan], 1 hingga 4 tempat. Jika ada jawapan lain yang juga betul, pisahkan dengan garis miring: [minum/meminum].
	</p>
	{#if err('sentence')}<p class="field-error">{err('sentence')}</p>{/if}

	{#if blanks}
		<p class="preview" aria-label="Pratonton ayat">
			{#each parts as part, i (i)}
				{#if 'answers' in part}<span class="gap" title={part.answers.join(' / ')}>{part.answers[0]}</span>{:else}{part.text}{/if}
			{/each}
		</p>
	{/if}

	<label class="check-row">
		<input type="checkbox" bind:checked={wordBank} />
		<span>Tunjuk bank perkataan (kanak-kanak pilih perkataan, tidak perlu menaip)</span>
	</label>
	{#if wordBank}
		<WordList
			bind:words={distractors}
			legend="Perkataan pengganggu (pilihan)"
			placeholder="Contoh: makan"
			addLabel="Tambah pengganggu"
			max={LIMITS.distractors}
			field="distractors"
			{err}
		/>
	{/if}
</div>

<style>
	.blank-editor {
		display: grid;
		gap: 0.6rem;
	}
	textarea {
		resize: vertical;
	}
	.preview {
		padding: 0.7rem 0.9rem;
		border-radius: var(--r-sm);
		background: var(--paper-2);
		line-height: 2;
	}
	.gap {
		display: inline-block;
		min-width: 4rem;
		margin: 0 0.15rem;
		padding: 0 0.6rem;
		border-bottom: 3px solid var(--brand);
		border-radius: 6px 6px 0 0;
		background: var(--card);
		color: var(--brand-deep);
		text-align: center;
		line-height: 1.6;
	}
</style>
