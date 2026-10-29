<!--
	The host's big screen for Legenda: the five worlds as a road, every child placed on the world they
	are in with their hero and hearts, and each boss fight's shared bars as it happens. Every world plays
	its living battlefield (muted), its boss moving; a world with children in it is lit up, so the room
	sees where the class is.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';
	import { keepPlaying } from './livevideo';
	import { HEROES, WORLD_ART, battleBg, heartIcons, heroArt, reducedMotion, sceneArt, sceneStill, symbol, storyArt } from './data';

	interface Row {
		id: string;
		hero: string | null;
		hearts: number;
		step: string;
		world: number;
		cleared: number;
		worlds: number[];
	}

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let { game, people }: { game: any; people: Map<string, Person> } = $props();

	// with reduced motion the cards keep the still painting
	const still = reducedMotion();
	const worlds = $derived((game.world?.worlds ?? []) as { key: string; title: string; boss: string }[]);
	const party = $derived((game.party ?? []) as Row[]);
	const raids = $derived((game.raids ?? []) as { id: string; world: number; hp: number; max: number; members: string[]; round: number }[]);

	const STEP: Record<string, string> = {
		select: 'Memilih wira',
		intro: 'Memasuki dunia',
		travel: 'Mengembara',
		encounter: 'Bertemu musuh',
		question: 'Bertarung',
		result: 'Bertarung',
		clear: 'Musuh tewas',
		unlock: 'Dapat senjata elemen',
		gather: 'Di pintu boss',
		reveal: 'Berdepan boss',
		wait: 'Lawan boss',
		fallen: 'Tumbang',
		worldclear: 'Dunia dibebaskan',
		victory: 'Tamat!'
	};

	function label(row: Row): string {
		if (['question', 'result'].includes(row.step) && row.cleared >= 5) return 'Lawan boss';
		if (['question', 'result', 'encounter', 'travel'].includes(row.step)) return `${STEP[row.step]} · musuh ${Math.min(5, row.cleared + 1)}/5`;
		return STEP[row.step] ?? row.step;
	}
</script>

<section class="legend">
	<ol class="road" aria-label="Lima dunia">
		{#each worlds as w, i (w.key)}
			{@const here = party.filter((p) => p.world === i && p.step !== 'victory')}
			{@const fight = raids.find((r) => r.world === i)}
			<li class="world" class:busy={here.length > 0} style:--bg="url({battleBg(i)})" style:--aura={WORLD_ART[i].aura}>
				{#if !still}
					<video class="alive" {@attach keepPlaying} src={sceneArt(i)} poster={sceneStill(i)} muted loop autoplay playsinline disablepictureinpicture aria-hidden="true"></video>
					<span class="veil" aria-hidden="true"></span>
				{/if}
				<div class="head">
					<img src={symbol(i)} alt="" />
					<div>
						<p class="n">Dunia {i + 1}</p>
						<h3>{w.title}</h3>
						<p class="boss">{w.boss}</p>
					</div>
				</div>
				{#if fight}
					<p class="bars" aria-label="{w.boss}: {fight.hp} daripada {fight.max} bar">
						{#each Array(fight.max) as _, b (b)}<span class:on={b < fight.hp}></span>{/each}
						<small>{fight.members.length} wira</small>
					</p>
				{/if}
				<ul class="kids">
					{#each here as row (row.id)}
						{@const person = people.get(row.id)}
						<li title={person?.name}>
							{#if row.hero}<img class="mini" src={heroArt(row.hero, 'idle')} alt="" />{:else}<Avatar animal={person?.avatar} colour={person?.colour} skin={person?.skin} size={36} />{/if}
						</li>
					{/each}
				</ul>
			</li>
		{/each}
	</ol>

	<table class="list">
		<caption>Pengembara</caption>
		<thead><tr><th>Nama</th><th>Wira</th><th>Di mana</th><th>Hati</th><th>Dunia bebas</th></tr></thead>
		<tbody>
			{#each party as row (row.id)}
				{@const person = people.get(row.id)}
				<tr class:fallen={row.step === 'fallen'}>
					<td><Avatar animal={person?.avatar} colour={person?.colour} skin={person?.skin} size={30} /> {person?.name ?? '…'}</td>
					<td>{HEROES.find((h) => h.key === row.hero)?.name ?? '-'}</td>
					<td>{worlds[row.world]?.title} · {label(row)}</td>
					<td class="hearts">{#each heartIcons(row.hearts) as h, i (i)}<img src={storyArt(`ui/heart_${h}.webp`)} alt="" />{/each}</td>
					<td>{row.worlds.length} / 5</td>
				</tr>
			{/each}
		</tbody>
	</table>
</section>

<style>
	.legend {
		display: grid;
		gap: 1rem;
	}
	.road {
		display: grid;
		grid-template-columns: repeat(5, minmax(0, 1fr));
		gap: 0.6rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.world {
		position: relative;
		display: grid;
		align-content: start;
		gap: 0.5rem;
		min-height: 15rem;
		padding: 0.7rem;
		overflow: hidden;
		border-radius: 14px;
		background:
			linear-gradient(180deg, rgb(8 16 36 / 0.78), rgb(8 16 36 / 0.45)),
			var(--bg) center / cover;
		color: #fff4d8;
		box-shadow:
			inset 0 0 0 2px #d9a441,
			0 8px 18px rgb(0 0 0 / 0.2);
	}
	/* the living battlefield fills the card behind its words, darkened so they read */
	.alive,
	.veil {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
	}
	.alive {
		object-fit: cover;
		object-position: 72% 40%;
	}
	/* a world nobody is in yet stays quieter than the ones being played */
	.world:not(.busy) .alive {
		filter: saturate(0.75) brightness(0.8);
	}
	.veil {
		background: linear-gradient(180deg, rgb(8 16 36 / 0.82), rgb(8 16 36 / 0.2) 60%, rgb(8 16 36 / 0.6));
	}
	.world > :not(.alive, .veil) {
		position: relative;
	}
	.world.busy {
		box-shadow:
			inset 0 0 0 2px #ffd27a,
			0 0 18px color-mix(in srgb, var(--aura) 45%, transparent),
			0 8px 18px rgb(0 0 0 / 0.2);
	}
	.head {
		display: flex;
		gap: 0.5rem;
		align-items: center;
	}
	.head img {
		width: 2.8rem;
		height: 2.8rem;
	}
	.n {
		font: 700 0.75rem var(--font-pixel);
		color: #ffd27a;
	}
	h3 {
		font: 700 1.1rem/1.1 var(--font-pixel);
	}
	.boss {
		font-weight: 700;
		font-size: 0.85rem;
		color: #d9e4ff;
	}
	.bars {
		display: flex;
		align-items: center;
		gap: 0.2rem;
	}
	.bars span {
		flex: 1;
		height: 0.7rem;
		border-radius: 3px;
		border: 1px solid #ffd8a0;
		background: rgb(0 0 0 / 0.5);
	}
	.bars span.on {
		background: linear-gradient(180deg, #ff6b5a, #c8102e);
	}
	.bars small {
		margin-left: 0.3rem;
		font-weight: 800;
	}
	.kids {
		display: flex;
		flex-wrap: wrap;
		gap: 0.2rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.mini {
		width: 2.6rem;
		height: 2.6rem;
		object-fit: contain;
		filter: drop-shadow(0 2px 3px rgb(0 0 0 / 0.5));
	}
	.list {
		width: 100%;
		border-collapse: collapse;
		background: var(--card);
		border-radius: 14px;
		overflow: hidden;
		box-shadow: var(--card-shadow);
	}
	caption {
		padding: 0.6rem;
		font: 700 1.2rem var(--font-display);
		text-align: left;
	}
	th,
	td {
		padding: 0.45rem 0.6rem;
		border-top: 1px solid var(--line);
		text-align: left;
		vertical-align: middle;
		font-weight: 700;
	}
	td:first-child {
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}
	.hearts img {
		width: 1.1rem;
	}
	tr.fallen td {
		color: #b0413e;
	}
	@media (max-width: 900px) {
		.road {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}
</style>
