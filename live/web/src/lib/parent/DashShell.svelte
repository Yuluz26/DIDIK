<!--
	The signed-in parent's dashboard shell: a soft neumorphic panel with a sidebar and the page beside it.
	Every page after sign-in (dashboard, quizzes, rooms, games, account, the quiz editor) sits in this.

	The shell sets the look for everything inside it by redefining the app's colour and shape tokens, so
	the existing editor and forms follow along; the games and the signed-out pages keep their own look.
	Type: Fredoka for headings and numbers (rounded, friendly, not pixel), Nunito for reading.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { session } from '$lib/session.svelte';
	import { parent } from './store.svelte';
	import Kawaii from './ui/Kawaii.svelte';
	import NmIcon from './ui/NmIcon.svelte';

	let { children }: { children: Snippet } = $props();

	let drawer = $state(false);
	let userMenu = $state(false);

	const NAV = [
		{ href: '/ibu-bapa', label: 'Papan pemuka', icon: 'dashboard' },
		{ href: '/ibu-bapa/kuiz', label: 'Kuiz saya', icon: 'quiz' },
		{ href: '/ibu-bapa/contoh', label: 'Kuiz contoh', icon: 'sparkle' },
		{ href: '/ibu-bapa/kuiz/baru', label: 'Kuiz baharu', icon: 'plus' },
		{ href: '/ibu-bapa/bilik', label: 'Bilik langsung', icon: 'room' },
		{ href: '/ibu-bapa/permainan', label: 'Permainan', icon: 'game' },
		{ href: '/ibu-bapa/akaun', label: 'Akaun', icon: 'user' }
	];

	function current(href: string): boolean {
		const path = page.url.pathname.replace(/\/$/, '');
		if (href === '/ibu-bapa') return path === '/ibu-bapa';
		if (href === '/ibu-bapa/kuiz') return path === href || (/^\/ibu-bapa\/kuiz\/\d+/.test(path) && true);
		return path === href;
	}

	onMount(() => {
		void (async () => {
			if (!(await session.load())) await goto('/ibu-bapa');
		})();
		const close = (e: KeyboardEvent) => {
			if (e.key === 'Escape') {
				drawer = false;
				userMenu = false;
			}
		};
		window.addEventListener('keydown', close);
		return () => window.removeEventListener('keydown', close);
	});

	$effect(() => {
		if (session.user) void parent.ensure();
	});

	// Going to another page closes the drawer.
	$effect(() => {
		void page.url.pathname;
		drawer = false;
		userMenu = false;
	});

	async function logout() {
		await session.logout();
		parent.reset();
		await goto('/ibu-bapa');
	}
</script>

<div class="nm">
	<div class="blobs" aria-hidden="true"><span class="b1"></span><span class="b2"></span><span class="b3"></span></div>

	<div class="frame">
		{#if drawer}<button type="button" class="scrim" aria-label="Tutup menu" onclick={() => (drawer = false)}></button>{/if}

		<aside class="side" class:open={drawer} aria-label="Menu utama">
			<div class="side-in">
			<a class="brand" href="/ibu-bapa" aria-label="DIDIK, papan pemuka">
				<span class="mascot"><Kawaii seed="didik" size={40} mood="happy" /></span>
				<span class="word"><b>Didik</b><small>main bersama</small></span>
			</a>

			<nav class="menu">
				{#each NAV as item (item.href)}
					<a href={item.href} class:on={current(item.href)} aria-current={current(item.href) ? 'page' : undefined}>
						<NmIcon name={item.icon} size={20} />
						<span>{item.label}</span>
						{#if item.icon === 'room' && parent.rooms.length}<em class="count" aria-label="{parent.rooms.length} bilik dibuka">{parent.rooms.length}</em>{/if}
					</a>
				{/each}
			</nav>

			<a class="home" href="/"><NmIcon name="home" size={18} /> Laman utama</a>

			<div class="user">
				<button type="button" class="who" aria-expanded={userMenu} onclick={() => (userMenu = !userMenu)}>
					<span class="face"><Kawaii seed={session.user?.email ?? 'ibu'} size={36} /></span>
					<span class="name">{session.user?.name ?? '…'}</span>
					<NmIcon name="more" size={18} label="Menu akaun" />
				</button>
				{#if userMenu}
					<div class="pop" role="menu">
						<a role="menuitem" href="/ibu-bapa/akaun"><NmIcon name="user" size={18} /> Akaun saya</a>
						<button type="button" role="menuitem" onclick={logout}><NmIcon name="logout" size={18} /> Log keluar</button>
					</div>
				{/if}
			</div>
			</div>
		</aside>

		<div class="content">
			<header class="top">
				<button type="button" class="burger" aria-label="Buka menu" aria-expanded={drawer} onclick={() => (drawer = true)}>
					<NmIcon name="menu" size={22} />
				</button>
				<a class="brand small" href="/ibu-bapa" aria-label="DIDIK, papan pemuka">
					<span class="mascot"><Kawaii seed="didik" size={32} mood="happy" /></span>
					<span class="word"><b>Didik</b></span>
				</a>
				<button type="button" class="avatar-btn" aria-label="Akaun" onclick={() => goto('/ibu-bapa/akaun')}>
					<Kawaii seed={session.user?.email ?? 'ibu'} size={34} />
				</button>
			</header>

			<main class="page">{@render children()}</main>
		</div>
	</div>
</div>

<style>
	/* ------------------------------------------------------------ tokens for everything inside */
	.nm {
		--nm-bg: #eceef4;
		--nm-surface: linear-gradient(145deg, #f7f8fc, #eaecf3);
		--nm-out: 9px 9px 22px rgb(163 172 198 / 0.42), -9px -9px 22px rgb(255 255 255 / 0.95);
		--nm-out-sm: 5px 5px 13px rgb(163 172 198 / 0.4), -5px -5px 13px rgb(255 255 255 / 0.95);
		--nm-in: inset 4px 4px 10px rgb(163 172 198 / 0.45), inset -4px -4px 10px rgb(255 255 255 / 0.95);
		--nm-purple: #7c5ce8;
		--nm-purple-2: #6644d8;
		--nm-pink: #f23f75;
		--nm-blue: #5b8cf5;
		--nm-teal: #1fc7a5;

		/* the app's own tokens, re-coloured so existing components follow */
		--paper: var(--nm-bg);
		--paper-2: #e4e7f0;
		--card: #f1f3f8;
		--ink: #20233c;
		--ink-2: #545a76;
		--ink-3: #666c86;
		--line: #dde0ea;
		--brand: var(--nm-purple);
		--brand-deep: var(--nm-purple-2);
		--brand-soft: #e7e1ff;
		--on-brand-soft: #4a30b0;
		--brand-ink: #5a3fc4;
		--sun: var(--nm-pink);
		--sun-deep: #c82a5c;
		--on-bright: #ffffff;
		--sea: var(--nm-teal);
		--sea-deep: #0f9a80;
		--sky: var(--nm-blue);
		--coral: #ef5b5b;
		--r-sm: 14px;
		--r-md: 20px;
		--r-lg: 28px;
		--card-shadow: var(--nm-out-sm);
		--font-display: 'Fredoka Variable', ui-rounded, 'Hiragino Maru Gothic ProN', system-ui, sans-serif;

		position: relative;
		min-height: 100dvh;
		padding: clamp(0px, 2.4vw, 2.2rem);
		background: linear-gradient(180deg, #f3f4f9, #e9ebf3);
		color: var(--ink);
		overflow-x: clip;
	}
	.blobs span {
		position: fixed;
		z-index: 0;
		border-radius: 50%;
		filter: blur(60px);
		pointer-events: none;
	}
	.b1 {
		top: -8vh;
		left: -6vw;
		width: 34vw;
		height: 34vw;
		background: rgb(255 154 196 / 0.28);
	}
	.b2 {
		right: -8vw;
		bottom: 8vh;
		width: 30vw;
		height: 30vw;
		background: rgb(150 120 255 / 0.25);
	}
	.b3 {
		top: 30vh;
		right: 4vw;
		width: 18vw;
		height: 18vw;
		background: rgb(120 190 255 / 0.2);
	}

	.frame {
		position: relative;
		z-index: 1;
		display: grid;
		grid-template-columns: 15.5rem minmax(0, 1fr);
		max-width: 82rem;
		min-height: calc(100dvh - clamp(0px, 4.8vw, 4.4rem));
		margin-inline: auto;
		border-radius: clamp(0px, 3vw, 2.4rem);
		background: linear-gradient(145deg, #f4f5fa, #eaecf3);
		box-shadow: 0 30px 60px rgb(150 160 190 / 0.35), 0 0 0 1px rgb(255 255 255 / 0.7) inset;
	}

	/* ------------------------------------------------------------ sidebar */
	.side {
		position: relative;
		border-radius: clamp(0px, 3vw, 2.4rem) 0 0 clamp(0px, 3vw, 2.4rem);
		background: linear-gradient(180deg, #f1f2f8, #e8eaf2);
		box-shadow: inset -1px 0 0 rgb(255 255 255 / 0.7), 6px 0 16px rgb(163 172 198 / 0.18);
	}
	/* the sidebar's content stays in view while a long page scrolls */
	.side-in {
		position: sticky;
		top: clamp(0px, 2.4vw, 2.2rem);
		display: flex;
		flex-direction: column;
		gap: 1.1rem;
		height: calc(100dvh - 2 * clamp(0px, 2.4vw, 2.2rem));
		padding: 1.6rem 1.1rem 1.1rem;
		overflow-y: auto;
	}
	.brand {
		display: flex;
		align-items: center;
		min-height: 2.75rem;
		gap: 0.6rem;
		padding: 0.2rem 0.5rem 0.8rem;
		color: var(--ink);
		text-decoration: none;
	}
	/* the "Kuiz saya" link back from a quiz's pages: a full-size target on a touch screen */
	.nm :global(a.back) {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		min-height: 2.75rem;
	}
	.mascot {
		display: grid;
		place-items: center;
		flex: none;
		line-height: 0;
		transition: transform 260ms var(--spring);
	}
	.brand:hover .mascot {
		transform: rotate(-8deg) scale(1.08);
	}
	.word {
		display: grid;
		line-height: 1;
	}
	.word b {
		font: 600 1.75rem/1 var(--font-display);
		letter-spacing: -0.01em;
		background: linear-gradient(90deg, var(--nm-purple), var(--nm-pink));
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
	}
	.word small {
		margin-top: 0.2rem;
		color: var(--ink-3);
		font: 700 0.7rem/1 var(--font-body);
		letter-spacing: 0.12em;
		text-transform: uppercase;
	}
	.menu {
		display: grid;
		gap: 0.35rem;
		margin-top: 0.2rem;
	}
	.menu a {
		position: relative;
		display: flex;
		align-items: center;
		gap: 0.8rem;
		min-height: 2.9rem;
		padding: 0.5rem 0.9rem;
		border-radius: 1.1rem;
		color: var(--ink-2);
		font: 500 1rem/1.1 var(--font-display);
		text-decoration: none;
		transition:
			box-shadow 200ms,
			color 200ms,
			background 200ms,
			transform 200ms;
	}
	.menu a:hover {
		color: var(--ink);
		box-shadow: var(--nm-out-sm);
	}
	.menu a.on {
		background: linear-gradient(135deg, #8a69f5, var(--nm-purple-2));
		color: #fff;
		box-shadow: 0 10px 20px rgb(112 80 220 / 0.38), inset 0 1px 0 rgb(255 255 255 / 0.3);
	}
	.count {
		margin-left: auto;
		display: inline-grid;
		place-items: center;
		min-width: 1.4rem;
		height: 1.4rem;
		padding: 0 0.35rem;
		border-radius: 999px;
		background: var(--nm-pink);
		color: #fff;
		font: 600 0.78rem/1 var(--font-display);
		font-style: normal;
		box-shadow: 0 4px 10px rgb(242 63 117 / 0.4);
	}
	.home {
		display: flex;
		align-items: center;
		min-height: 2.75rem;
		gap: 0.6rem;
		margin-top: auto;
		padding: 0.5rem 0.9rem;
		border-radius: 1rem;
		color: var(--ink-2);
		font: 600 0.92rem/1 var(--font-display);
		text-decoration: none;
	}
	.home:hover {
		color: var(--ink);
		box-shadow: var(--nm-out-sm);
	}
	.user {
		position: relative;
		padding-top: 0.9rem;
		border-top: 1px solid rgb(255 255 255 / 0.8);
		box-shadow: 0 -1px 0 rgb(163 172 198 / 0.25);
	}
	.who {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		width: 100%;
		padding: 0.4rem 0.6rem;
		border: 0;
		border-radius: 1.2rem;
		background: transparent;
		color: var(--ink);
		text-align: left;
		cursor: pointer;
		transition: box-shadow 200ms;
	}
	.who:hover,
	.who[aria-expanded='true'] {
		box-shadow: var(--nm-out-sm);
	}
	.face {
		line-height: 0;
	}
	.name {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		font: 600 0.98rem/1.1 var(--font-display);
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.pop {
		position: absolute;
		left: 0.4rem;
		right: 0.4rem;
		bottom: calc(100% - 0.4rem);
		z-index: 5;
		display: grid;
		gap: 0.2rem;
		padding: 0.5rem;
		border-radius: 1.2rem;
		background: #f4f5fa;
		box-shadow: var(--nm-out);
		animation: nm-pop 180ms var(--ease-out);
	}
	.pop a,
	.pop button {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		min-height: 2.6rem;
		padding: 0.4rem 0.7rem;
		border: 0;
		border-radius: 0.9rem;
		background: transparent;
		color: var(--ink);
		font: 600 0.95rem/1 var(--font-display);
		text-decoration: none;
		text-align: left;
		cursor: pointer;
	}
	.pop a:hover,
	.pop button:hover {
		background: #e8eaf3;
	}
	@keyframes nm-pop {
		from {
			opacity: 0;
			transform: translateY(6px) scale(0.97);
		}
	}

	/* ------------------------------------------------------------ the page beside it */
	.content {
		min-width: 0;
		display: flex;
		flex-direction: column;
	}
	.top {
		display: none;
	}
	.page {
		flex: 1;
		min-width: 0;
		padding: clamp(1.2rem, 2.6vw, 2.2rem);
		padding-bottom: 3rem;
	}

	/* ------------------------------------------------------------ small screens: the sidebar is a drawer */
	.scrim {
		display: none;
	}
	@media (max-width: 62rem) {
		.nm {
			padding: 0;
		}
		.frame {
			display: block;
			min-height: 100dvh;
			border-radius: 0;
		}
		.side {
			position: fixed;
			inset: 0 auto 0 0;
			z-index: 40;
			width: min(18rem, 86vw);
			border-radius: 0 2rem 2rem 0;
			box-shadow: 14px 0 40px rgb(100 110 150 / 0.35);
			transform: translateX(-105%);
			transition: transform 260ms var(--ease-out);
		}
		.side-in {
			position: static;
			height: 100%;
		}
		.side.open {
			transform: none;
		}
		.scrim {
			position: fixed;
			inset: 0;
			z-index: 30;
			display: block;
			border: 0;
			background: rgb(40 46 80 / 0.35);
			backdrop-filter: blur(2px);
		}
		.top {
			position: sticky;
			top: 0;
			z-index: 20;
			display: flex;
			align-items: center;
			justify-content: space-between;
			gap: 0.8rem;
			padding: 0.7rem 1rem;
			background: rgb(240 241 247 / 0.92);
			backdrop-filter: blur(10px);
			box-shadow: 0 6px 18px rgb(163 172 198 / 0.25);
		}
		.burger,
		.avatar-btn {
			display: grid;
			place-items: center;
			width: 2.9rem;
			height: 2.9rem;
			padding: 0;
			border: 0;
			border-radius: 1rem;
			background: var(--nm-surface);
			color: var(--ink);
			box-shadow: var(--nm-out-sm);
			cursor: pointer;
		}
		.avatar-btn {
			border-radius: 50%;
		}
		.brand.small {
			padding: 0;
		}
		.brand.small .word b {
			font-size: 1.5rem;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.side,
		.mascot,
		.pop {
			transition: none;
			animation: none;
		}
	}

	/* ------------------------------------------------------------ the app's own controls, softened */
	.nm :global(.btn) {
		--on: var(--ink);
		min-height: 2.85rem;
		padding: 0.6em 1.4em;
		border-radius: 999px;
		background: var(--nm-surface);
		color: var(--ink);
		font: 600 1rem/1.1 var(--font-display);
		letter-spacing: 0;
		box-shadow: var(--nm-out-sm);
		transition:
			box-shadow 180ms,
			transform 180ms,
			filter 180ms;
	}
	.nm :global(.btn:hover) {
		transform: translateY(-1px);
		box-shadow: 7px 7px 16px rgb(163 172 198 / 0.45), -7px -7px 16px rgb(255 255 255 / 0.95);
	}
	.nm :global(.btn:active) {
		transform: translateY(0);
		box-shadow: var(--nm-in);
	}
	.nm :global(.btn--sun),
	.nm :global(.btn--sky) {
		background: linear-gradient(135deg, #ff5f8d, #ee3469);
		color: #fff;
		box-shadow: 0 10px 20px rgb(242 63 117 / 0.38), inset 0 1px 0 rgb(255 255 255 / 0.35);
	}
	.nm :global(.btn--sun:hover),
	.nm :global(.btn--sky:hover) {
		box-shadow: 0 13px 24px rgb(242 63 117 / 0.45), inset 0 1px 0 rgb(255 255 255 / 0.35);
	}
	.nm :global(.btn--sun:active),
	.nm :global(.btn--sky:active) {
		box-shadow: inset 0 3px 8px rgb(150 20 60 / 0.45);
	}
	.nm :global(.btn:not(.btn--plain):not(.btn--sun):not(.btn--sky):not(.btn--coral):not(.btn--sea):not(.btn--ghost):not(.tool)) {
		background: linear-gradient(135deg, #8a69f5, var(--nm-purple-2));
		color: #fff;
		box-shadow: 0 10px 20px rgb(112 80 220 / 0.35), inset 0 1px 0 rgb(255 255 255 / 0.3);
	}
	.nm :global(.btn--sea) {
		background: linear-gradient(135deg, #3fe0bf, #12a98d);
		color: #fff;
		box-shadow: 0 10px 20px rgb(18 169 141 / 0.32);
	}
	.nm :global(.btn--coral) {
		background: linear-gradient(135deg, #ff7a7a, #e84a4a);
		color: #fff;
		box-shadow: 0 10px 20px rgb(232 74 74 / 0.3);
	}
	.nm :global(.btn--plain) {
		background: var(--nm-surface);
		color: var(--ink);
	}
	.nm :global(.btn--ghost) {
		background: transparent;
		box-shadow: none;
	}
	.nm :global(.btn--icon) {
		min-width: 2.85rem;
		padding: 0.5rem;
	}
	.nm :global(.input) {
		border: 0;
		border-radius: 1.1rem;
		background: #eceef5;
		box-shadow: var(--nm-in);
		font-weight: 700;
	}
	.nm :global(.input:hover) {
		border: 0;
	}
	.nm :global(.input:focus) {
		outline: none;
		box-shadow: var(--nm-in), 0 0 0 3px rgb(124 92 232 / 0.35);
	}
	.nm :global(.chip) {
		border: 0;
		border-radius: 999px;
		background: #eceef5;
		color: var(--ink-2);
		box-shadow: inset 2px 2px 5px rgb(163 172 198 / 0.35), inset -2px -2px 5px rgb(255 255 255 / 0.9);
	}
	.nm :global(.tool:hover) {
		background: #e4e7f0;
	}
	.nm :global(:focus-visible) {
		outline: 3px solid rgb(124 92 232 / 0.6);
		outline-offset: 3px;
	}
	.nm :global(h1),
	.nm :global(h2),
	.nm :global(h3) {
		font-weight: 500;
		letter-spacing: -0.005em;
	}

	/* ------------------------------------------------------------ pieces the pages share */
	.nm :global(.nm-head) {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		gap: 1rem 1.5rem;
		margin-bottom: clamp(1.2rem, 2.4vw, 2rem);
	}
	.nm :global(.nm-head h1) {
		font: 500 clamp(1.7rem, 1.2rem + 1.6vw, 2.5rem) / 1.1 var(--font-display);
		color: var(--ink);
	}
	.nm :global(.nm-head p) {
		margin-top: 0.3rem;
		color: var(--ink-2);
		font-weight: 600;
	}
	.nm :global(.nm-card) {
		position: relative;
		border-radius: 1.6rem;
		background: var(--nm-surface);
		box-shadow: var(--nm-out);
	}
	.nm :global(.nm-well) {
		border-radius: 1.2rem;
		background: #eceef5;
		box-shadow: var(--nm-in);
	}
</style>
