<!-- A child waiting for the host: their animal, the game's rules, friends arriving, stickers. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person, View } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';
	import StickerBar from '$ui/StickerBar.svelte';
	import SoundToggle from '$ui/SoundToggle.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';
	import PlayerWall from './PlayerWall.svelte';
	import Stickers from './Stickers.svelte';

	let { client, view, me, people }: { client: RoomClient; view: View; me: Me; people: Person[] } = $props();

	let wallEl = $state<HTMLElement>();
	const friends = $derived(people.filter((p) => p.approved));
</script>

<main class="lobby wrap">
	<div class="top">
		<p class="quiz">{view.room.quizTitle}</p>
		<SoundToggle />
	</div>

	<section class="hello">
		<Avatar animal={me.avatar} colour={me.colour} size={120} bob mood="cheer" />
		<h1>Hai, {me.name}!</h1>
		<p class="wait">Tunggu hos tekan <strong>Mula</strong><span class="dots" aria-hidden="true"><i>.</i><i>.</i><i>.</i></span></p>
	</section>

	<section class="mode">
		<WorldBadge world={view.room.mode.world} size={76} />
		<div>
			<p class="style">{view.room.mode.style}</p>
			<h2>{view.room.mode.title}</h2>
			<p class="how">{view.room.mode.how}</p>
		</div>
	</section>

	<section class="friends" bind:this={wallEl}>
		<h2>Dalam bilik ({friends.length})</h2>
		<PlayerWall people={friends} me={me.id} size={56} />
		<Stickers {client} within={wallEl} />
	</section>

	<div class="stickers">
		<StickerBar onsend={(id) => client.send({ t: 'sticker', id })} />
	</div>
</main>

<style>
	.lobby {
		display: grid;
		gap: 1.4rem;
		padding-block: 1rem 7rem;
		max-width: 46rem;
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
		justify-items: center;
		gap: 0.5rem;
		text-align: center;
	}
	.hello h1 {
		font-size: var(--fs-h1);
	}
	.wait {
		font-size: 1.1rem;
		color: var(--ink-2);
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
	.style {
		color: var(--brand);
		font-weight: 800;
		font-size: 0.85rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
	}
	.how {
		margin-top: 0.25rem;
		color: var(--ink-2);
	}
	.friends {
		position: relative;
		display: grid;
		gap: 0.8rem;
	}
	.friends h2 {
		font-size: 1.2rem;
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
