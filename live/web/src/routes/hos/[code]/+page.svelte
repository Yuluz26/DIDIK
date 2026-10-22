<!-- The host screen for one room: lobby, the game on the big screen, then the podium. -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import { applyLook } from '$lib/look';
	import Didi from '$ui/Didi.svelte';
	import Icon from '$ui/Icon.svelte';
	import Podium from '$ui/Podium.svelte';
	import HostBar from '$lib/host/HostBar.svelte';
	import HostGame from '$lib/host/HostGame.svelte';
	import HostLobby from '$lib/host/HostLobby.svelte';

	const code = page.params.code ?? '';
	const client = new RoomClient(code, 'host');
	const view = $derived(client.view);
	const people = $derived(client.people);
	const unit = $derived(view?.room.mode.unit ?? 'mata');

	$effect(() => applyLook(view?.room.mode.look));

	onMount(() => {
		client.connect();
		const stop = client.onFx((fx) => {
			if (fx.kind === 'joined') play('join');
			if (fx.kind === 'start') play('go');
		});
		return () => {
			stop();
			client.close();
		};
	});
</script>

<svelte:head><title>{view ? `Hos · ${view.room.mode.title}` : 'Hos'} · DIDIK Main Bersama</title></svelte:head>

{#if client.notice}
	<main class="center wrap">
		<Didi mood="hint" size={150} />
		<h1>Bilik tidak dapat dibuka</h1>
		<p>{client.notice}</p>
		<a class="btn btn--big" href="/ibu-bapa">Ke kuiz saya</a>
	</main>
{:else if !view}
	<main class="center wrap" aria-busy="true">
		<Didi mood="think" size={130} />
		<p>Membuka bilik…</p>
	</main>
{:else}
	<HostBar {client} {view} />
	<main class="host wrap">
		{#if view.phase === 'lobby'}
			<HostLobby {client} {view} />
		{:else if view.phase === 'playing' && view.game}
			<HostGame {client} {view} {people} />
		{:else if view.phase === 'ended' && view.results}
			<div class="ended">
				<h1>Tamat!</h1>
				<Podium results={view.results} {people} {unit} />
				<div class="again">
					<button type="button" class="btn btn--sun btn--big" onclick={() => client.send({ t: 'lobby' })}><Icon name="play" /> Main lagi</button>
					<a class="btn btn--plain btn--big" href="/ibu-bapa">Pilih kuiz lain</a>
				</div>
			</div>
		{/if}
	</main>
{/if}

{#if client.status === 'reconnecting' && view}
	<p class="toast" role="status">Sambungan terputus. Menyambung semula…</p>
{/if}
{#if client.error}
	<p class="toast warn" role="alert">{client.error}</p>
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
	}
	.host {
		padding-block: 1.2rem 3rem;
	}
	.ended {
		display: grid;
		gap: 1.2rem;
		max-width: 48rem;
		margin-inline: auto;
	}
	.ended h1 {
		font-size: var(--fs-hero);
		text-align: center;
	}
	.again {
		display: flex;
		justify-content: center;
		gap: 0.8rem;
		flex-wrap: wrap;
	}
	.toast {
		position: fixed;
		left: 50%;
		bottom: max(1rem, env(safe-area-inset-bottom, 0px));
		translate: -50% 0;
		z-index: 50;
		padding: 0.7rem 1.1rem;
		border-radius: var(--r-pill);
		background: var(--ink);
		color: #fff;
		font-weight: 800;
		animation: rise-in var(--t-enter) var(--spring);
	}
	.warn {
		background: #7a3d00;
	}
</style>
