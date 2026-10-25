<!--
	Sepakan Penalti's stadium with the scoreboard over it, on the big screen and on phones. At each
	reveal the round's two kicks play one after the other; the score and the shootout dots only
	change when each ball arrives, so the screen never gives a result away before the kick.
-->
<script lang="ts">
	import { TEAM_COLOURS } from '$lib/names';
	import { play } from '$lib/sound';
	import Stage3D from '$lib/three/Stage3D.svelte';
	import type { Kick, StadiumWorld } from './stadium';

	interface Match {
		teams: { key: string; name: string; goals: number; players: number }[];
		rounds: { kicks: Kick[] }[];
		myTeam?: string | null;
	}

	let { match, stage, index, view }: { match: Match; stage: string; index: number; view: 'host' | 'phone' } = $props();

	// The same moments as the 3D kick (stadium.ts): contact at 0.9 s, the ball arrives at 1.45 s,
	// and each kick takes 3.1 s.
	const KICK = 3100;
	const CONTACT = 900;
	const ARRIVE = 1450;
	const CALLS = { gol: 'GOL!', selamat: 'Diselamatkan!', tiang: 'Kena tiang!', luar: 'Terlepas!' } as const;

	let world = $state<StadiumWorld | null>(null);
	let called = $state(2);
	let call = $state<{ text: string; team: string; good: boolean } | null>(null);
	let shown = '';

	const KITS = {
		harimau: { shirt: TEAM_COLOURS.harimau.colour, keeper: TEAM_COLOURS.harimau.deep },
		penyu: { shirt: TEAM_COLOURS.penyu.colour, keeper: TEAM_COLOURS.penyu.deep }
	};
	const create = () => import('./stadium').then(({ StadiumWorld }) => new StadiumWorld(view, KITS));

	const round = $derived(stage === 'reveal' && match.rounds.length === index + 1 ? match.rounds[index] : null);
	const nextTeam = $derived(match.rounds.length % 2 ? 'penyu' : 'harimau');

	// Start the round's kicks once per reveal; between rounds, the next kicker waits at the spot.
	$effect(() => {
		const key = round ? `play:${index}` : `idle:${match.rounds.length}`;
		if (!world || key === shown) return;
		shown = key;
		if (!round) {
			called = 2;
			call = null;
			world.idle(nextTeam);
			return;
		}
		called = 0;
		world.play(round.kicks, index);
	});

	// Sounds, the call over the picture and the score, timed with the kicks.
	$effect(() => {
		if (!round) return;
		const kicks = round.kicks;
		const timers: ReturnType<typeof setTimeout>[] = [];
		kicks.forEach((kick, k) => {
			timers.push(setTimeout(() => play('kick'), k * KICK + CONTACT));
			timers.push(
				setTimeout(() => {
					called = k + 1;
					call = { text: CALLS[kick.result], team: kick.team, good: kick.result === 'gol' };
					play(kick.result === 'gol' ? 'goal' : 'almost');
				}, k * KICK + ARRIVE)
			);
			timers.push(setTimeout(() => (call = null), k * KICK + ARRIVE + 1400));
		});
		return () => timers.forEach(clearTimeout);
	});

	// Kicks of this reveal that have not landed yet are left out of the score and the dots.
	const pending = $derived(round ? round.kicks.slice(called) : []);
	const goals = (team: string) =>
		(match.teams.find((t) => t.key === team)?.goals ?? 0) - pending.filter((k) => k.team === team && k.result === 'gol').length;
	const dots = (team: string) =>
		match.rounds.flatMap((r, i) => r.kicks.filter((k) => k.team === team && !(i === match.rounds.length - 1 && pending.includes(k))).map((k) => k.result === 'gol'));
	const teamOf = (key: string) => TEAM_COLOURS[key];
	const mine = $derived(match.myTeam ? teamOf(match.myTeam) : null);
	const label = $derived(
		`Sepakan penalti. ${match.teams.map((t) => `${t.name} ${goals(t.key)}`).join(', ')}.${call ? ` ${call.text}` : ''}`
	);
</script>

<div class="penalty penalty--{view}">
	<Stage3D {create} bind:world {label}>
		{#snippet fallback()}
			<p class="plain">
				{#if round}{#each round.kicks.slice(0, called) as kick (kick.team)}{teamOf(kick.team).name}: {CALLS[kick.result]} {/each}{:else}Sepakan seterusnya: {teamOf(nextTeam).name}{/if}
			</p>
		{/snippet}
		{#if call}
			<p class="call" class:good={call.good} style:--team={teamOf(call.team).colour}>
				<strong>{call.text}</strong>
				<span>{teamOf(call.team).name}</span>
			</p>
		{/if}
		{#if view === 'phone' && mine}
			<p class="mine" style:--team={mine.colour}>Kamu: {mine.name}</p>
		{/if}
	</Stage3D>
	<div class="score" aria-hidden="true">
		{#each match.teams as team, i (team.key)}
			<div class="side" class:right={i === 1} style:--team={teamOf(team.key).colour}>
				<span class="name">{team.name.replace('Pasukan ', '')}</span>
				<span class="goals">{goals(team.key)}</span>
				<span class="dots">
					{#each dots(team.key).slice(-8) as scored, d (d)}<i class:scored></i>{/each}
				</span>
			</div>
			{#if i === 0}<span class="dash">–</span>{/if}
		{/each}
	</div>
</div>

<style>
	.penalty {
		position: relative;
		height: 100%;
		border-radius: inherit;
		--stage-bg: #173a4f;
	}
	.penalty--phone {
		height: clamp(12rem, 32svh, 17rem);
		border-radius: var(--r-lg);
		overflow: hidden;
	}
	.score {
		position: absolute;
		top: 0.7rem;
		left: 50%;
		translate: -50% 0;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.35rem 0.8rem;
		border-radius: var(--r-md);
		border: 2px solid #050f13;
		background: #0b191f;
		color: #fff;
		pointer-events: none;
	}
	.side {
		display: grid;
		grid-template-columns: auto auto;
		grid-template-areas: 'name goals' 'dots dots';
		align-items: center;
		column-gap: 0.55rem;
	}
	.side.right {
		grid-template-columns: auto auto;
		grid-template-areas: 'goals name' 'dots dots';
	}
	.name {
		grid-area: name;
		padding-left: 0.5rem;
		border-left: 4px solid var(--team);
		font: 600 1rem var(--font-display);
	}
	.side.right .name {
		padding: 0 0.5rem 0 0;
		border-left: 0;
		border-right: 4px solid var(--team);
	}
	.goals {
		grid-area: goals;
		font: 600 1.7rem/1 var(--font-display);
		font-variant-numeric: tabular-nums;
	}
	.dash {
		align-self: start;
		font: 600 1.4rem/1 var(--font-display);
		color: #9fb3b4;
		margin-top: 0.2em;
	}
	.dots {
		grid-area: dots;
		display: flex;
		gap: 3px;
		min-height: 9px;
		margin-top: 0.2rem;
	}
	.side.right .dots {
		justify-content: flex-end;
	}
	.dots i {
		width: 9px;
		height: 9px;
		border-radius: 1px;
		border: 2px solid #9fb3b4;
	}
	.dots i.scored {
		border-color: var(--team);
		background: var(--team);
	}
	.call {
		position: absolute;
		left: 50%;
		bottom: 9%;
		translate: -50% 0;
		display: grid;
		justify-items: center;
		padding: 0.5rem 1.4rem 0.6rem;
		border-radius: var(--r-md);
		border: 2px solid #050f13;
		background: #0b191f;
		color: #fff;
		text-align: center;
		animation: pop-in 300ms steps(5);
	}
	.call strong {
		font: 600 clamp(1.6rem, 1.2rem + 2vw, 3rem) / 1.05 var(--font-display);
	}
	.call.good strong {
		color: var(--team);
	}
	.call span {
		font-weight: 700;
		font-size: 0.95rem;
		color: #c9d6d3;
	}
	.mine {
		position: absolute;
		left: 0.6rem;
		bottom: 0.6rem;
		padding: 0.15rem 0.6rem;
		border-radius: var(--r-pill);
		background: var(--team);
		color: #fff;
		font: 600 0.9rem var(--font-display);
	}
	.plain {
		padding: 3.6rem 1rem 1rem;
		font-weight: 700;
		text-align: center;
	}
	.penalty--host .score {
		top: 1rem;
		padding: 0.5rem 1.1rem;
	}
	.penalty--host .goals {
		font-size: 2.3rem;
	}
	.penalty--host .name {
		font-size: 1.25rem;
	}
</style>
