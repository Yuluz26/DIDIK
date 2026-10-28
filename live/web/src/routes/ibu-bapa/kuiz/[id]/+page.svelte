<!-- Editing a quiz. A sample quiz opens read-only, with a button to copy it into "Kuiz saya". -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { api, ApiError } from '$lib/api';
	import { session } from '$lib/session.svelte';
	import DashShell from '$lib/parent/DashShell.svelte';
	import Kawaii from '$lib/parent/ui/Kawaii.svelte';
	import NmIcon from '$lib/parent/ui/NmIcon.svelte';
	import QuizEditor from '$lib/parent/editor/QuizEditor.svelte';
	import { normalise, type QuizDraft } from '$lib/parent/editor/model';

	interface QuizOut {
		id: number;
		title: string;
		description: string;
		questions: Record<string, unknown>[];
		canEdit: boolean;
		isSample: boolean;
	}

	const id = $derived(Number(page.params.id));
	let quiz = $state<QuizOut | null>(null);
	let initial = $state<QuizDraft | null>(null);
	let problem = $state('');

	async function load(quizId: number) {
		quiz = null;
		initial = null;
		problem = '';
		try {
			const data = await api.get<QuizOut>(`/api/quizzes/${quizId}`);
			quiz = data;
			initial = { title: data.title, description: data.description, questions: data.questions.map(normalise) };
		} catch (error) {
			problem = error instanceof ApiError ? error.message : 'Kuiz tidak dapat dibuka.';
		}
	}

	onMount(async () => {
		if (!(await session.load())) await goto('/ibu-bapa');
	});

	$effect(() => {
		if (session.user && id) void load(id);
	});

	async function save(draft: QuizDraft) {
		await api.put(`/api/quizzes/${id}`, draft);
	}

	async function copy() {
		const copied = await api.post<{ id: number }>(`/api/quizzes/${id}/copy`);
		await goto(`/ibu-bapa/kuiz/${copied.id}`);
	}
</script>

<svelte:head><title>{quiz?.title || 'Sunting kuiz'} · DIDIK Main Bersama</title></svelte:head>

<DashShell>
	<div class="nm-head">
		<div>
			<a class="back" href="/ibu-bapa/kuiz"><NmIcon name="back" size={16} /> Kuiz saya</a>
			<h1>{quiz?.canEdit === false ? 'Kuiz contoh' : 'Sunting kuiz'}</h1>
		</div>
	</div>
	{#if problem}
		<div class="missing nm-card">
			<Kawaii seed="hilang" size={90} mood="sleepy" />
			<p>{problem}</p>
			<a class="btn btn--plain" href="/ibu-bapa/kuiz">Kembali ke Kuiz saya</a>
		</div>
	{:else if quiz && initial}
		{#if !quiz.canEdit}
			<div class="sample">
				<p>Ini kuiz contoh. Salin ke kuiz anda untuk mengubah soalannya.</p>
				<button type="button" class="btn btn--sun" onclick={copy}><NmIcon name="copy" size={16} /> Salin dan ubah</button>
			</div>
		{/if}
		{#key quiz.id}
			<QuizEditor {initial} quizId={quiz.id} readonly={!quiz.canEdit} onsave={save} />
		{/key}
	{:else}
		<div class="loading" aria-busy="true"><Kawaii seed="muat" size={90} mood="wow" /></div>
	{/if}
</DashShell>

<style>
	.back {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		margin-bottom: 0.4rem;
		color: var(--ink-2);
		font: 600 0.9rem/1 var(--font-display);
		text-decoration: none;
	}
	.back:hover {
		color: var(--brand-ink);
	}
	.sample {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		gap: 0.8rem;
		margin-bottom: 1rem;
		padding: 0.9rem 1.2rem;
		border-radius: 1.3rem;
		background: #fff3d6;
		box-shadow: 4px 4px 10px rgb(200 170 100 / 0.25), -4px -4px 10px rgb(255 255 255 / 0.9);
		font-weight: 800;
	}
	.missing,
	.loading {
		display: grid;
		justify-items: center;
		gap: 0.8rem;
		padding: 3rem 1rem;
		text-align: center;
		font-weight: 700;
	}
</style>
