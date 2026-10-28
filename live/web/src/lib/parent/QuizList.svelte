<!--
	Quizzes as soft rows: a little face, the title, what is in it, and what you can do with it. The
	parent's own quizzes can be edited, copied and deleted; the samples can be played or copied.
-->
<script lang="ts">
	import { TYPE_NAMES, parent, type QuizSummary } from './store.svelte';
	import Kawaii from './ui/Kawaii.svelte';
	import NmIcon from './ui/NmIcon.svelte';

	let { quizzes, sample = false }: { quizzes: QuizSummary[]; sample?: boolean } = $props();

	let deleting = $state<number | null>(null);
	let busy = $state<number | null>(null);

	async function copy(quiz: QuizSummary) {
		busy = quiz.id;
		try {
			await parent.copy(quiz);
		} finally {
			busy = null;
		}
	}

	async function remove(quiz: QuizSummary) {
		await parent.remove(quiz);
		deleting = null;
	}
</script>

<ul class="quizzes">
	{#each quizzes as quiz (quiz.id)}
		<li class="quiz nm-card">
			<span class="face"><Kawaii seed={quiz.title} size={52} /></span>
			<div class="info">
				<h3>
					{#if sample}{quiz.title}{:else}<a href="/ibu-bapa/kuiz/{quiz.id}">{quiz.title}</a>{/if}
				</h3>
				{#if quiz.description}<p class="desc">{quiz.description}</p>{/if}
				<p class="types">
					<span class="count">{quiz.questionCount} soalan</span>
					{#each Object.entries(quiz.types) as [type, n] (type)}<span class="chip">{TYPE_NAMES[type] ?? type} ×{n}</span>{/each}
				</p>
			</div>
			<div class="actions">
				<a class="btn btn--sun" href="/ibu-bapa/kuiz/{quiz.id}/main" aria-disabled={!quiz.questionCount}><NmIcon name="play" size={16} /> Main bersama</a>
				{#if sample}
					<button type="button" class="btn btn--plain" disabled={busy === quiz.id} onclick={() => copy(quiz)}><NmIcon name="copy" size={16} /> Salin dan ubah</button>
				{:else}
					<a class="btn btn--plain" href="/ibu-bapa/kuiz/{quiz.id}"><NmIcon name="edit" size={16} /> Sunting</a>
					<button type="button" class="btn btn--plain btn--icon" onclick={() => copy(quiz)} aria-label="Salin {quiz.title}"><NmIcon name="copy" size={18} /></button>
					{#if deleting === quiz.id}
						<span class="confirm">Padam kuiz ini?
							<button type="button" class="btn btn--coral" onclick={() => remove(quiz)}>Ya, padam</button>
							<button type="button" class="btn btn--plain" onclick={() => (deleting = null)}>Batal</button>
						</span>
					{:else}
						<button type="button" class="btn btn--plain btn--icon" onclick={() => (deleting = quiz.id)} aria-label="Padam {quiz.title}"><NmIcon name="trash" size={18} /></button>
					{/if}
				{/if}
			</div>
		</li>
	{/each}
</ul>

<style>
	.quizzes {
		display: grid;
		gap: 1.1rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.quiz {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 1rem 1.2rem;
		padding: 1rem 1.3rem;
	}
	.face {
		display: grid;
		place-items: center;
		flex: none;
		width: 3.7rem;
		height: 3.7rem;
		border-radius: 50%;
		background: #eceef5;
		box-shadow: inset 3px 3px 7px rgb(163 172 198 / 0.4), inset -3px -3px 7px rgb(255 255 255 / 0.95);
		line-height: 0;
	}
	.info {
		display: grid;
		gap: 0.3rem;
		flex: 1 1 18rem;
		min-width: 0;
	}
	h3 {
		font: 500 1.2rem/1.2 var(--font-display);
	}
	h3 a {
		color: var(--ink);
		text-decoration: none;
	}
	h3 a:hover {
		color: var(--brand-ink);
	}
	.desc {
		color: var(--ink-2);
		font-size: 0.95rem;
	}
	.types {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.35rem;
	}
	.count {
		margin-right: 0.3rem;
		font: 600 0.9rem/1 var(--font-display);
		color: var(--ink);
	}
	.actions {
		display: flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.6rem;
	}
	.confirm {
		display: inline-flex;
		align-items: center;
		flex-wrap: wrap;
		gap: 0.5rem;
		font: 600 0.95rem/1.1 var(--font-display);
	}
</style>
