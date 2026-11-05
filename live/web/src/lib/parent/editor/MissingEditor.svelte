<!--
	Huruf hilang: the word, then a tap on each letter to hide (one to three, never all), a picture that
	shows the word, and how many extra letters to mix in.
-->
<script lang="ts">
	import { stickerOf } from '$lib/stickers';
	import StickerPicker from './StickerPicker.svelte';
	import { LIMITS, type Question } from './model';

	type Missing = Extract<Question, { type: 'missing' }>;
	let { question = $bindable(), err }: { question: Missing; err: (...path: (string | number)[]) => string | undefined } = $props();

	const letters = $derived(question.word.split(''));
	const bad = $derived(question.word.length > 0 && !/^[A-Za-z]+$/.test(question.word));

	function toggle(i: number) {
		if (question.hide.includes(i)) question.hide = question.hide.filter((h) => h !== i);
		else if (question.hide.length < 3 && question.hide.length < letters.length - 1) question.hide = [...question.hide, i].sort((a, b) => a - b);
	}

	function typed() {
		// letters that no longer exist cannot stay hidden
		question.hide = question.hide.filter((i) => i < question.word.length);
	}

	function picked(key: string | null) {
		const name = stickerOf(key)?.name.toLowerCase() ?? '';
		if (!question.word.trim() && /^[a-z]{2,12}$/.test(name)) {
			question.word = name;
			question.hide = [Math.min(1, name.length - 1)];
		}
	}
</script>

<div class="missing-ed">
	<div class="row">
		<label class="field word">
			<span>Perkataan</span>
			<input class="input" bind:value={question.word} oninput={typed} maxlength="12" autocomplete="off" spellcheck="false" placeholder="Contoh: kucing" aria-invalid={bad || !!err('word')} />
			{#if err('word')}<span class="field-error">{err('word')}</span>{:else if bad}<span class="field-error">Huruf sahaja, tanpa jarak, nombor atau tanda.</span>{/if}
		</label>
		<div class="field">
			<span>Gambar petunjuk</span>
			<StickerPicker bind:value={question.sticker} label="Petunjuk" optional onpick={picked} />
		</div>
	</div>

	{#if letters.length}
		<fieldset class="hide">
			<legend>Ketik huruf yang hendak disembunyikan (1 hingga 3)</legend>
			<div class="letters">
				{#each letters as ch, i (i)}
					<button type="button" class="ch" aria-pressed={question.hide.includes(i)} onclick={() => toggle(i)} aria-label="Huruf {i + 1}, {ch}">
						{question.hide.includes(i) ? '?' : ch}
					</button>
				{/each}
			</div>
			{#if err('hide')}<p class="field-error">{err('hide')}</p>{/if}
		</fieldset>
	{/if}

	<label class="field decoys">
		<span>Huruf tambahan untuk dipilih</span>
		<select class="input" bind:value={question.decoys}>
			{#each Array.from({ length: LIMITS.decoys + 1 }, (_, i) => i) as n (n)}<option value={n}>{n === 0 ? 'Tiada' : `${n} huruf`}</option>{/each}
		</select>
	</label>
</div>

<style>
	.missing-ed {
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
	.hide {
		margin: 0;
		padding: 0;
		border: 0;
	}
	.hide legend {
		margin-bottom: 0.45rem;
		padding: 0;
		font-weight: 800;
		font-size: 0.95rem;
	}
	.letters {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem;
	}
	.ch {
		display: grid;
		place-items: center;
		width: 2.6rem;
		height: 2.9rem;
		border: 2px solid var(--line);
		border-radius: 10px;
		background: var(--card);
		font: 600 1.3rem var(--font-display);
		cursor: pointer;
	}
	.ch[aria-pressed='true'] {
		border: 2px dashed var(--sky);
		background: #eef6ff;
		color: var(--sky);
	}
	.decoys select {
		width: auto;
	}
	@media (max-width: 520px) {
		.row {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
