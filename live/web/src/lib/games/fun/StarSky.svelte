<!--
	Kejar Bintang's night sky, on a phone and on the host's screen: the sky split between Pasukan
	Harimau and Pasukan Penyu, each half filling with the stars its team has caught and its lit
	constellations; a star falls into a team's half whenever someone catches one.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import { star } from './art';

	interface Team {
		key: string;
		name: string;
		stars: number;
		lit: number;
		players: number;
	}
	let {
		client,
		world,
		big = false
	}: { client: RoomClient; world: { teams: Team[]; constellations: string[]; per: number; myTeam?: string | null; mine?: number }; big?: boolean } = $props();

	let falls = $state<{ key: number; team: string; x: number }[]>([]);
	let n = 0;
	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind !== 'star') return;
			const key = ++n;
			falls = [...falls, { key, team: fx.team, x: 10 + Math.random() * 80 }];
			if (fx.by === undefined || fx.team === world.myTeam) play('pop');
			setTimeout(() => (falls = falls.filter((f) => f.key !== key)), 1400);
		})
	);
	// where each caught star sits in its half: a loose, steady scatter
	const spot = (i: number) => ({ x: 6 + ((i * 37) % 88), y: 8 + ((i * 53) % 70) });
	const leader = $derived(world.teams[0].stars === world.teams[1].stars ? null : world.teams[0].stars > world.teams[1].stars ? world.teams[0].key : world.teams[1].key);
</script>

<div class="sky" class:big>
	{#each world.teams as team (team.key)}
		<section class="half {team.key}" class:mine={team.key === world.myTeam} aria-label="{team.name}: {team.stars} bintang">
			<header>
				<strong>{team.name}</strong>
				<span>{team.stars} bintang{leader === team.key ? ' · mendahului' : ''}</span>
			</header>
			<div class="field">
				{#each Array(Math.min(team.stars, 60)) as _, i (i)}
					{@const p = spot(i)}
					<span class="st" style:left="{p.x}%" style:top="{p.y}%"><Sprite sheet={star(true)} s={big ? 3 : 2} /></span>
				{/each}
				{#each falls.filter((f) => f.team === team.key) as f (f.key)}
					<span class="fall" style:left="{f.x}%"><Sprite sheet={star(true)} s={big ? 4 : 3} /></span>
				{/each}
			</div>
			<ul class="lit" aria-label="Buruj menyala">
				{#each world.constellations.slice(0, Math.max(1, team.lit + 1)) as name, i (name)}
					<li class:on={i < team.lit}>{name}</li>
				{/each}
			</ul>
		</section>
	{/each}
	{#if world.mine !== undefined}<p class="mine-count">Kamu sudah menangkap <strong>{world.mine}</strong> bintang untuk pasukan kamu.</p>{/if}
</div>

<style>
	.sky {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.5rem;
	}
	.half {
		display: grid;
		grid-template-rows: auto minmax(0, 1fr) auto;
		gap: 0.4rem;
		min-height: 15rem;
		padding: 0.6rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #14121f, #2f2c48);
		color: #fff4d8;
		box-shadow: var(--card-shadow);
		image-rendering: pixelated;
	}
	.big .half {
		min-height: 24rem;
	}
	.harimau {
		box-shadow:
			inset 0 0 0 3px #e0742a,
			var(--card-shadow);
	}
	.penyu {
		box-shadow:
			inset 0 0 0 3px #2bb0a6,
			var(--card-shadow);
	}
	.mine {
		outline: 3px solid #ffcf5a;
		outline-offset: 2px;
	}
	header {
		display: grid;
		font-family: var(--font-display);
	}
	header span {
		color: #ffd98a;
		font-size: 0.85rem;
		font-weight: 700;
	}
	.field {
		position: relative;
		overflow: hidden;
	}
	.st {
		position: absolute;
		line-height: 0;
		animation: twinkle 2.4s ease-in-out infinite;
	}
	.st:nth-child(3n) {
		animation-delay: -0.8s;
	}
	.fall {
		position: absolute;
		top: -10%;
		line-height: 0;
		animation: fall 1.3s ease-in forwards;
	}
	.lit {
		display: flex;
		flex-wrap: wrap;
		gap: 0.3rem;
		margin: 0;
		padding: 0;
		list-style: none;
		font-size: 0.75rem;
		font-weight: 800;
	}
	.lit li {
		padding: 0.1rem 0.5rem;
		border-radius: 999px;
		background: rgb(255 255 255 / 0.1);
		color: #a8a4bc;
	}
	.lit li.on {
		background: #ffcf5a;
		color: #3a2306;
	}
	.mine-count {
		grid-column: 1 / -1;
		text-align: center;
		font-weight: 800;
	}
	@keyframes twinkle {
		50% {
			opacity: 0.55;
		}
	}
	@keyframes fall {
		to {
			top: 60%;
			transform: rotate(200deg) scale(0.7);
			opacity: 0.4;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.st,
		.fall {
			animation: none;
		}
	}
</style>
