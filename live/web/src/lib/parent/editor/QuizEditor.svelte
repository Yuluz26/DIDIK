<!--
	The quiz editor: the quiz's title and description, an outline to jump between questions, every
	question as its own card, and a row of the eight question types to add another. Saving sends the
	whole quiz; the server checks it and its Malay messages land beside the fields they are about.
-->
<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { ApiError, type FieldError } from '$lib/api';
	import Icon from '$ui/Icon.svelte';
	import QuestionEditor from './QuestionEditor.svelte';
	import TypeIcon from './TypeIcon.svelte';
	import { LIMITS, TYPES, blank, duplicate, type QuizDraft, type QuestionType } from './model';

	let {
		initial,
		quizId = null,
		readonly = false,
		onsave
	}: {
		initial: QuizDraft;
		quizId?: number | null;
		readonly?: boolean;
		onsave: (draft: QuizDraft) => Promise<void>;
	} = $props();

	// The editor owns its copy from here on; `initial` is only the starting point.
	// svelte-ignore state_referenced_locally
	let draft = $state<QuizDraft>(JSON.parse(JSON.stringify(initial)));
	// svelte-ignore state_referenced_locally
	let baseline = $state(JSON.stringify(initial));
	let errors = $state<FieldError[]>([]);
	let problem = $state('');
	let saving = $state(false);
	let savedAt = $state<Date | null>(null);

	const dirty = $derived(JSON.stringify(draft) !== baseline);
	const status = $derived(
		saving ? 'Menyimpan…' : dirty ? 'Ada perubahan belum disimpan.' : savedAt ? `Disimpan pada ${savedAt.toLocaleTimeString('ms-MY', { hour: '2-digit', minute: '2-digit' })}.` : quizId ? 'Semua perubahan disimpan.' : 'Belum disimpan.'
	);
	const flagged = $derived(new Set(errors.filter((e) => e.loc[0] === 'questions').map((e) => e.loc[1] as number)));

	function errorAt(...path: (string | number)[]): string | undefined {
		const key = path.join('.');
		return errors.find((e) => e.loc.join('.') === key)?.message;
	}

	async function add(type: QuestionType) {
		if (draft.questions.length >= LIMITS.questions) return;
		draft.questions.push(blank(type));
		await tick();
		const card = document.getElementById(`soalan-${draft.questions.length}`);
		card?.scrollIntoView({ behavior: 'smooth', block: 'start' });
		card?.querySelector('textarea')?.focus({ preventScroll: true });
	}

	function move(index: number, by: number) {
		const target = index + by;
		if (target < 0 || target >= draft.questions.length) return;
		const [question] = draft.questions.splice(index, 1);
		draft.questions.splice(target, 0, question);
		errors = [];
	}

	function copy(index: number) {
		draft.questions.splice(index + 1, 0, duplicate(draft.questions[index]));
		errors = [];
	}

	function remove(index: number) {
		draft.questions.splice(index, 1);
		errors = [];
	}

	async function save() {
		if (saving || readonly) return;
		saving = true;
		problem = '';
		try {
			const snapshot = JSON.stringify(draft);
			await onsave(JSON.parse(snapshot));
			baseline = snapshot;
			errors = [];
			savedAt = new Date();
		} catch (error) {
			if (error instanceof ApiError) {
				errors = error.errors;
				problem = error.errors.length ? `${error.errors.length} perkara perlu dibetulkan sebelum kuiz disimpan.` : error.message;
			} else {
				problem = 'Kuiz tidak dapat disimpan. Cuba lagi.';
			}
		}
		saving = false;
	}

	onMount(() => {
		const leave = (event: BeforeUnloadEvent) => {
			if (dirty) event.preventDefault();
		};
		const shortcut = (event: KeyboardEvent) => {
			if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
				event.preventDefault();
				void save();
			}
		};
		window.addEventListener('beforeunload', leave);
		window.addEventListener('keydown', shortcut);
		return () => {
			window.removeEventListener('beforeunload', leave);
			window.removeEventListener('keydown', shortcut);
		};
	});
</script>

{#snippet saveControls()}
	<p class="status" class:dirty aria-live="polite">{status}</p>
	<div class="save-actions">
		<button type="button" class="btn btn--sun" onclick={save} disabled={saving || readonly}>
			<Icon name="check" /> {saving ? 'Menyimpan…' : 'Simpan'}
		</button>
		{#if quizId && !dirty && draft.questions.length}
			<a class="btn btn--plain" href="/ibu-bapa/kuiz/{quizId}/main"><Icon name="play" /> Main bersama</a>
		{/if}
	</div>
{/snippet}

<div class="editor-wrap">
	<div class="toolbar">{@render saveControls()}</div>

	<div class="editor">
		<aside class="side">
			<section class="details">
				<label class="field">
					<span>Tajuk kuiz</span>
					<input class="input" bind:value={draft.title} maxlength="120" placeholder="Contoh: Haiwan di Malaysia" aria-invalid={!!errorAt('title')} disabled={readonly} />
					{#if errorAt('title')}<span class="field-error">{errorAt('title')}</span>{/if}
				</label>
				<label class="field">
					<span>Penerangan <small>(pilihan)</small></span>
					<textarea class="input" rows="2" bind:value={draft.description} maxlength="500" placeholder="Untuk siapa kuiz ini, atau apa yang dipelajari." disabled={readonly}></textarea>
				</label>
			</section>

			{#if draft.questions.length}
				<nav class="outline" aria-label="Senarai soalan">
					<h2>Soalan <span>{draft.questions.length}/{LIMITS.questions}</span></h2>
					<ol>
						{#each draft.questions as question, i (question.id)}
							<li class:flagged={flagged.has(i)}>
								<a href="#soalan-{i + 1}">
									<span class="n">{i + 1}</span>
									<TypeIcon type={question.type} size={18} />
									<span class="text">{question.prompt || question.type === 'blank' && question.sentence || 'Belum ditulis'}</span>
								</a>
							</li>
						{/each}
					</ol>
				</nav>
			{/if}

		</aside>

		<div class="main">
			{#if problem}
				<div class="summary" role="alert">
					<p>{problem}</p>
					{#if flagged.size}
						<p class="jump">
							Lihat soalan
							{#each [...flagged].sort((a, b) => a - b) as i (i)}<a href="#soalan-{i + 1}">{i + 1}</a>{/each}
						</p>
					{/if}
				</div>
			{/if}

			<fieldset class="questions" disabled={readonly}>
				<legend class="visually-hidden">Soalan-soalan</legend>
				{#each draft.questions as question, i (question.id)}
					<QuestionEditor
						bind:question={draft.questions[i]}
						index={i}
						count={draft.questions.length}
						err={(...path) => errorAt('questions', i, ...path)}
						onmove={(by) => move(i, by)}
						onduplicate={() => copy(i)}
						onremove={() => remove(i)}
					/>
				{/each}
			</fieldset>

			{#if !readonly}
				<section class="add" aria-labelledby="add-title">
					<h2 id="add-title">{draft.questions.length ? 'Tambah soalan' : 'Pilih jenis soalan pertama'}</h2>
					{#if draft.questions.length >= LIMITS.questions}
						<p class="help">Kuiz ini sudah ada {LIMITS.questions} soalan, iaitu had maksimum.</p>
					{:else}
						<div class="types">
							{#each TYPES as t (t.type)}
								<button type="button" class="type-card" onclick={() => add(t.type)}>
									<span class="icon"><TypeIcon type={t.type} /></span>
									<strong>{t.name}</strong>
									<small>{t.hint}</small>
								</button>
							{/each}
						</div>
					{/if}
				</section>
			{/if}
		</div>
	</div>
</div>

<style>
	.editor {
		display: grid;
		grid-template-columns: minmax(16rem, 21rem) minmax(0, 1fr);
		gap: 1.6rem;
		align-items: start;
	}
	/* The save controls stay in view: along the top on a laptop, along the bottom on a phone.
	   (They sit outside the grid because a grid item cannot stick outside its own row.) */
	.toolbar {
		position: sticky;
		top: 0;
		z-index: 30;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		gap: 0.4rem 1rem;
		margin-bottom: 1.2rem;
		padding: 0.6rem 0;
		border-bottom: 2px solid var(--line);
		background: var(--paper);
	}
	.side {
		position: sticky;
		top: 5.5rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
		max-height: calc(100dvh - 6.5rem);
	}
	.details {
		display: grid;
		gap: 0.8rem;
		padding: 1rem;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	.details small {
		color: var(--ink-3);
		font-weight: 700;
	}
	.details textarea {
		resize: vertical;
	}
	.outline {
		display: grid;
		grid-template-rows: auto minmax(0, 1fr);
		flex: 0 1 auto;
		gap: 0.5rem;
		min-height: 0;
	}
	.outline h2 {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		font-size: 1.1rem;
	}
	.outline h2 span {
		color: var(--ink-3);
		font: 700 0.85rem var(--font-body);
	}
	.outline ol {
		display: grid;
		align-content: start;
		gap: 0.15rem;
		margin: 0;
		padding: 0 0.2rem 0 0;
		overflow-y: auto;
		list-style: none;
	}
	.outline a {
		display: grid;
		grid-template-columns: 1.6rem auto minmax(0, 1fr);
		align-items: center;
		gap: 0.45rem;
		padding: 0.35rem 0.5rem;
		border-radius: var(--r-sm);
		color: var(--ink);
		text-decoration: none;
		font-weight: 700;
		font-size: 0.92rem;
	}
	.outline a:hover {
		background: var(--paper-2);
	}
	.outline .n {
		color: var(--ink-3);
		font: 600 0.95rem var(--font-display);
		text-align: right;
	}
	.outline :global(.type-icon) {
		color: var(--brand);
	}
	.outline .text {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.outline .flagged a {
		background: var(--almost-soft);
	}
	.status {
		color: var(--ink-2);
		font-size: 0.9rem;
	}
	.status.dirty {
		color: #8a4b00;
	}
	.save-actions {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.main {
		display: grid;
		gap: 1.2rem;
		min-width: 0;
	}
	.summary {
		display: grid;
		gap: 0.3rem;
		padding: 0.8rem 1rem;
		border-radius: var(--r-md);
		background: var(--almost-soft);
		color: #7a3c00;
		font-weight: 800;
	}
	.jump {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.4rem;
		font-weight: 700;
	}
	.jump a {
		display: grid;
		place-items: center;
		min-width: 1.9rem;
		height: 1.9rem;
		border-radius: 50%;
		background: #fff;
		color: inherit;
		font: 600 0.95rem var(--font-display);
		text-decoration: none;
	}
	.questions {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: 1.2rem;
		margin: 0;
		padding: 0;
		border: 0;
		min-width: 0;
	}
	.add {
		display: grid;
		gap: 0.8rem;
		padding-top: 0.4rem;
	}
	.add h2 {
		font-size: 1.25rem;
	}
	.types {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(11.5rem, 1fr));
		gap: 0.6rem;
	}
	.type-card {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr);
		grid-template-areas: 'icon name' 'icon hint';
		align-items: center;
		column-gap: 0.65rem;
		row-gap: 0.1rem;
		padding: 0.75rem 0.8rem;
		border: 2px solid var(--line);
		border-radius: var(--r-md);
		background: var(--card);
		text-align: left;
		cursor: pointer;
		transition:
			border-color var(--t-state),
			transform var(--t-press) var(--ease-out);
	}
	.type-card:hover {
		border-color: var(--brand);
		transform: translateY(-2px);
	}
	.type-card:active {
		transform: translateY(1px);
	}
	.type-card .icon {
		grid-area: icon;
		display: grid;
		place-items: center;
		width: 2.4rem;
		height: 2.4rem;
		border-radius: var(--r-sm);
		background: var(--brand-soft);
		color: var(--brand-deep);
	}
	.type-card strong {
		grid-area: name;
		font: 600 1rem var(--font-display);
	}
	.type-card small {
		grid-area: hint;
		color: var(--ink-2);
		font-size: 0.8rem;
		line-height: 1.3;
	}
	@media (max-width: 900px) {
		.editor {
			grid-template-columns: minmax(0, 1fr);
			padding-bottom: 6rem;
		}
		.side {
			position: static;
			max-height: none;
		}
		.outline {
			display: none;
		}
		.toolbar {
			position: fixed;
			inset: auto 0 0;
			margin: 0;
			padding: 0.7rem var(--gutter-r) calc(0.7rem + env(safe-area-inset-bottom, 0px)) var(--gutter);
			border-top: 2px solid var(--line);
			border-bottom: 0;
		}
	}
</style>
