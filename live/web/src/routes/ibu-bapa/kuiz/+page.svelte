<!-- Kuiz saya: every quiz the parent has written, to play, edit, copy or delete. -->
<script lang="ts">
	import DashShell from '$lib/parent/DashShell.svelte';
	import QuizList from '$lib/parent/QuizList.svelte';
	import NmIcon from '$lib/parent/ui/NmIcon.svelte';
	import Kawaii from '$lib/parent/ui/Kawaii.svelte';
	import { parent } from '$lib/parent/store.svelte';
</script>

<svelte:head><title>Kuiz saya · DIDIK Main Bersama</title></svelte:head>

<DashShell>
	<div class="nm-head">
		<div>
			<h1>Kuiz saya</h1>
			<p>{parent.mine.length} kuiz · {parent.totalQuestions} soalan semuanya</p>
		</div>
		<a class="btn btn--sun" href="/ibu-bapa/kuiz/baru"><NmIcon name="plus" size={18} /> Kuiz baharu</a>
	</div>
	{#if parent.problem}<p class="problem" role="alert">{parent.problem}</p>{/if}
	{#if !parent.loading && !parent.mine.length}
		<div class="empty nm-card">
			<Kawaii seed="kuiz" size={84} mood="wow" />
			<div>
				<h2>Belum ada kuiz anda sendiri</h2>
				<p>Mulakan dengan kuiz kosong, atau salin satu contoh dan ubah ikut anak anda.</p>
				<p class="row">
					<a class="btn btn--sun" href="/ibu-bapa/kuiz/baru"><NmIcon name="plus" size={18} /> Kuiz baharu</a>
					<a class="btn btn--plain" href="/ibu-bapa/contoh"><NmIcon name="sparkle" size={18} /> Lihat contoh</a>
				</p>
			</div>
		</div>
	{/if}
	<QuizList quizzes={parent.mine} />
</DashShell>

<style>
	.problem {
		margin-bottom: 1rem;
		color: #b04a00;
		font-weight: 800;
	}
	.empty {
		display: flex;
		align-items: center;
		gap: 1.6rem;
		padding: 1.6rem 1.8rem;
		margin-bottom: 1.2rem;
	}
	.empty h2 {
		font: 500 1.4rem/1.2 var(--font-display);
	}
	.empty p {
		margin-top: 0.3rem;
		color: var(--ink-2);
	}
	.row {
		display: flex;
		flex-wrap: wrap;
		gap: 0.6rem;
		margin-top: 1rem !important;
	}
	@media (max-width: 560px) {
		.empty {
			flex-direction: column;
			text-align: center;
		}
		.row {
			justify-content: center;
		}
	}
</style>
