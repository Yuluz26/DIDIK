<!--
	The parent area: signed out, the welcome and sign-in; signed in, the dashboard (lib/parent/Dashboard.svelte).
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { session } from '$lib/session.svelte';
	import Didi from '$ui/Didi.svelte';
	import Icon from '$ui/Icon.svelte';
	import DashShell from '$lib/parent/DashShell.svelte';
	import Dashboard from '$lib/parent/Dashboard.svelte';
	import ParentHeader from '$lib/parent/ParentHeader.svelte';
	import SignIn from '$lib/parent/SignIn.svelte';

	onMount(() => {
		void session.load();
	});
</script>

<svelte:head><title>Papan pemuka · DIDIK Main Bersama</title></svelte:head>

{#if !session.loaded}
	<ParentHeader />
	<main class="wrap loading" aria-busy="true"><Didi mood="think" size={110} /></main>
{:else if !session.user}
	<ParentHeader />
	<main class="wrap welcome">
		<section class="pitch">
			<p class="kind">Untuk ibu bapa dan guru</p>
			<h1>Tulis kuiz anda sendiri. Anak-anak main bersama.</h1>
			<p class="lead">Lapan jenis soalan, lapan permainan dan Legenda Story Mode, satu pautan untuk masuk. Tiada akaun untuk kanak-kanak, tiada iklan, percuma.</p>
			<ul class="points">
				<li><Icon name="edit" /> Anda tulis setiap soalan. Tiada soalan dijana oleh AI.</li>
				<li><Icon name="link" /> Kongsi pautan, kod QR atau kod 6 digit.</li>
				<li><Icon name="heart" /> Nama samaran sahaja; tiada sembang bebas.</li>
			</ul>
		</section>
		<SignIn />
	</main>
{:else}
	<DashShell><Dashboard /></DashShell>
{/if}

<style>
	.loading {
		display: grid;
		place-items: center;
		min-height: 60vh;
	}
	.welcome {
		display: grid;
		grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
		gap: 3rem;
		align-items: center;
		padding-block: 3rem 4rem;
	}
	.pitch h1 {
		margin: 0.6rem 0 1rem;
		font-size: var(--fs-h1);
	}
	.lead {
		font-size: var(--fs-lead);
		color: var(--ink-2);
	}
	.points {
		display: grid;
		gap: 0.7rem;
		margin: 1.6rem 0 0;
		padding: 0;
		list-style: none;
		font-weight: 700;
	}
	.points li {
		display: flex;
		align-items: center;
		gap: 0.6rem;
	}
	.points :global(.icon) {
		color: var(--brand-ink);
	}
	@media (max-width: 860px) {
		.welcome {
			grid-template-columns: minmax(0, 1fr);
			gap: 2rem;
			padding-block: 2rem;
		}
	}
</style>
