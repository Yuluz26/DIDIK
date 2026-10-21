<!--
	The end of a game. Solo games get a podium; Pasukan Warna names the winning team; Kampung Kita
	celebrates what the room built together, with no ranks at all.
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import type { Person, Results } from '$lib/types';
	import { TEAM_COLOURS } from '$lib/names';
	import { confetti } from '$lib/confetti';
	import { play } from '$lib/sound';
	import Avatar from './Avatar.svelte';
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
			<h2>{results.complete ? 'Kampung kita siap!' : `Kita bina ${results.built} daripada ${results.total} bangunan!`}</h2>
			<p>{results.decorations ? `Dengan ${results.decorations} hiasan dari semua.` : 'Terima kasih semua pembina.'}</p>
		</div>
		<ul class="helpers">
			{#each results.players as row (row.id)}
				{@const person = people.get(row.id)}
				<li class:me={row.id === me}>
					<Avatar animal={person?.avatar} colour={person?.colour} size={52} mood="cheer" bob />
					<span>{row.id === me ? 'Kamu' : person?.name}</span>
					<small>{row.score} bahan</small>
				</li>
			{/each}
		</ul>
	{:else}
		{#if results.kind === 'teams'}
			{@const winner = results.winner ? TEAM_COLOURS[results.winner] : null}
			<div class="banner" style:--team={winner?.colour ?? 'var(--sun)'}>
				<h2>{winner ? `${winner.name} menang!` : 'Seri! Dua pasukan sama hebat.'}</h2>
				<p>
					{#each results.teams ?? [] as team, i (team.key)}{i ? ' · ' : ''}{team.name}: {team.cells} petak{/each}
				</p>
			</div>
		{/if}

		<ol class="podium" aria-label="Tiga teratas">
			{#each order as row (row.id)}
				{@const person = people.get(row.id)}
				<li class="step step--{row.rank}" class:me={row.id === me}>
					{#if row.rank === 1}<svg class="crown" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 17l2-10 5 5 2-7 2 7 5-5 2 10z" fill="#ffb627" stroke="#c98400" stroke-width="1.5" stroke-linejoin="round" /></svg>{/if}
					<Avatar animal={person?.avatar} colour={person?.colour} size={row.rank === 1 ? 92 : 72} mood="cheer" />
					<span class="name">{person?.name}</span>
					<span class="score">{row.score.toLocaleString('ms-MY')} {unit}</span>
					<span class="block"><span>{row.rank}</span></span>
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
						<Avatar animal={person?.avatar} colour={person?.colour} size={32} />
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
		gap: 0.25rem;
		width: min(11rem, 31%);
		animation: rise-in 700ms var(--spring) both;
	}
	.step--1 {
		animation-delay: 0.5s;
	}
	.step--2 {
		animation-delay: 0.25s;
	}
	.crown {
		position: absolute;
		top: -1.5rem;
		width: 2.6rem;
		animation: wiggle 1.2s ease-in-out 3;
	}
	.name {
		max-width: 100%;
		font: 600 clamp(0.95rem, 0.8rem + 0.6vw, 1.15rem) / 1.15 var(--font-display);
		text-align: center;
		text-wrap: balance;
		overflow-wrap: anywhere;
	}
	.me .name {
		padding: 0 0.5rem;
		border-radius: var(--r-pill);
		background: var(--sun);
	}
	.score {
		font-weight: 800;
		color: var(--ink-2);
	}
	.block {
		display: grid;
		place-items: center;
		width: 100%;
		border-radius: var(--r-md) var(--r-md) 0 0;
		color: #fff;
		font: 600 2.2rem var(--font-display);
	}
	.step--1 .block {
		height: 8.5rem;
		background: var(--sun);
		color: var(--ink);
	}
	.step--2 .block {
		height: 6rem;
		background: var(--sea);
	}
	.step--3 .block {
		height: 4.5rem;
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
		font-size: 1rem;
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
