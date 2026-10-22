<script lang="ts">
	import { goto } from '$app/navigation';
	import { session } from '$lib/session.svelte';
	import Logo from '$ui/Logo.svelte';

	async function logout() {
		await session.logout();
		await goto('/ibu-bapa');
	}
</script>

<header class="head">
	<div class="wrap inner">
		<Logo />
		{#if session.user}
			<nav aria-label="Akaun">
				<a href="/ibu-bapa">Kuiz saya</a>
				<span class="who">{session.user.name}</span>
				<button type="button" class="btn btn--plain" onclick={logout}>Log keluar</button>
			</nav>
		{/if}
	</div>
</header>

<style>
	.head {
		border-bottom: 2px solid var(--line);
		background: var(--paper);
	}
	.inner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		min-height: 4.2rem;
	}
	nav {
		display: flex;
		align-items: center;
		gap: 1rem;
		font-weight: 800;
	}
	nav a {
		color: var(--ink);
		text-decoration: none;
	}
	nav a:hover {
		color: var(--brand-ink);
	}
	.who {
		color: var(--ink-2);
	}
	@media (max-width: 560px) {
		.who {
			display: none;
		}
	}
</style>
