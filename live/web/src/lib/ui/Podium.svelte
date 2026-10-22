<!--
	The end of a game. Solo games get a podium; team games name the winning team; the games where the
	room builds something together (Kampung Kita, Menara 118) celebrate it, with no ranks at all. The
	server words the team and co-op endings, so this stays the same for every game.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import type { Person, Results } from '$lib/types';
	import { TEAM_COLOURS } from '$lib/names';
	import { confetti } from '$lib/confetti';
	import { play } from '$lib/sound';
	import Avatar from './Avatar.svelte';
	import Chibi from './Chibi.svelte';
	import Didi from './Didi.svelte';

	let {
		results,
		people,
		me = null,
		unit = 'mata'
	}: { results: Results; people: Map<string, Person>; me?: string | null; unit?: string } = $props();

	const top = $derived(results.players.slice(0, 3));
	const rest = $derived(results.players.slice(3));
	const mine = $derived(results.players.find((r) => r.id === me));
	// Podium order on screen: second, first, third.
	const order = $derived([top[1], top[0], top[2]].filter(Boolean));

	onMount(() => {
		play('fanfare');
		const timer = setTimeout(() => confetti({ count: 140, spread: 1.3 }), 700);
		return () => clearTimeout(timer);
	});
</script>

<section class="end">
	{#if results.kind === 'coop'}
		<div class="banner coop">
			<Didi mood="cheer" size={130} />
			<h2>{results.headline}</h2>
			{#if results.note}<p>{results.note}</p>{/if}
		</div>
		<ul class="helpers">
			{#each results.players as row (row.id)}
				{@const person = people.get(row.id)}
				<li class:me={row.id === me}>
					<Avatar animal={person?.avatar} colour={person?.colour} skin={person?.skin} size={52} mood="cheer" bob />
					<span>{row.id === me ? 'Kamu' : person?.name}</span>
					<small>{row.score.toLocaleString('ms-MY')} {unit}</small>
				</li>
			{/each}
		</ul>
	{:else}
		{#if results.kind === 'teams'}
			{@const winner = results.winner ? TEAM_COLOURS[results.winner] : null}
			<div class="banner" style:--team={winner?.colour ?? 'var(--sun)'}>
				<h2>{winner ? `${winner.name} menang!` : 'Seri! Dua pasukan sama hebat.'}</h2>
				<p>
					{#each results.teams ?? [] as team, i (team.key)}{i ? ' · ' : ''}{team.name}: {team.score} {results.teamUnit}{/each}
				</p>
				{#if results.note}<p class="tiebreak">{results.note}</p>{/if}
			</div>
		{/if}

		<ol class="podium" aria-label="Tiga teratas">
			{#each order as row (row.id)}
				{@const person = people.get(row.id)}
				<li class="step step--{row.rank}" class:me={row.id === me}>
					<span class="who">
						{#if row.id === me}<span class="tag">Kamu</span>{/if}
						{#if row.rank === 1}<svg class="crown" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 17l2-10 5 5 2-7 2 7 5-5 2 10z" fill="#ffb627" stroke="#c98400" stroke-width="1.5" stroke-linejoin="round" /></svg>{/if}
						<Chibi animal={person?.avatar} colour={person?.colour} skin={person?.skin} size={row.rank === 1 ? 78 : 64} mood="cheer" />
					</span>
					<span class="block">
						<span class="rank">{row.rank}</span>
						<span class="name">{person?.name}</span>
						<span class="score">{row.score.toLocaleString('ms-MY')} {unit}</span>
					</span>
				</li>
			{/each}
		</ol>

		{#if mine && mine.rank > 3}
			<p class="you">Kamu di tempat ke-{mine.rank} dengan {mine.score.toLocaleString('ms-MY')} {unit}. Syabas!</p>
		{/if}

		{#if rest.length}
			<ol class="rest">
				{#each rest as row (row.id)}
					{@const person = people.get(row.id)}
					<li class:me={row.id === me}>
						<span class="rank">{row.rank}</span>
						<Avatar animal={person?.avatar} colour={person?.colour} skin={person?.skin} size={32} />
						<span class="name">{person?.name}</span>
						<span class="score">{row.score.toLocaleString('ms-MY')}</span>
					</li>
				{/each}
			</ol>
		{/if}
	{/if}
</section>

<style>
	.end {
		display: grid;
		gap: 1.4rem;
	}
	.banner {
		display: grid;
		justify-items: center;
		gap: 0.4rem;
		padding: 1.2rem;
		border-radius: var(--r-lg);
		background: var(--team, var(--sun));
		color: #fff;
		text-align: center;
		box-shadow: var(--lift-low);
		animation: pop-in 600ms var(--spring);
	}
	.banner h2 {
		font-size: var(--fs-h1);
	}
	.banner p {
		font-weight: 800;
	}
	.banner .tiebreak {
		font-weight: 700;
		opacity: 0.9;
	}
	.banner.coop {
		background: var(--brand);
	}
	.podium {
		display: flex;
		align-items: flex-end;
		justify-content: center;
		gap: 0.6rem;
		margin: 0;
		padding: 1.5rem 0 0;
		list-style: none;
	}
	.step {
		position: relative;
		display: grid;
		justify-items: center;
		width: min(11rem, 31%);
		animation: rise-in 700ms var(--spring) both;
	}
	.step--1 {
		animation-delay: 0.5s;
	}
	.step--2 {
		animation-delay: 0.25s;
	}
	/* The winner stands on the block: the feet overlap its top face. */
	.who {
		position: relative;
		z-index: 1;
		display: grid;
		justify-items: center;
		margin-bottom: -1rem;
	}
	.crown {
		width: 2.4rem;
		margin-bottom: -0.5rem;
		animation: wiggle 1.2s ease-in-out 3;
	}
	.tag {
		padding: 0 0.5rem;
		border-radius: var(--r-pill);
		background: var(--sun);
		font-weight: 800;
		font-size: 0.8rem;
	}
	.block {
		display: grid;
		align-content: start;
		justify-items: center;
		gap: 0.1rem;
		width: 100%;
		padding: 1.25rem 0.4rem 0.8rem;
		border-radius: var(--r-md) var(--r-md) 0 0;
		color: #fff;
		text-align: center;
		box-shadow: inset 0 0.9rem 0 rgb(255 255 255 / 0.22);
	}
	.rank {
		font: 600 2rem/1 var(--font-display);
	}
	.block .name {
		max-width: 100%;
		font: 600 clamp(0.9rem, 0.78rem + 0.5vw, 1.1rem) / 1.15 var(--font-display);
		text-wrap: balance;
		overflow-wrap: anywhere;
	}
	.block .score {
		font-weight: 800;
		font-size: 0.85rem;
		opacity: 0.85;
	}
	.step--1 .block {
		min-height: 9.5rem;
		background: var(--sun);
		color: var(--ink);
	}
	.step--2 .block {
		min-height: 7.5rem;
		background: var(--sea);
	}
	.step--3 .block {
		min-height: 6rem;
		background: var(--coral);
	}
	.you {
		padding: 0.8rem 1rem;
		border-radius: var(--r-md);
		background: #fff3cf;
		font-weight: 800;
		text-align: center;
	}
	.rest {
		display: grid;
		gap: 0.4rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.rest li {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		padding: 0.35rem 0.8rem 0.35rem 0.5rem;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: 0 2px 0 var(--line);
	}
	.rest li.me {
		background: #fff3cf;
	}
	.rest .rank {
		width: 1.8rem;
		text-align: center;
		font: 600 1rem var(--font-display);
	}
	.rest .name {
		flex: 1;
		font: 600 1rem var(--font-display);
	}
	.rest .score {
		font-weight: 800;
		color: var(--ink-2);
	}
	.helpers {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(7rem, 1fr));
		gap: 0.8rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.helpers li {
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		font-weight: 800;
		text-align: center;
	}
	.helpers small {
		color: var(--ink-2);
	}
	.helpers .me span {
		padding: 0 0.5rem;
		border-radius: var(--r-pill);
		background: var(--sun);
	}
</style>
