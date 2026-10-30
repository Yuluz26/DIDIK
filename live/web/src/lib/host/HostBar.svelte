<!-- The host's controls during a game: pause, next, end. Always within reach, never in the way. On a phone
	the logo is the mascot alone and the controls sit together on one compact row under the game's name. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { View } from '$lib/types';
	import Icon from '$ui/Icon.svelte';
	import Logo from '$ui/Logo.svelte';
	import FullscreenToggle from '$ui/FullscreenToggle.svelte';
	import SoundToggle from '$ui/SoundToggle.svelte';

	let { client, view }: { client: RoomClient; view: View } = $props();

	let confirming = $state(false);
	const paused = $derived(!!view.game?.clock?.paused);
	const sync = $derived(view.room.mode.pace === 'sync');
	const players = $derived(client.roster.filter((p) => p.approved && !p.bot).length);
</script>

<header class="bar">
	<Logo href="/ibu-bapa" compact />
	<div class="what">
		<strong>{view.room.mode.title}</strong>
		<span>{view.room.quizTitle} · kod {view.room.code} · {players} kanak-kanak</span>
	</div>
	<div class="tools">
	{#if view.phase === 'playing'}
		<button type="button" class="btn btn--plain" onclick={() => client.send({ t: paused ? 'resume' : 'pause' })}>
			<Icon name={paused ? 'play' : 'pause'} /> {paused ? 'Sambung' : 'Rehat'}
		</button>
		{#if sync}
			<button type="button" class="btn btn--plain" onclick={() => client.send({ t: 'skip' })}><Icon name="skip" /> Seterusnya</button>
		{/if}
		{#if confirming}
			<span class="confirm">
				Tamatkan sekarang?
				<button type="button" class="btn btn--coral" onclick={() => { client.send({ t: 'end' }); confirming = false; }}>Ya, tamat</button>
				<button type="button" class="btn btn--plain" onclick={() => (confirming = false)}>Batal</button>
			</span>
		{:else}
			<button type="button" class="btn btn--plain" onclick={() => (confirming = true)}><Icon name="stop" /> Tamat</button>
		{/if}
	{/if}
	<FullscreenToggle />
	<SoundToggle />
	</div>
</header>

<style>
	.bar {
		position: sticky;
		top: env(safe-area-inset-top, 0px);
		z-index: 30;
		display: flex;
		align-items: center;
		gap: 0.7rem;
		padding: 0.6rem var(--gutter-r) 0.6rem var(--gutter);
		background: var(--paper);
		border-bottom: 2px solid var(--line);
		flex-wrap: wrap;
	}
	.what {
		display: grid;
		flex: 1;
		min-width: 12rem;
		line-height: 1.2;
	}
	.tools {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.6rem;
	}
	.what strong {
		font: 600 1.15rem var(--font-display);
	}
	.what span {
		color: var(--ink-2);
		font-size: 0.88rem;
		font-weight: 700;
	}
	.confirm {
		display: inline-flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.5rem;
		font-weight: 800;
	}
	@media (max-width: 40rem) {
		.bar {
			gap: 0.45rem 0.6rem;
			padding-block: 0.45rem;
		}
		.what {
			min-width: 0;
		}
		.what strong {
			font-size: 1.05rem;
		}
		.what span {
			font-size: 0.8rem;
		}
		.tools {
			width: 100%;
			gap: 0.45rem;
		}
		.tools :global(.btn) {
			min-height: 2.75rem;
			padding-inline: 0.75rem;
			font-size: 0.95rem;
		}
	}
</style>
