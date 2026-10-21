<!-- Sign in or create a parent account. Errors appear under the field they belong to. -->
<script lang="ts">
	import { ApiError } from '$lib/api';
	import { session } from '$lib/session.svelte';
	import Icon from '$ui/Icon.svelte';

	let mode = $state<'login' | 'register'>('login');
	let name = $state('');
	let email = $state('');
	let password = $state('');
	let busy = $state(false);
	let failure = $state<ApiError | null>(null);

	async function submit(event: Event) {
		event.preventDefault();
		busy = true;
		failure = null;
		try {
			if (mode === 'login') await session.login(email, password);
			else await session.register(name, email, password);
		} catch (error) {
			failure = error instanceof ApiError ? error : new ApiError(0, 'Sesuatu tidak kena. Cuba lagi.');
		} finally {
			busy = false;
		}
	}

	function useDemo() {
		mode = 'login';
		email = 'demo@didik.test';
		password = 'main-bersama';
	}
</script>

<div class="signin card">
	<div class="tabs" role="tablist" aria-label="Akaun">
		<button type="button" role="tab" aria-selected={mode === 'login'} class:on={mode === 'login'} onclick={() => (mode = 'login')}>Log masuk</button>
		<button type="button" role="tab" aria-selected={mode === 'register'} class:on={mode === 'register'} onclick={() => (mode = 'register')}>Daftar percuma</button>
	</div>

	<form onsubmit={submit} novalidate>
		{#if failure && !failure.errors.length}<p class="alert" role="alert">{failure.message}</p>{/if}

		{#if mode === 'register'}
			<label class="field">
				<span>Nama anda</span>
				<input class="input" bind:value={name} autocomplete="name" aria-invalid={!!failure?.at('name')} required />
				{#if failure?.at('name')}<span class="field-error">{failure.at('name')}</span>{/if}
			</label>
		{/if}
		<label class="field">
			<span>Emel</span>
			<input class="input" type="email" bind:value={email} autocomplete="email" aria-invalid={!!failure?.at('email')} required />
			{#if failure?.at('email')}<span class="field-error">{failure.at('email')}</span>{/if}
		</label>
		<label class="field">
			<span>Kata laluan</span>
			<input class="input" type="password" bind:value={password} autocomplete={mode === 'login' ? 'current-password' : 'new-password'} aria-invalid={!!failure?.at('password')} required />
			{#if failure?.at('password')}<span class="field-error">{failure.at('password')}</span>
			{:else if mode === 'register'}<span class="help">Sekurang-kurangnya 8 aksara.</span>{/if}
		</label>

		<button class="btn btn--big" disabled={busy}>
			{busy ? 'Sebentar…' : mode === 'login' ? 'Log masuk' : 'Cipta akaun'} <Icon name="next" />
		</button>
	</form>

	{#if session.demo}
		<p class="demo">
			Mencuba di komputer sendiri? <button type="button" class="link" onclick={useDemo}>Guna akaun demo</button>
			(<code>demo@didik.test</code> / <code>main-bersama</code>).
		</p>
	{/if}
</div>

<style>
	.signin {
		display: grid;
		gap: 1.2rem;
		padding: 1.4rem;
	}
	.tabs {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.3rem;
		padding: 0.3rem;
		border-radius: var(--r-md);
		background: var(--paper-2);
	}
	.tabs button {
		min-height: 2.8rem;
		border: 0;
		border-radius: var(--r-sm);
		background: transparent;
		font: 600 1.05rem var(--font-display);
		cursor: pointer;
	}
	.tabs .on {
		background: var(--card);
		box-shadow: 0 2px 0 var(--line);
	}
	form {
		display: grid;
		gap: 1rem;
	}
	.alert {
		padding: 0.7rem 1rem;
		border-radius: var(--r-md);
		background: var(--almost-soft);
		color: #7a3d00;
		font-weight: 800;
	}
	.demo {
		color: var(--ink-2);
		font-size: 0.92rem;
	}
	.link {
		border: 0;
		padding: 0;
		background: none;
		color: var(--brand);
		font-weight: 800;
		text-decoration: underline;
		text-underline-offset: 3px;
		cursor: pointer;
	}
	code {
		font-size: 0.85rem;
	}
</style>
