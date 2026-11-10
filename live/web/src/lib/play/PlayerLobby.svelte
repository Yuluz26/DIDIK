<!-- The student's classroom fills the viewport while the host prepares the game. -->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person, View } from '$lib/types';
	import StickerBar from '$ui/StickerBar.svelte';
	import FullscreenToggle from '$ui/FullscreenToggle.svelte';
	import SoundToggle from '$ui/SoundToggle.svelte';
	import LobbyPlaza from '$lib/worlds/LobbyPlaza.svelte';
	import WorldBadge from '$lib/worlds/WorldBadge.svelte';

	let { client, view, me, people }: { client: RoomClient; view: View; me: Me; people: Person[] } = $props();

	const friends = $derived(people.filter((p) => p.approved));
	const others = $derived(friends.length - 1);
</script>

<main class="lobby">
	<header class="top">
		<div class="room">
			<WorldBadge world={view.room.mode.world} size={44} />
			<div class="room-copy">
				<p class="quiz">{view.room.quizTitle}</p>
				<p class="mode">{view.room.mode.title}</p>
			</div>
		</div>
		<div class="hello">
			<h1>Hai, {me.name}!</h1>
			<p class="wait">Tunggu hos tekan <strong>Mula</strong><span class="dots" aria-hidden="true"><i>.</i><i>.</i><i>.</i></span> <span class="count">{others > 0 ? `${others} kawan sudah sampai` : 'Kamu yang pertama sampai'}</span></p>
		</div>
		<div class="tools"><FullscreenToggle /><SoundToggle /></div>
	</header>

	<section class="classroom" aria-label="Bilik darjah">
		<LobbyPlaza fill people={friends} spots={view.plaza ?? []} {client} me={me.id} onwalk={(x, y) => client.send({ t: 'walk', x, y })} onsit={(seat) => client.send({ t: 'sit', seat })} />
		<details class="instructions"><summary>Cara main</summary><p>{view.room.mode.how}</p></details>
	</section>

	<footer class="stickers">
		<StickerBar compact onsend={(id) => client.send({ t: 'sticker', id })} />
	</footer>
</main>

<style>
	.lobby {
		position: relative;
		display: grid;
		grid-template-rows: auto minmax(0, 1fr);
		width: 100%;
		height: 100dvh;
		min-height: 0;
		overflow: hidden;
		background: #fdf5e7;
	}
	.top {
		z-index: 1;
		display: grid;
		grid-template-columns: minmax(0, 1fr) auto auto;
		align-items: center;
		gap: clamp(.6rem, 2vw, 2rem);
		min-width: 0;
		padding: .65rem clamp(.8rem, 2vw, 2rem);
		border-bottom: 2px solid #d8ac84;
		background: #fff9ed;
	}
	.room { display: flex; align-items: center; gap: .7rem; min-width: 0; }
	.room-copy { min-width: 0; }
	.quiz { display: -webkit-box; overflow: hidden; -webkit-box-orient: vertical; -webkit-line-clamp: 2; line-clamp: 2; margin: 0; font-size: .9rem; font-weight: 900; line-height: 1.2; }
	.mode { margin: .12rem 0 0; color: var(--ink-2); font-size: .76rem; line-height: 1.2; }
	.hello { min-width: 0; text-align: center; }
	.hello h1 { overflow: hidden; margin: 0; font-size: clamp(1.25rem, 2.3vw, 1.65rem); line-height: 1.1; text-overflow: ellipsis; white-space: nowrap; }
	.wait { margin: .15rem 0 0; color: var(--ink-2); font-size: .8rem; line-height: 1.3; }
	.count { margin-left: .55rem; color: var(--brand-ink); font-weight: 900; }
	.tools { display: flex; align-items: center; gap: .45rem; }
	.dots i { font-style: normal; animation: blinkdot 1.4s infinite; }
	.dots i:nth-child(2) { animation-delay: .2s; }
	.dots i:nth-child(3) { animation-delay: .4s; }
	@keyframes blinkdot { 0%, 60%, 100% { opacity: .2; } 30% { opacity: 1; } }
	.classroom { position: relative; min-width: 0; min-height: 0; overflow: hidden; background: #c99061; }
	.classroom :global(.plaza), .classroom :global(.viewport) { border-radius: 0; box-shadow: none; }
	.instructions { position: absolute; z-index: 2; top: .7rem; right: .7rem; width: min(18rem, calc(100% - 1.4rem)); color: #352d2a; }
	.instructions summary { display: block; width: max-content; max-width: 100%; margin-left: auto; padding: .45rem .7rem; border: 2px solid #704f39; border-radius: .6rem; background: #fff5de; box-shadow: 0 2px 0 #704f39; font-size: .76rem; font-weight: 900; cursor: pointer; }
	.instructions summary::-webkit-details-marker { display: none; }
	.instructions summary:focus-visible { outline: 3px solid #295b9b; outline-offset: 3px; }
	.instructions p { margin: .35rem 0 0; padding: .75rem; border: 2px solid #704f39; border-radius: .7rem; background: #fff8e9; box-shadow: 0 4px 14px #49352d44; font-size: .83rem; line-height: 1.4; }
	.stickers { position: absolute; z-index: 1; inset: auto 0 0; display: grid; place-items: center; min-width: 0; padding: .25rem .7rem max(.25rem, env(safe-area-inset-bottom)); background: linear-gradient(transparent, #fff9ed 30%); }
	.stickers :global(.bar) { width: min(30rem, 100%); box-shadow: none; background: transparent; }
	@media (max-width: 760px) {
		.top { grid-template-columns: minmax(0,1fr) auto; gap: .3rem .6rem; padding: .5rem .7rem; }
		.room { gap: .4rem; }
		.quiz { font-size: .8rem; }
		.mode { font-size: .7rem; }
		.hello { grid-column: 1 / -1; grid-row: 2; text-align: left; }
		.hello h1 { font-size: 1.25rem; }
		.wait { font-size: .76rem; }
		.count { display: inline-block; }
		.tools { grid-column: 2; grid-row: 1; gap: .2rem; }
	}
	@media (max-height: 480px) and (min-width: 600px) {
		.top { padding-block: .25rem; }
		.mode, .wait { display: none; }
		.stickers { padding-block: 0; }
	}
	@media (prefers-reduced-motion: reduce) { .dots i { animation: none; } }
</style>
