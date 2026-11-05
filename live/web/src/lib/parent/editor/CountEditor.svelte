<!--
	Kira dan masukkan: what to count, where it goes and how many. While the question still says what the
	editor wrote for it ("Masukkan 5 biji epal ke dalam bakul."), it follows these choices; once the parent
	writes their own question it is left alone.
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import { PLACES, countPrompt, stickerOf } from '$lib/stickers';
	import StickerPicker from './StickerPicker.svelte';
	import { LIMITS, type Question } from './model';

	type Count = Extract<Question, { type: 'count' }>;
	let { question = $bindable(), err }: { question: Count; err: (...path: (string | number)[]) => string | undefined } = $props();

	function change(next: Partial<Pick<Count, 'sticker' | 'place' | 'answer'>>) {
		const before = countPrompt(question.sticker, question.place, question.answer);
		const following = !question.prompt.trim() || question.prompt === before;
		Object.assign(question, next);
		if (following) question.prompt = countPrompt(question.sticker, question.place, question.answer);
	}

	const unit = $derived(stickerOf(question.sticker)?.unit ?? 'biji');
</script>

<div class="count-ed">
	<div class="what">
		<span class="label">Objek untuk dikira</span>
		<StickerPicker value={question.sticker} label="Objek" onpick={(key) => key && change({ sticker: key })} />
		{#if err('sticker')}<p class="field-error">{err('sticker')}</p>{/if}
	</div>

	<fieldset class="places">
		<legend>Masukkan ke dalam</legend>
		<div class="place-row">
			{#each PLACES as p (p.key)}
				<button type="button" class="place" aria-pressed={question.place === p.key} onclick={() => change({ place: p.key })}>
					<Sticker key={p.key} size={40} alt="" />
					<span>{p.name}</span>
				</button>
			{/each}
		</div>
	</fieldset>

	<div class="how-many">
		<span class="label" id="bilangan-{question.id}">Bilangan yang betul</span>
		<div class="stepper" role="group" aria-labelledby="bilangan-{question.id}">
			<button type="button" class="step" onclick={() => change({ answer: Math.max(1, question.answer - 1) })} disabled={question.answer <= 1} aria-label="Kurangkan"><Icon name="minus" size={20} /></button>
			<output aria-live="polite"><strong>{question.answer}</strong> {unit}</output>
			<button type="button" class="step" onclick={() => change({ answer: Math.min(LIMITS.count, question.answer + 1) })} disabled={question.answer >= LIMITS.count} aria-label="Tambah"><Icon name="plus" size={20} /></button>
		</div>
		{#if err('answer')}<p class="field-error">{err('answer')}</p>{/if}
	</div>

	<p class="help preview">
		<span class="dots" aria-hidden="true">
			{#each Array.from({ length: Math.min(question.answer, 10) }, (_, i) => i) as i (i)}<Sticker key={question.sticker} size={22} alt="" />{/each}{#if question.answer > 10}<b>+{question.answer - 10}</b>{/if}
		</span>
		Kanak-kanak melihat timbunan yang lebih banyak daripada {question.answer}, dan perlu memasukkan tepat {question.answer}. Soalan boleh juga berbentuk kira-kira, contoh "3 + 2 = ?".
	</p>
</div>

<style>
	.count-ed {
		display: grid;
		gap: 1rem;
	}
	.label,
	legend {
		display: block;
		margin-bottom: 0.45rem;
		padding: 0;
		font-weight: 800;
		font-size: 0.95rem;
	}
	.places {
		margin: 0;
		padding: 0;
		border: 0;
		min-width: 0;
	}
	.place-row {
		display: flex;
		flex-wrap: wrap;
		gap: 0.45rem;
	}
	.place {
		display: grid;
		justify-items: center;
		gap: 0.15rem;
		min-width: 4.6rem;
		padding: 0.4rem 0.5rem;
		border: 2px solid var(--line);
		border-radius: var(--r-md);
		background: var(--card);
		font-size: 0.8rem;
		font-weight: 800;
		cursor: pointer;
		transition:
			border-color var(--t-state),
			transform var(--t-state) var(--spring);
	}
	.place:hover {
		transform: translateY(-2px);
	}
	.place[aria-pressed='true'] {
		border-color: var(--brand);
		background: var(--brand-soft);
	}
	.stepper {
		display: inline-flex;
		align-items: center;
		gap: 0.6rem;
		padding: 0.25rem;
		border: 2px solid var(--line);
		border-radius: 999px;
		background: var(--card);
	}
	.step {
		display: grid;
		place-items: center;
		width: 2.75rem;
		height: 2.75rem;
		border: 0;
		border-radius: 50%;
		background: var(--paper-2);
		cursor: pointer;
	}
	.step:disabled {
		opacity: 0.4;
		cursor: default;
	}
	output {
		min-width: 6rem;
		font-weight: 800;
		text-align: center;
	}
	output strong {
		font: 600 1.5rem var(--font-display);
	}
	.preview {
		display: grid;
		gap: 0.4rem;
	}
	.dots {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.1rem;
	}
	.dots b {
		margin-left: 0.3rem;
		color: var(--ink-2);
	}
</style>
