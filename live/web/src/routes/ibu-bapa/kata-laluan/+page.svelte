<!--
	A new password for a parent who forgot theirs, in two steps on one page: ask for a link by email,
	then open the link and choose the password. The link's token comes after #, so it never reaches the
	server's logs; it is taken out of the address bar at once (a projected screen must not show it) and
	kept for this tab only, so a reload still works.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { afterNavigate, goto, replaceState } from '$app/navigation';
	import { api, ApiError } from '$lib/api';
	import { session, type Parent } from '$lib/session.svelte';
	import Didi from '$ui/Didi.svelte';
	import Icon from '$ui/Icon.svelte';
	import ParentHeader from '$lib/parent/ParentHeader.svelte';

	const KEPT = 'didik-live:reset-token';

	let step = $state<'ask' | 'sent' | 'checking' | 'choose' | 'gone'>('ask');
	let email = $state(session.emailHint);
	let account = $state('');
	let password = $state('');
	let show = $state(false);
	let busy = $state(false);
	let failure = $state<ApiError | null>(null);
	let notice = $state('');
	/** Why a link cannot be used: expired or used (the usual case), or it could not be checked. */
	let expired = $state(true);
	let token = '';

	function tabStorage(): Storage | null {
		try {
			return sessionStorage;
		} catch {
			return null;
		}
	}

	onMount(() => void session.load());
	// After the router has started (replaceState cannot run while the page is still hydrating), and
	// again whenever a link is opened in a tab that already shows this page.
	afterNavigate(() => void openLink());

	async function openLink() {
		const fresh = location.hash.slice(1);
		if (fresh) {
			tabStorage()?.setItem(KEPT, fresh);
			replaceState(location.pathname, {});
		}
		const link = fresh || tabStorage()?.getItem(KEPT) || '';
		if (!link || link === token) return;
		token = link;
		failure = null;
		step = 'checking';
		try {
			account = (await api.post<{ email: string }>('/api/auth/reset/check', { token })).email;
			password = '';
			step = 'choose';
		} catch (error) {
			refuse(error);
		}
	}

	function refuse(error: unknown) {
		expired = error instanceof ApiError && error.status === 410;
		notice = error instanceof ApiError ? error.message : 'Pautan ini tidak dapat disemak. Cuba lagi.';
		tabStorage()?.removeItem(KEPT);
		step = 'gone';
	}

	async function ask(event: Event) {
		event.preventDefault();
		busy = true;
		failure = null;
		try {
			notice = (await api.post<{ message: string }>('/api/auth/forgot', { email })).message;
			step = 'sent';
		} catch (error) {
			failure = error instanceof ApiError ? error : new ApiError(0, 'Sesuatu tidak kena. Cuba lagi.');
		} finally {
			busy = false;
		}
	}

	async function choose(event: Event) {
		event.preventDefault();
		busy = true;
		failure = null;
		try {
			const data = await api.post<{ user: Parent }>('/api/auth/reset', { token, password });
			tabStorage()?.removeItem(KEPT);
			session.user = data.user;
			await goto('/ibu-bapa');
		} catch (error) {
			if (error instanceof ApiError && error.status === 410) {
				refuse(error);
			} else {
				failure = error instanceof ApiError ? error : new ApiError(0, 'Sesuatu tidak kena. Cuba lagi.');
			}
		} finally {
			busy = false;
		}
	}

	function again() {
		failure = null;
		notice = '';
		step = 'ask';
	}
</script>

<svelte:head><title>Kata laluan · DIDIK Main Bersama</title></svelte:head>
<svelte:window onhashchange={() => location.hash.length > 1 && openLink()} />

<ParentHeader />

<main class="wrap reset">
	{#if step === 'checking'}
		<div class="checking" aria-busy="true">
			<Didi mood="think" size={96} />
			<p>Menyemak pautan…</p>
		</div>
	{:else if step === 'choose'}
		<p class="kind">Akaun ibu bapa</p>
		<h1>Pilih kata laluan baharu</h1>
		<p class="lead">Untuk <strong>{account}</strong>.</p>
		<form class="card form" onsubmit={choose} novalidate>
			{#if failure && !failure.errors.length}<p class="alert" role="alert">{failure.message}</p>{/if}
			<input class="username" type="email" name="username" autocomplete="username" value={account} readonly tabindex="-1" aria-hidden="true" />
			<label class="field">
				<span>Kata laluan baharu</span>
				<!-- svelte-ignore a11y_autofocus -->
				<input class="input" type={show ? 'text' : 'password'} bind:value={password} autocomplete="new-password" aria-invalid={!!failure?.at('password')} required autofocus />
				{#if failure?.at('password')}<span class="field-error">{failure.at('password')}</span>
				{:else}<span class="help">Sekurang-kurangnya 8 aksara.</span>{/if}
			</label>
			<label class="check-row"><input type="checkbox" bind:checked={show} /> Tunjuk kata laluan</label>
			<button class="btn btn--big" disabled={busy}>{busy ? 'Sebentar…' : 'Simpan'} <Icon name="next" /></button>
		</form>
		<p class="after">Selepas disimpan, anda terus log masuk di sini dan peranti lain dilog keluar.</p>
	{:else if step === 'gone'}
		<p class="kind">Akaun ibu bapa</p>
		{#if expired}
			<h1>Pautan ini sudah tidak sah</h1>
			<p class="lead">Pautan untuk menetapkan kata laluan sah selama satu jam dan boleh digunakan sekali sahaja.</p>
		{:else}
			<h1>Pautan ini tidak dapat disemak</h1>
			<p class="lead">{notice}</p>
		{/if}
		<button type="button" class="btn btn--big" onclick={again}>Minta pautan baharu <Icon name="next" /></button>
	{:else if step === 'sent'}
		<p class="kind">Akaun ibu bapa</p>
		<h1>Semak emel anda</h1>
		<p class="lead">{notice}</p>
		{#if !session.mail}
			<p class="server-note">
				Pelayan ini belum disambungkan ke emel, jadi pautan itu ditulis dalam log pelayan. Orang yang menjalankan laman ini juga
				boleh mencetak pautan dengan arahan <code>didik-live --reset-link {email || 'emel-anda'}</code>.
			</p>
		{/if}
		<p class="after">Tiada emel selepas beberapa minit? Semak folder spam, atau <button type="button" class="link" onclick={again}>cuba sekali lagi</button>.</p>
	{:else}
		<p class="kind">Akaun ibu bapa</p>
		<h1>Lupa kata laluan?</h1>
		<p class="lead">Tulis emel akaun anda. Kami hantar pautan untuk memilih kata laluan baharu.</p>
		<form class="card form" onsubmit={ask} novalidate>
			{#if failure && !failure.errors.length}<p class="alert" role="alert">{failure.message}</p>{/if}
			<label class="field">
				<span>Emel</span>
				<input class="input" type="email" bind:value={email} autocomplete="email" aria-invalid={!!failure?.at('email')} required />
				{#if failure?.at('email')}<span class="field-error">{failure.at('email')}</span>{/if}
			</label>
			<button class="btn btn--big" disabled={busy}>{busy ? 'Sebentar…' : 'Hantar pautan'} <Icon name="next" /></button>
		</form>
		<a class="back" href="/ibu-bapa"><Icon name="back" size={18} /> Kembali ke log masuk</a>
	{/if}
</main>

<style>
	.reset {
		display: grid;
		align-content: start;
		gap: 1rem;
		max-width: 34rem;
		padding-block: 3.5rem 5rem;
	}
	h1 {
		font-size: var(--fs-h1);
	}
	.lead {
		color: var(--ink-2);
		font-size: var(--fs-lead);
	}
	.lead strong {
		color: var(--ink);
		overflow-wrap: anywhere;
	}
	.form {
		display: grid;
		gap: 1rem;
		margin-top: 0.6rem;
		padding: 1.4rem;
	}
	.username {
		position: absolute;
		width: 1px;
		height: 1px;
		opacity: 0;
		pointer-events: none;
	}
	.alert {
		padding: 0.7rem 1rem;
		border-radius: var(--r-md);
		background: var(--almost-soft);
		color: #7a3d00;
		font-weight: 800;
	}
	.after {
		color: var(--ink-2);
	}
	.server-note {
		padding: 1rem 1.1rem;
		border-radius: var(--r-md);
		background: var(--paper-2);
		color: var(--ink-2);
	}
	code {
		font-size: 0.88rem;
		overflow-wrap: anywhere;
	}
	.link {
		border: 0;
		padding: 0;
		background: none;
		color: var(--brand-ink);
		font: inherit;
		font-weight: 800;
		text-decoration: underline;
		text-underline-offset: 3px;
		cursor: pointer;
	}
	.back {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		width: fit-content;
		margin-top: 0.4rem;
		font-weight: 800;
		text-decoration: none;
	}
	.checking {
		display: grid;
		justify-items: center;
		gap: 0.6rem;
		padding-block: 3rem;
		font-weight: 800;
	}
	.btn--big {
		justify-self: start;
	}
	.form .btn--big {
		justify-self: stretch;
	}
</style>
