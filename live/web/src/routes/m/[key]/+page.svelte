<!--
	The page a room link opens: didik…/m/harimau-ungu-42 (or the six-digit code). A child picks an
	animal and a name, waits in the lobby, plays, and sees the podium, all on this one page.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { api } from '$lib/api';
	import { RoomClient } from '$lib/room.svelte';
	import type { RoomInfo } from '$lib/types';
	import { play } from '$lib/sound';
	import { enterFullscreen, fullscreenActive, fullscreenAvailable } from '$lib/fullscreen';
	import Didi from '$ui/Didi.svelte';
	import Logo from '$ui/Logo.svelte';
	import Podium from '$ui/Podium.svelte';
	import CharacterStage from '$ui/CharacterStage.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';
	import JoinForm from '$lib/play/JoinForm.svelte';
	import PlayerLobby from '$lib/play/PlayerLobby.svelte';
	import PlayerGame from '$lib/games/PlayerGame.svelte';

	const key = page.params.key ?? '';
	// ?pratonton=1: a parent trying the game from the host screen joins at once, as a pretend child.
	const preview = page.url.searchParams.has('pratonton');
	let previewJoined = false;
	const client = new RoomClient(key, 'player');

	let info = $state<RoomInfo | null>(null);
	let missing = $state<string | null>(null);
	let canFullscreen = $state(false);
	let isFullscreen = $state(false);
	let dismissFullscreenPrompt = $state(false);
	let wasPlaying = false;

	const view = $derived(client.view);
	const me = $derived(view?.me);
	const people = $derived(client.people);
	const unit = $derived(view?.room.mode.unit ?? 'mata');

	$effect(() => {
		const playing = view?.phase === 'playing';
		if (playing && !wasPlaying) dismissFullscreenPrompt = false;
		wasPlaying = playing;
	});

	function joinWithFullscreen(data: Parameters<typeof client.join>[0]) {
		// JoinForm calls this directly from its submit event, while user activation is still available.
		void enterFullscreen();
		client.join(data);
	}

	async function enterForGame() {
		if (!(await enterFullscreen())) dismissFullscreenPrompt = true;
	}


	$effect(() => {
		if (preview && info && client.needsJoin && !previewJoined) {
			previewJoined = true;
			client.join({ name: 'Cikgu Pratonton', avatar: 'kancil', colour: 'hijau', skin: 's2' });
		}
	});

	onMount(() => {
		canFullscreen = fullscreenAvailable();
		const syncFullscreen = () => (isFullscreen = fullscreenActive());
		syncFullscreen();
		document.addEventListener('fullscreenchange', syncFullscreen);
		document.addEventListener('webkitfullscreenchange', syncFullscreen);
		api
			.get<RoomInfo>(`/api/rooms/${encodeURIComponent(key)}`)
			.then((room) => {
				info = room;
				client.connect();
			})
			.catch((error) => (missing = error.message));
		const stopFx = client.onFx((fx) => {
			if (fx.kind === 'start') play('go');
			if (fx.kind === 'joined' && fx.player !== client.youId) play('pop');
		});
		return () => {
			document.removeEventListener('fullscreenchange', syncFullscreen);
			document.removeEventListener('webkitfullscreenchange', syncFullscreen);
			stopFx();
			client.close();
		};
	});
</script>

<svelte:head><title>{info ? `${info.quizTitle} · DIDIK Main Bersama` : 'Masuk bilik · DIDIK Main Bersama'}</title></svelte:head>

{#if missing}
	<main class="center wrap">
		<Didi mood="hint" size={150} />
		<h1>Bilik tidak dijumpai</h1>
		<p>{missing}</p>
		<a class="btn btn--sun btn--big" href="/">Masukkan kod lain</a>
	</main>
{:else if client.notice}
	<main class="center wrap">
		<Didi mood="hint" size={150} />
		<h1>Permainan tamat di sini</h1>
		<p>{client.notice}</p>
		<a class="btn btn--big" href="/">Ke laman utama</a>
	</main>
{:else if view && me && view.phase === 'waiting'}
	<main class="center wrap">
		<CharacterStage animal={me.avatar} colour={me.colour} skin={me.skin} size={84} mood="happy" />
		<h1>Tunggu sebentar, {me.name}</h1>
		<p>Hos akan benarkan kamu masuk.</p>
	</main>
{:else if view && me && view.phase === 'lobby'}
	<PlayerLobby {client} {view} {me} people={client.roster} />
{:else if view && me && view.phase === 'playing' && view.game}
	<PlayerGame {client} {view} {me} {people} />
	{#if canFullscreen && !isFullscreen && !dismissFullscreenPrompt}
		<div class="fullscreen-prompt" role="region" aria-label="Pilihan skrin penuh">
			<span>Main dengan paparan skrin penuh?</span>
			<button type="button" class="fullscreen-yes" onclick={enterForGame}>Skrin penuh</button>
			<button type="button" class="fullscreen-skip" onclick={() => (dismissFullscreenPrompt = true)} aria-label="Teruskan tanpa skrin penuh">×</button>
		</div>
	{/if}
{:else if view && me && view.phase === 'ended' && view.results}
	<main class="ended wrap">
		<h1>Tamat!</h1>
		<Podium results={view.results} {people} me={me.id} {unit} />
		<p class="next">Tunggu hos untuk permainan seterusnya.</p>
	</main>
{:else if info && client.needsJoin}
	<main class="joining wrap">
		<header class="join-head">
			<Logo />
		</header>
		<section class="room-card">
			<WorldBadge world={info.mode.world} size={64} />
			<div>
				<p class="mode">{info.mode.title}</p>
				<h1>{info.quizTitle}</h1>
			</div>
		</section>
		<JoinForm {info} busy={client.joining} error={client.error} onjoin={joinWithFullscreen} />
	</main>
{:else}
	<main class="center wrap" aria-busy="true">
		<Didi mood="think" size={130} />
		<p class="connecting">{client.status === 'reconnecting' ? 'Menyambung semula…' : 'Menyambung ke bilik…'}</p>
	</main>
{/if}

{#if client.status === 'reconnecting' && view}
	<p class="offline" role="status">Sambungan terputus. Menyambung semula…</p>
{:else if view?.resuming}
	<p class="offline" role="status">Menunggu semua pemain kembali…</p>
{/if}
{#if client.error && view}
	<p class="toast" role="alert">{client.error}</p>
{/if}

<style>
	.center {
		display: grid;
		justify-items: center;
		align-content: center;
		gap: 0.9rem;
		min-height: 100dvh;
		text-align: center;
	}
	.center h1 {
		font-size: var(--fs-h1);
	}
	.center p {
		color: var(--ink-2);
		max-width: 28rem;
	}
	.connecting {
		font-weight: 800;
	}
	.joining {
		display: grid;
		gap: 1.4rem;
		max-width: 34rem;
		padding-block: 1rem 3rem;
	}
	.room-card {
		display: flex;
		align-items: center;
		gap: 0.9rem;
	}
	.room-card h1 {
		font-size: 1.5rem;
	}
	.mode {
		color: var(--brand-ink);
		font-weight: 800;
	}
	.ended {
		display: grid;
		gap: 1rem;
		max-width: 44rem;
		padding-block: 1.5rem 3rem;
	}
	.ended h1 {
		font-size: var(--fs-hero);
		text-align: center;
	}
	.next {
		text-align: center;
		color: var(--ink-2);
		font-weight: 800;
	}
	.offline,
	.toast {
		position: fixed;
		left: 50%;
		bottom: max(1rem, env(safe-area-inset-bottom, 0px));
		translate: -50% 0;
		z-index: 50;
		width: max-content;
		max-width: calc(100vw - 2rem);
		padding: 0.7rem 1.1rem;
		border-radius: var(--r-lg);
		text-align: center;
		background: var(--ink);
		color: #fff;
		font-weight: 800;
		box-shadow: var(--lift-low);
		animation: rise-in var(--t-enter) var(--spring);
	}
	.toast {
		background: #7a3d00;
		bottom: max(4.2rem, env(safe-area-inset-bottom, 0px));
	}
	.fullscreen-prompt {
		position: fixed;
		z-index: 90;
		top: max(.7rem, env(safe-area-inset-top, 0px));
		left: 50%;
		translate: -50% 0;
		display: flex;
		align-items: center;
		gap: .65rem;
		width: max-content;
		max-width: calc(100vw - 1rem);
		padding: .55rem;
		border: 2px solid #4e3d37;
		border-radius: .85rem;
		background: #fff7e5;
		box-shadow: 0 .4rem 1.3rem #1f172c55;
		font-size: .85rem;
		font-weight: 800;
	}
	.fullscreen-prompt button { flex: none; min-height: 2.5rem; border: 0; border-radius: .55rem; font: 800 .82rem var(--font-body); cursor: pointer; }
	.fullscreen-yes { padding: .35rem .75rem; background: #6d4ed2; color: white; }
	.fullscreen-skip { width: 2.5rem; background: #eee3d4; color: #4e3d37; font-size: 1.2rem !important; }
	.fullscreen-prompt button:focus-visible { outline: 3px solid #176b9c; outline-offset: 2px; }
	@media (max-width: 500px) {
		.fullscreen-prompt { flex-wrap: wrap; width: calc(100vw - 1rem); }
		.fullscreen-prompt span { flex: 1 1 100%; }
		.fullscreen-skip { margin-left: auto; }
	}
</style>
