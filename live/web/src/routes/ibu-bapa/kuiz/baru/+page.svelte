<!-- A new quiz: starts with one empty question of the most common type. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { api } from '$lib/api';
	import { session } from '$lib/session.svelte';
	import Icon from '$ui/Icon.svelte';
	import ParentHeader from '$lib/parent/ParentHeader.svelte';
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

<ParentHeader />

<main class="wrap page">
	<div class="top">
		<a class="back" href="/ibu-bapa"><Icon name="back" size={18} /> Kuiz saya</a>
		<h1>Kuiz baharu</h1>
	</div>
	{#if ready}<QuizEditor {initial} onsave={create} />{/if}
</main>

<style>
	.page {
		display: grid;
		gap: 1.2rem;
		padding-block: 1.4rem 3rem;
	}
	.top {
		display: grid;
		gap: 0.4rem;
	}
	.back {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		justify-self: start;
		font-weight: 800;
		text-decoration: none;
	}
	h1 {
		font-size: var(--fs-h1);
	}
</style>
