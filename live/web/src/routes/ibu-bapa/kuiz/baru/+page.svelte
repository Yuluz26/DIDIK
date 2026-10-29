<!-- A new quiz: starts with one empty question of the most common type. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { session } from '$lib/session.svelte';
	import DashShell from '$lib/parent/DashShell.svelte';
	import NmIcon from '$lib/parent/ui/NmIcon.svelte';
	import QuizEditor from '$lib/parent/editor/QuizEditor.svelte';
	import { blank, type QuizDraft } from '$lib/parent/editor/model';

	let ready = $state(false);
	const initial: QuizDraft = { title: '', description: '', questions: [blank('single')] };

	onMount(async () => {
		if (!(await session.load())) await goto('/ibu-bapa');
		else ready = true;
	});

	async function create(draft: QuizDraft) {
		const quiz = await api.post<{ id: number }>('/api/quizzes', draft);
		await goto(`/ibu-bapa/kuiz/${quiz.id}`, { replaceState: true });
	}
</script>

<svelte:head><title>Kuiz baharu · DIDIK Main Bersama</title></svelte:head>

<DashShell>
	<div class="nm-head">
		<div>
			<a class="back" href="/ibu-bapa/kuiz"><NmIcon name="back" size={16} /> Kuiz saya</a>
			<h1>Kuiz baharu</h1>
		</div>
	</div>
	{#if ready}<QuizEditor {initial} onsave={create} />{/if}
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
</style>
