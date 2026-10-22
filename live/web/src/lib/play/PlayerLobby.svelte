<!--
	A child waiting for the host: the town square with everyone who has joined, where they can walk
	about and send stickers, and what the game will be.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person, View } from '$lib/types';
	import StickerBar from '$ui/StickerBar.svelte';
	import SoundToggle from '$ui/SoundToggle.svelte';
	import LobbyPlaza from '$lib/worlds/LobbyPlaza.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';

	let { client, view, me, people }: { client: RoomClient; view: View; me: Me; people: Person[] } = $props();

	const friends = $derived(people.filter((p) => p.approved));
	const others = $derived(friends.length - 1);
</script>

<main class="lobby wrap">
	<div class="top">
		<p class="quiz">{view.room.quizTitle}</p>
		<SoundToggle />
	</div>

	<section class="hello">
		<h1>Hai, {me.name}!</h1>
		<p class="wait">
			Tunggu hos tekan <strong>Mula</strong><span class="dots" aria-hidden="true"><i>.</i><i>.</i><i>.</i></span>
			<span class="count">{others > 0 ? `${others} kawan sudah sampai` : 'Kamu yang pertama sampai'}</span>
		</p>
	</section>

	<LobbyPlaza people={friends} spots={view.plaza ?? []} {client} me={me.id} onwalk={(x, y) => client.send({ t: 'walk', x, y })} />

	<section class="mode">
		<WorldBadge world={view.room.mode.world} size={76} />
		<div>
			<p class="kind">{view.room.mode.style}</p>
			<h2>{view.room.mode.title}</h2>
			<p class="how">{view.room.mode.how}</p>
		</div>
	</section>

	<div class="stickers">
		<StickerBar onsend={(id) => client.send({ t: 'sticker', id })} />
	</div>
</main>

<style>
	.lobby {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		gap: 1.1rem;
		padding-block: 1rem 7rem;
		max-width: 52rem;
	}
	.top {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}
	.quiz {
		font-weight: 800;
		color: var(--ink-2);
	}
	.hello {
		display: grid;
		gap: 0.3rem;
	}
	.hello h1 {
		font-size: var(--fs-h2);
	}
	.wait {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		gap: 0 0.9rem;
		font-size: 1.05rem;
		color: var(--ink-2);
	}
	.count {
		font-size: 0.95rem;
		font-weight: 800;
		color: var(--brand);
	}
	.dots i {
		font-style: normal;
		animation: blinkdot 1.4s infinite;
	}
	.dots i:nth-child(2) {
		animation-delay: 0.2s;
	}
	.dots i:nth-child(3) {
		animation-delay: 0.4s;
	}
	@keyframes blinkdot {
		0%,
		60%,
		100% {
			opacity: 0.2;
		}
		30% {
			opacity: 1;
		}
	}
	.mode {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem 1.2rem;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	.mode h2 {
		font-size: 1.5rem;
	}
	.how {
		margin-top: 0.25rem;
		color: var(--ink-2);
	}
	.stickers {
		position: fixed;
		left: 50%;
		bottom: max(0.8rem, env(safe-area-inset-bottom, 0px));
		translate: -50% 0;
		width: min(30rem, calc(100% - 2rem));
		z-index: 10;
	}
</style>
