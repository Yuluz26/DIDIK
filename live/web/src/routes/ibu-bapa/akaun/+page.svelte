<!-- Akaun: who is signed in, the way to a new password, and signing out. -->
<script lang="ts">
	import { goto } from '$app/navigation';
	import { session } from '$lib/session.svelte';
	import DashShell from '$lib/parent/DashShell.svelte';
	import { parent } from '$lib/parent/store.svelte';
	import Kawaii from '$lib/parent/ui/Kawaii.svelte';
	import NmIcon from '$lib/parent/ui/NmIcon.svelte';

	async function logout() {
		await session.logout();
		parent.reset();
		await goto('/ibu-bapa');
	}

	function password() {
		session.emailHint = session.user?.email ?? '';
	}
</script>

<svelte:head><title>Akaun · DIDIK Main Bersama</title></svelte:head>

<DashShell>
	<div class="nm-head">
		<div>
			<h1>Akaun saya</h1>
			<p>Maklumat log masuk anda.</p>
		</div>
	</div>

	{#if session.user}
		<div class="cols">
			<section class="nm-card me">
				<span class="face"><Kawaii seed={session.user.email} size={92} mood="happy" /></span>
				<h2>{session.user.name}</h2>
				<p class="mail">{session.user.email}</p>
				{#if session.demo}<p class="demo">Akaun demo untuk mencuba di komputer sendiri.</p>{/if}
				<ul class="facts">
					<li><strong>{parent.mine.length}</strong><span>kuiz</span></li>
					<li><strong>{parent.totalQuestions}</strong><span>soalan</span></li>
					<li><strong>{parent.rooms.length}</strong><span>bilik dibuka</span></li>
				</ul>
			</section>

			<section class="nm-card actions">
				<h2>Tindakan</h2>
				<p>Pautan kata laluan baharu dihantar ke emel anda, sah selama satu jam.</p>
				<a class="btn btn--plain" href="/ibu-bapa/kata-laluan" onclick={password}><NmIcon name="link" size={16} /> Tukar kata laluan</a>
				<button type="button" class="btn btn--coral" onclick={logout}><NmIcon name="logout" size={16} /> Log keluar</button>
				<p class="note">Kanak-kanak tidak mempunyai akaun. Mereka hanya masuk bilik dengan nama samaran.</p>
			</section>
		</div>
	{/if}
</DashShell>

<style>
	.cols {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: clamp(1rem, 2vw, 1.6rem);
	}
	.me {
		display: grid;
		justify-items: center;
		gap: 0.5rem;
		padding: 2rem 1.5rem;
		text-align: center;
	}
	.face {
		display: grid;
		place-items: center;
		width: 7rem;
		height: 7rem;
		border-radius: 50%;
		background: #eceef5;
		box-shadow: var(--nm-in, inset 4px 4px 10px rgb(163 172 198 / 0.45), inset -4px -4px 10px rgb(255 255 255 / 0.95));
		line-height: 0;
	}
	h2 {
		font: 500 1.4rem/1.2 var(--font-display);
	}
	.mail {
		color: var(--ink-2);
		font-weight: 700;
		word-break: break-all;
	}
	.demo {
		padding: 0.3rem 0.8rem;
		border-radius: 999px;
		background: #fff0cc;
		color: #8a5a00;
		font: 600 0.82rem/1.2 var(--font-display);
	}
	.facts {
		display: flex;
		gap: 1.6rem;
		margin: 0.8rem 0 0;
		padding: 0;
		list-style: none;
	}
	.facts li {
		display: grid;
	}
	.facts strong {
		font: 300 2rem/1 var(--font-display);
	}
	.facts span {
		color: var(--ink-2);
		font-size: 0.82rem;
		font-weight: 700;
	}
	.actions {
		display: grid;
		align-content: start;
		justify-items: start;
		gap: 0.9rem;
		padding: 1.6rem 1.5rem;
	}
	.actions p {
		color: var(--ink-2);
	}
	.note {
		margin-top: 0.4rem;
		font-size: 0.9rem;
	}
	@media (max-width: 52rem) {
		.cols {
			grid-template-columns: minmax(0, 1fr);
		}
	}
</style>
