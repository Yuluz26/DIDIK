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
	import Kawaii from '$lib/parent/ui/Kawaii.svelte';
	import Logo from '$ui/Logo.svelte';
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
	<div class="nm-auth">
		<header class="auth-top">
			<Logo />
			<a class="back" href="/"><Icon name="back" size={18} /> Laman utama</a>
		</header>
		<main class="welcome">
			<section class="pitch">
				<p class="kind">Untuk ibu bapa dan guru</p>
				<h1>Tulis kuiz anda sendiri. Anak-anak main bersama.</h1>
				<p class="lead">Lapan jenis soalan, lapan permainan dan Legenda Story Mode, satu pautan untuk masuk. Tiada akaun untuk kanak-kanak, tiada iklan, percuma.</p>
				<ul class="points">
					<li><span class="dot"><Icon name="edit" /></span> Anda tulis setiap soalan. Tiada soalan dijana oleh AI.</li>
					<li><span class="dot"><Icon name="link" /></span> Kongsi pautan, kod QR atau kod 6 digit.</li>
					<li><span class="dot"><Icon name="heart" /></span> Nama panggilan sahaja; tiada sembang bebas.</li>
				</ul>
				<div class="friends" aria-hidden="true">
					<span class="f f1"><Kawaii seed="ibu" size={64} mood="happy" /></span>
					<span class="f f2"><Kawaii seed="cikgu" size={78} mood="wink" /></span>
					<span class="f f3"><Kawaii seed="anak" size={58} mood="wow" /></span>
				</div>
			</section>
			<SignIn />
		</main>
	</div>
{:else}
	<DashShell><Dashboard /></DashShell>
{/if}

<style>
	.loading {
		display: grid;
		place-items: center;
		min-height: 60vh;
	}
	/* Signed out: the same soft neumorphism as the dashboard. */
	.nm-auth {
		--nm-bg: #eceef4;
		--nm-out: 9px 9px 22px rgb(163 172 198 / 0.42), -9px -9px 22px rgb(255 255 255 / 0.95);
		--nm-out-sm: 5px 5px 13px rgb(163 172 198 / 0.4), -5px -5px 13px rgb(255 255 255 / 0.95);
		--nm-in: inset 4px 4px 10px rgb(163 172 198 / 0.45), inset -4px -4px 10px rgb(255 255 255 / 0.95);
		--nm-purple: #7c5ce8;
		--nm-ink: #2b2f45;
		--nm-ink-2: #6b7090;
		min-height: 100dvh;
		background:
			radial-gradient(60rem 30rem at 10% -10%, rgb(124 92 232 / 0.12), transparent 60%),
			radial-gradient(50rem 26rem at 110% 110%, rgb(242 63 117 / 0.1), transparent 60%),
			var(--nm-bg);
		color: var(--nm-ink);
		font-family: var(--font-body);
	}
	.auth-top {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		max-width: 72rem;
		margin: 0 auto;
		padding: 1.2rem var(--gutter, 1rem) 0;
	}
	.back {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		min-height: 2.75rem;
		padding: 0 1rem;
		border-radius: 999px;
		background: var(--nm-bg);
		box-shadow: var(--nm-out-sm);
		color: var(--nm-ink);
		font: 600 0.95rem var(--font-display);
		text-decoration: none;
	}
	.back:active {
		box-shadow: var(--nm-in);
	}
	.welcome {
		display: grid;
		grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
		gap: 3rem;
		align-items: center;
		max-width: 72rem;
		margin: 0 auto;
		padding: 2.5rem var(--gutter, 1rem) 4rem;
	}
	.kind {
		display: inline-block;
		padding: 0.35rem 0.9rem;
		border-radius: 999px;
		box-shadow: var(--nm-in);
		color: var(--nm-purple);
		font: 700 0.85rem var(--font-display);
	}
	.pitch h1 {
		margin: 0.9rem 0 1rem;
		font: 700 clamp(2rem, 1.4rem + 2.4vw, 3.1rem) / 1.08 var(--font-display);
		color: var(--nm-ink);
	}
	.lead {
		font-size: 1.08rem;
		color: var(--nm-ink-2);
		max-width: 34rem;
	}
	.points {
		display: grid;
		gap: 0.8rem;
		margin: 1.6rem 0 0;
		padding: 0;
		list-style: none;
		font-weight: 700;
	}
	.points li {
		display: flex;
		align-items: center;
		gap: 0.75rem;
	}
	.dot {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.4rem;
		height: 2.4rem;
		border-radius: 12px;
		background: var(--nm-bg);
		box-shadow: var(--nm-out-sm);
		color: var(--nm-purple);
	}
	.friends {
		display: flex;
		align-items: flex-end;
		gap: 0.9rem;
		margin-top: 2rem;
	}
	.f {
		display: grid;
		place-items: center;
		padding: 0.6rem;
		border-radius: 50%;
		background: var(--nm-bg);
		box-shadow: var(--nm-out);
		animation: bob 3.2s ease-in-out infinite;
	}
	.f2 {
		animation-delay: 0.5s;
	}
	.f3 {
		animation-delay: 1s;
	}
	@keyframes bob {
		50% {
			transform: translateY(-6px);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.f {
			animation: none;
		}
	}
	@media (max-width: 860px) {
		.welcome {
			grid-template-columns: minmax(0, 1fr);
			gap: 2rem;
			padding-block: 1.6rem 3rem;
		}
		.friends {
			display: none;
		}
	}
</style>
