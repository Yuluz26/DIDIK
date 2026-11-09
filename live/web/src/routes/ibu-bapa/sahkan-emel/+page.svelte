<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { session } from '$lib/session.svelte';
	let message = $state('Mengesahkan emel…');
	let done = $state(false);
	onMount(async () => {
		const token = location.hash.slice(1);
		if (!token) { message = 'Pautan pengesahan tidak lengkap.'; return; }
		try {
			const result = await api.post<{ message: string }>('/api/auth/verify-email', { token });
			history.replaceState(null, '', location.pathname);
			message = result.message; done = true; await session.load();
		} catch (problem) { message = problem instanceof Error ? problem.message : 'Pautan tidak dapat disahkan.'; }
	});
</script>
<svelte:head><title>Sahkan emel · DIDIK</title></svelte:head>
<main class="verify"><section><h1>{done ? 'Emel sudah disahkan' : 'Sahkan emel anda'}</h1><p role="status">{message}</p><a href="/ibu-bapa/akaun">Kembali ke akaun</a></section></main>
<style>.verify{min-height:80dvh;display:grid;place-items:center;padding:1.5rem;background:#eceef4;color:#2b2f45}.verify section{max-width:34rem;background:white;border-radius:16px;padding:2rem;box-shadow:8px 8px 25px #a3acc666}.verify h1{font:700 2rem var(--font-display)}.verify p{line-height:1.6}.verify a{color:#5840bd;font-weight:800}.verify a:focus-visible{outline:3px solid #dd4f88;outline-offset:3px}</style>
