<!--
	One question in the quiz editor: its type, words, picture and time, then the part that depends on
	the type. Errors from the server appear beside the field they are about.
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import BlankEditor from './BlankEditor.svelte';
	import ChoicesEditor from './ChoicesEditor.svelte';
	import ImageField from './ImageField.svelte';
	import OrderEditor from './OrderEditor.svelte';
	import PairsEditor from './PairsEditor.svelte';
	import TypeIcon from './TypeIcon.svelte';
	import WordList from './WordList.svelte';
	import { LIMITS, TIME_LIMITS, TYPES, blank, type Question, type QuestionType } from './model';

	let {
		question = $bindable(),
		index,
		count,
		err,
		onmove,
		onduplicate,
		onremove
	}: {
		question: Question;
		index: number;
		count: number;
		err: (...path: (string | number)[]) => string | undefined;
		onmove: (by: number) => void;
		onduplicate: () => void;
		onremove: () => void;
	} = $props();

	let confirming = $state(false);

	function retype(event: Event) {
		question = blank((event.currentTarget as HTMLSelectElement).value as QuestionType, question);
	}

	const problem = $derived(err());
</script>

<article class="question" id="soalan-{index + 1}" class:has-problem={!!problem} aria-labelledby="q-title-{question.id}">
	<header>
		<h3 id="q-title-{question.id}"><span class="n">{index + 1}</span><span class="visually-hidden">Soalan {index + 1}</span></h3>
		<div class="type">
			<TypeIcon type={question.type} />
			<select value={question.type} onchange={retype} aria-label="Jenis soalan {index + 1}">
				{#each TYPES as t (t.type)}<option value={t.type}>{t.name}</option>{/each}
			</select>
		</div>
		<div class="tools">
			<button type="button" class="tool" onclick={() => onmove(-1)} disabled={index === 0} aria-label="Naikkan soalan {index + 1}"><Icon name="up" size={18} /></button>
			<button type="button" class="tool" onclick={() => onmove(1)} disabled={index === count - 1} aria-label="Turunkan soalan {index + 1}"><Icon name="down" size={18} /></button>
			<button type="button" class="tool" onclick={onduplicate} disabled={count >= LIMITS.questions} aria-label="Salin soalan {index + 1}"><Icon name="copy" size={18} /></button>
			<button type="button" class="tool" onclick={() => (confirming = true)} aria-label="Padam soalan {index + 1}"><Icon name="trash" size={18} /></button>
		</div>
	</header>

	{#if confirming}
		<div class="confirm" role="alert">
			<p>Padam soalan {index + 1}?</p>
			<button type="button" class="btn btn--coral" onclick={onremove}>Ya, padam</button>
			<button type="button" class="btn btn--plain" onclick={() => (confirming = false)}>Batal</button>
		</div>
	{/if}

	{#if problem}<p class="problem">{problem}</p>{/if}

	<label class="field">
		<span>{question.type === 'truefalse' ? 'Kenyataan' : question.type === 'blank' ? 'Arahan' : 'Soalan'}</span>
		<textarea
			class="input"
			rows="2"
			bind:value={question.prompt}
			maxlength="300"
			placeholder={question.type === 'truefalse' ? 'Contoh: Penyu bertelur di pantai.' : question.type === 'blank' ? 'Contoh: Lengkapkan ayat ini.' : 'Contoh: Haiwan manakah yang mempunyai belalai?'}
			aria-invalid={!!err('prompt')}
		></textarea>
		{#if err('prompt')}<span class="field-error">{err('prompt')}</span>{/if}
	</label>

	<div class="extras">
		<ImageField bind:image={question.image} id={question.id} />
		<label class="time">
			<span>Masa menjawab</span>
			<select class="input" bind:value={question.time_limit}>
				{#each TIME_LIMITS as seconds (seconds)}<option value={seconds}>{seconds} saat</option>{/each}
			</select>
		</label>
	</div>

	<div class="kind">
		{#if question.type === 'single' || question.type === 'multiple'}
			<ChoicesEditor bind:choices={question.choices} multiple={question.type === 'multiple'} name="betul-{question.id}" {err} />
			{#if question.type === 'multiple'}
				<label class="check-row">
					<input type="checkbox" bind:checked={question.partial} />
					<span>Beri sebahagian markah jika sebahagian jawapan betul</span>
				</label>
			{/if}
		{:else if question.type === 'truefalse'}
			<fieldset class="tf">
				<legend>Jawapan yang betul</legend>
				<div class="tf-options">
					<button type="button" class="tf-option yes" aria-pressed={question.answer === true} onclick={() => question.type === 'truefalse' && (question.answer = true)}>
						<Icon name="check" /> Betul
					</button>
					<button type="button" class="tf-option no" aria-pressed={question.answer === false} onclick={() => question.type === 'truefalse' && (question.answer = false)}>
						<Icon name="close" /> Salah
					</button>
				</div>
			</fieldset>
		{:else if question.type === 'text'}
			<WordList
				bind:words={question.answers}
				legend="Jawapan yang diterima"
				placeholder="Contoh: hijau"
				addLabel="Tambah jawapan lain"
				max={LIMITS.answers}
				min={1}
				field="answers"
				{err}
			/>
			<label class="check-row">
				<input type="checkbox" bind:checked={question.forgive_typo} />
				<span>Terima ejaan yang hampir sama (contoh: "hijua" untuk "hijau")</span>
			</label>
		{:else if question.type === 'number'}
			<div class="number">
				<label class="field">
					<span>Jawapan</span>
					<input class="input" type="number" step="any" inputmode="decimal" bind:value={question.answer} aria-invalid={!!err('answer')} />
					{#if err('answer')}<span class="field-error">{err('answer')}</span>{/if}
				</label>
				<label class="field">
					<span>Julat diterima (±)</span>
					<input class="input" type="number" step="any" min="0" inputmode="decimal" bind:value={question.tolerance} aria-invalid={!!err('tolerance')} />
					{#if err('tolerance')}<span class="field-error">{err('tolerance')}</span>{/if}
				</label>
				<label class="field">
					<span>Unit (pilihan)</span>
					<input class="input" bind:value={question.unit} maxlength="16" placeholder="Contoh: kg" />
				</label>
			</div>
		{:else if question.type === 'order'}
			<OrderEditor bind:items={question.items} {err} />
		{:else if question.type === 'match'}
			<PairsEditor bind:pairs={question.pairs} {err} />
		{:else if question.type === 'blank'}
			<BlankEditor bind:sentence={question.sentence} bind:distractors={question.distractors} bind:wordBank={question.word_bank} id={question.id} {err} />
		{/if}
	</div>
</article>

<style>
	.question {
		display: grid;
		gap: 1rem;
		min-width: 0;
		padding: 1.1rem 1.2rem 1.3rem;
		border: 2px solid transparent;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
		scroll-margin-top: 1rem;
	}
	.question.has-problem,
	.question:has([aria-invalid='true']) {
		border-color: #f3c98f;
	}
	header {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.5rem 0.7rem;
	}
	h3 {
		display: contents;
	}
	.n {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.2rem;
		height: 2.2rem;
		border-radius: 50%;
		background: var(--ink);
		color: #fff;
		font: 600 1.05rem var(--font-display);
	}
	.type {
		position: relative;
		display: flex;
		align-items: center;
		gap: 0.4rem;
		min-width: 0;
		padding: 0 0.3rem 0 0.7rem;
		border: 2px solid var(--line);
		border-radius: var(--r-sm);
		background: var(--paper);
		color: var(--brand-deep);
	}
	.type select {
		min-width: 0;
		min-height: 2.6rem;
		padding: 0 0.4rem;
		border: 0;
		background: transparent;
		font-weight: 800;
		cursor: pointer;
	}
	.type select:focus-visible {
		outline: none;
	}
	.type:focus-within {
		border-color: var(--sky);
	}
	.tools {
		display: flex;
		margin-left: auto;
	}
	.confirm {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.6rem;
		padding: 0.7rem 0.9rem;
		border-radius: var(--r-md);
		background: #fde6e1;
	}
	.confirm p {
		margin-right: auto;
		font-weight: 800;
	}
	.problem {
		padding: 0.55rem 0.8rem;
		border-radius: var(--r-sm);
		background: var(--almost-soft);
		color: #7a3c00;
		font-weight: 800;
	}
	textarea {
		resize: vertical;
		min-height: 4.2rem;
	}
	.extras {
		display: flex;
		flex-wrap: wrap;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
	}
	.time {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		font-weight: 800;
		font-size: 0.95rem;
	}
	.time select {
		width: auto;
		min-height: 2.75rem;
		padding-block: 0.4rem;
	}
	.kind {
		display: grid;
		gap: 0.9rem;
		padding-top: 1rem;
		border-top: 2px solid var(--paper-2);
	}
	.tf {
		margin: 0;
		padding: 0;
		border: 0;
	}
	.tf legend {
		padding: 0;
		margin-bottom: 0.6rem;
		font-weight: 800;
		font-size: 0.95rem;
	}
	.tf-options {
		display: flex;
		gap: 0.6rem;
	}
	.tf-option {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
		min-height: 3rem;
		padding: 0.5rem 1.3rem;
		border: 2px solid var(--line);
		border-radius: var(--r-md);
		background: var(--card);
		font: 600 1.1rem var(--font-display);
		cursor: pointer;
		transition:
			background var(--t-state),
			border-color var(--t-state),
			color var(--t-state);
	}
	.tf-option.yes[aria-pressed='true'] {
		border-color: var(--good);
		background: var(--good);
		color: #fff;
	}
	.tf-option.no[aria-pressed='true'] {
		border-color: var(--coral);
		background: var(--coral);
		color: #fff;
	}
	.number {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 0.8rem;
	}
	@media (max-width: 560px) {
		.question {
			padding: 0.9rem 0.9rem 1.1rem;
		}
		.number {
			grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		}
	}
</style>
