<!-- Kuiz contoh: ready-made quizzes to play at once, or copy and change. -->
<script lang="ts">
	import DashShell from '$lib/parent/DashShell.svelte';
	import SampleLibrary from '$lib/parent/SampleLibrary.svelte';
	import { parent } from '$lib/parent/store.svelte';
</script>

<svelte:head><title>Perpustakaan DIDIK · Kuiz contoh</title></svelte:head>

<DashShell>
	<div class="nm-head">
		<div>
			<h1>Perpustakaan DIDIK</h1>
			<p>Selak buku soalan Pendidikan Islam, KAFA, KSSR dan menengah. Pilih, main bersama atau salin untuk diubah.</p>
		</div>
	</div>
	{#if parent.problem}<p role="alert">{parent.problem}</p>{/if}
	<SampleLibrary quizzes={parent.samples} />
</DashShell>
