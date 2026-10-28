<!--
	Sign in or create a parent account, in the dashboard's soft neumorphism: an inset tab track with a
	raised pill, inset input wells, a raised button that shows it is working. Errors appear under the
	field they belong to and are announced.
-->
<script lang="ts">
	import { ApiError } from '$lib/api';
	import { session } from '$lib/session.svelte';
	import Icon from '$ui/Icon.svelte';
	import Kawaii from './ui/Kawaii.svelte';

	let mode = $state<'login' | 'register'>('login');
	let name = $state('');
	let email = $state('');
	let password = $state('');
	let busy = $state(false);
	let showPassword = $state(false);
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

	function switchTo(next: 'login' | 'register') {
		mode = next;
		failure = null;
	}

	function useDemo() {
		switchTo('login');
		email = 'demo@didik.test';
		password = 'main-bersama';
	}
</script>

<div class="signin">
	<div class="hello">
		<span class="wave" aria-hidden="true"><Kawaii seed={mode === 'login' ? 'masuk' : 'daftar'} size={52} mood={mode === 'login' ? 'happy' : 'wow'} /></span>
		<div>
			<h2>{mode === 'login' ? 'Selamat kembali!' : 'Jom mula!'}</h2>
			<p>{mode === 'login' ? 'Log masuk untuk menulis dan membuka kuiz.' : 'Akaun percuma, siap dalam seminit.'}</p>
		</div>
	</div>

	<div class="tabs" role="tablist" aria-label="Akaun">
		<span class="pill" class:right={mode === 'register'} aria-hidden="true"></span>
		<button type="button" role="tab" aria-selected={mode === 'login'} class:on={mode === 'login'} onclick={() => switchTo('login')}>Log masuk</button>
		<button type="button" role="tab" aria-selected={mode === 'register'} class:on={mode === 'register'} onclick={() => switchTo('register')}>Daftar percuma</button>
	</div>

	<form onsubmit={submit} novalidate aria-busy={busy}>
		{#if failure && !failure.errors.length}<p class="alert" role="alert">{failure.message}</p>{/if}

		{#if mode === 'register'}
			<div class="field">
				<label for="signin-name">Nama anda</label>
				<div class="well">
					<Icon name="users" size={18} />
					<input id="signin-name" bind:value={name} autocomplete="name" aria-invalid={!!failure?.at('name')} aria-describedby={failure?.at('name') ? 'signin-name-error' : undefined} required />
				</div>
				{#if failure?.at('name')}<span class="field-error" id="signin-name-error" role="alert">{failure.at('name')}</span>{/if}
			</div>
		{/if}
		<div class="field">
			<label for="signin-email">Emel</label>
			<div class="well">
				<Icon name="share" size={18} />
				<input
					id="signin-email"
					type="email"
					inputmode="email"
					bind:value={email}
					autocomplete="email"
					aria-invalid={!!failure?.at('email')}
					aria-describedby={failure?.at('email') ? 'signin-email-error' : undefined}
					required
				/>
			</div>
			{#if failure?.at('email')}<span class="field-error" id="signin-email-error" role="alert">{failure.at('email')}</span>{/if}
		</div>
		<div class="field">
			<label for="signin-password">Kata laluan</label>
			<div class="well">
				<Icon name="lock" size={18} />
				<input
					id="signin-password"
					type={showPassword ? 'text' : 'password'}
					bind:value={password}
					autocomplete={mode === 'login' ? 'current-password' : 'new-password'}
					aria-invalid={!!failure?.at('password')}
					aria-describedby={failure?.at('password') ? 'signin-password-error' : mode === 'register' ? 'signin-password-help' : undefined}
					required
				/>
				<button
					type="button"
					class="peek"
					onclick={() => (showPassword = !showPassword)}
					aria-pressed={showPassword}
					aria-label={showPassword ? 'Sembunyikan kata laluan' : 'Tunjuk kata laluan'}
				>
					<Icon name="eye" size={18} />
				</button>
			</div>
			{#if failure?.at('password')}<span class="field-error" id="signin-password-error" role="alert">{failure.at('password')}</span>
			{:else if mode === 'register'}<span class="help" id="signin-password-help">Sekurang-kurangnya 8 aksara.</span>{/if}
		</div>
		{#if mode === 'login'}
			<a class="forgot" href="/ibu-bapa/kata-laluan" onclick={() => (session.emailHint = email)}>Lupa kata laluan?</a>
		{/if}

		<button class="go" disabled={busy}>
			{#if busy}<span class="spinner" aria-hidden="true"></span> Sebentar…{:else}{mode === 'login' ? 'Log masuk' : 'Cipta akaun'} <Icon name="next" />{/if}
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
		gap: 1.3rem;
		padding: 1.8rem;
		border-radius: 28px;
		background: var(--nm-bg, #eceef4);
		box-shadow: var(--nm-out);
		color: var(--nm-ink, #2b2f45);
	}
	.hello {
		display: flex;
		align-items: center;
		gap: 0.9rem;
	}
	.wave {
		display: grid;
		place-items: center;
		padding: 0.45rem;
		border-radius: 50%;
		box-shadow: var(--nm-out-sm);
	}
	.hello h2 {
		font: 700 1.5rem/1.1 var(--font-display);
	}
	.hello p {
		color: var(--nm-ink-2, #6b7090);
		font-size: 0.95rem;
	}
	.tabs {
		position: relative;
		display: grid;
		grid-template-columns: 1fr 1fr;
		padding: 0.35rem;
		border-radius: 999px;
		box-shadow: var(--nm-in);
	}
	.pill {
		position: absolute;
		inset: 0.35rem auto 0.35rem 0.35rem;
		width: calc(50% - 0.35rem);
		border-radius: 999px;
		background: linear-gradient(145deg, #f7f8fc, #e6e8f0);
		box-shadow: var(--nm-out-sm);
		transition: transform 280ms cubic-bezier(0.3, 1.3, 0.5, 1);
	}
	.pill.right {
		transform: translateX(100%);
	}
	.tabs button {
		position: relative;
		min-height: 2.9rem;
		border: 0;
		border-radius: 999px;
		background: transparent;
		color: var(--nm-ink-2, #6b7090);
		font: 600 1.02rem var(--font-display);
		cursor: pointer;
		transition: color 200ms ease;
	}
	.tabs .on {
		color: var(--nm-purple, #7c5ce8);
	}
	.tabs button:focus-visible {
		outline: 3px solid var(--nm-purple, #7c5ce8);
		outline-offset: 2px;
	}
	form {
		display: grid;
		gap: 1rem;
	}
	.field {
		display: grid;
		gap: 0.4rem;
	}
	.field label {
		font: 600 0.95rem var(--font-display);
	}
	.well {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		min-height: 3.2rem;
		padding: 0 0.6rem 0 1rem;
		border-radius: 16px;
		box-shadow: var(--nm-in);
		color: var(--nm-ink-2, #6b7090);
		transition: box-shadow 200ms ease;
	}
	.well:focus-within {
		box-shadow:
			var(--nm-in),
			0 0 0 3px rgb(124 92 232 / 0.35);
	}
	.well:has(input[aria-invalid='true']) {
		box-shadow:
			var(--nm-in),
			0 0 0 2px #f23f75;
	}
	.well input {
		flex: 1;
		min-width: 0;
		height: 3rem;
		border: 0;
		background: transparent;
		color: var(--nm-ink, #2b2f45);
		font: 600 1rem var(--font-body);
		outline: none;
	}
	.peek {
		display: grid;
		place-items: center;
		width: 2.75rem;
		height: 2.75rem;
		border: 0;
		border-radius: 12px;
		background: transparent;
		color: var(--nm-ink-2, #6b7090);
		cursor: pointer;
	}
	.peek[aria-pressed='true'] {
		box-shadow: var(--nm-in);
		color: var(--nm-purple, #7c5ce8);
	}
	.peek:focus-visible {
		outline: 3px solid var(--nm-purple, #7c5ce8);
	}
	.field-error {
		color: #c2185b;
		font-weight: 700;
		font-size: 0.9rem;
	}
	.help {
		color: var(--nm-ink-2, #6b7090);
		font-size: 0.88rem;
	}
	.forgot {
		justify-self: end;
		margin-top: -0.3rem;
		color: var(--nm-purple, #7c5ce8);
		font-weight: 800;
		font-size: 0.92rem;
		text-underline-offset: 3px;
	}
	.go {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		min-height: 3.4rem;
		border: 0;
		border-radius: 18px;
		background: linear-gradient(145deg, #8f73f0, #6644d8);
		color: #fff;
		font: 700 1.1rem var(--font-display);
		box-shadow:
			6px 6px 16px rgb(102 68 216 / 0.35),
			-6px -6px 14px rgb(255 255 255 / 0.9);
		cursor: pointer;
		transition:
			transform 140ms ease,
			box-shadow 140ms ease;
	}
	.go:hover:not(:disabled) {
		transform: translateY(-1px);
	}
	.go:active:not(:disabled) {
		transform: translateY(1px);
		box-shadow: inset 3px 3px 8px rgb(60 30 160 / 0.45);
	}
	.go:disabled {
		opacity: 0.75;
		cursor: progress;
	}
	.go:focus-visible {
		outline: 3px solid #2b2f45;
		outline-offset: 3px;
	}
	.spinner {
		width: 1.1rem;
		height: 1.1rem;
		border: 3px solid rgb(255 255 255 / 0.4);
		border-top-color: #fff;
		border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}
	.alert {
		padding: 0.75rem 1rem;
		border-radius: 14px;
		box-shadow: var(--nm-in);
		color: #a3134f;
		font-weight: 800;
	}
	.demo {
		color: var(--nm-ink-2, #6b7090);
		font-size: 0.92rem;
	}
	.link {
		border: 0;
		padding: 0;
		background: none;
		color: var(--nm-purple, #7c5ce8);
		font-weight: 800;
		text-decoration: underline;
		text-underline-offset: 3px;
		cursor: pointer;
	}
	code {
		font-size: 0.85rem;
	}
	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.pill {
			transition: none;
		}
		.spinner {
			animation: none;
		}
	}
	@media (max-width: 420px) {
		.signin {
			padding: 1.3rem;
		}
	}
</style>
