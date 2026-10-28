<!-- Kuiz contoh: ready-made quizzes to play at once, or copy and change. -->
<script lang="ts">
	import DashShell from '$lib/parent/DashShell.svelte';
	import QuizList from '$lib/parent/QuizList.svelte';
	import { parent } from '$lib/parent/store.svelte';
</script>

<svelte:head><title>Kuiz contoh · DIDIK Main Bersama</title></svelte:head>

<DashShell>
	<div class="nm-head">
		<div>
			<h1>Kuiz contoh</h1>
			<p>Sedia untuk dimainkan. Salin untuk mengubah soalannya.</p>
		</div>
	</div>
	{#if parent.problem}<p role="alert">{parent.problem}</p>{/if}
	<QuizList quizzes={parent.samples} sample />
</DashShell>
