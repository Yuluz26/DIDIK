<!--
	Kuiz Interaktif on the host's big screen: the whole class on Didi's trail. One lane for each child,
	with a stop for every question coloured by the stars earned there, Didi-style progress and the stars
	so far. Those furthest along are at the top; those who have finished wear a crown.
-->
<script lang="ts">
	import { flip } from 'svelte/animate';
	import type { Person } from '$lib/types';
	import Avatar from '$ui/Avatar.svelte';
	import Sticker from '$ui/Sticker.svelte';

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let { game, people }: { game: any; people: Map<string, Person> } = $props();

	interface Kid {
		id: string;
		stars: number[];
		done: boolean;
	}

	const total = $derived<number>(game.world?.total ?? 0);
	const kids = $derived<Kid[]>(
		[...((game.world?.kids ?? []) as Kid[])]
			.filter((k) => people.has(k.id))
			.sort((a, b) => b.stars.length - a.stars.length || sum(b.stars) - sum(a.stars))
	);
	const finished = $derived(kids.filter((k) => k.done).length);
	const sum = (list: number[]) => list.reduce((a, b) => a + b, 0);
</script>

<section class="class-trail" aria-labelledby="ik-host-title">
	<header>
		<h2 id="ik-host-title">Denai Didi</h2>
		<p><strong>{finished}</strong> daripada {kids.length} sudah sampai ke hujung · {total} soalan</p>
	</header>
	{#if !kids.length}
		<p class="empty">Belum ada pemain di denai.</p>
	{:else}
		<ol class="lanes">
			{#each kids as kid (kid.id)}
				{@const person = people.get(kid.id)}
				<li class="lane" class:done={kid.done} animate:flip={{ duration: 400 }}>
					<span class="who">
						<span class="face"><Avatar animal={person?.avatar} colour={person?.colour} skin={person?.skin} size={36} /></span>
						<span class="name">{person?.name ?? 'Pemain'}</span>
						{#if kid.done}<Sticker key="mahkota" size={24} alt="Sudah sampai" />{/if}
					</span>
					<span class="stops" style:--n={total} aria-label="{kid.stars.length} daripada {total} soalan dijawab">
						{#each Array.from({ length: total }, (_, i) => i) as i (i)}
							<span class="stop s{kid.stars[i] ?? 'x'}" class:now={!kid.done && i === kid.stars.length}></span>
						{/each}
					</span>
					<span class="count"><Sticker key="bintang" size={22} alt="" /> {sum(kid.stars)}</span>
				</li>
			{/each}
		</ol>
		<p class="legend" aria-hidden="true">
			<span><i class="stop s3"></i> 3 bintang</span>
			<span><i class="stop s2"></i> 2</span>
			<span><i class="stop s1"></i> 1</span>
			<span><i class="stop s0"></i> belum tepat</span>
		</p>
	{/if}
</section>

<style>
	.class-trail {
		display: grid;
		gap: 0.8rem;
		padding: 1.1rem 1.2rem;
		border-radius: 26px;
		background: linear-gradient(180deg, #fff0f7, #f1ecff 50%, #e9f8ff);
		box-shadow: 0 5px 0 #e6dbf6;
	}
	header {
		display: flex;
		flex-wrap: wrap;
		align-items: baseline;
		justify-content: space-between;
		gap: 0.3rem 1rem;
	}
	h2 {
		font: 600 1.5rem 'Fredoka Variable', ui-rounded, sans-serif;
		color: #5b3e99;
	}
	header p {
		color: #5a4d70;
		font-weight: 800;
	}
	.empty {
		padding: 1.5rem;
		color: #5a4d70;
		font-weight: 800;
		text-align: center;
	}
	.lanes {
		display: grid;
		gap: 0.45rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.lane {
		display: grid;
		grid-template-columns: minmax(8rem, 13rem) minmax(0, 1fr) auto;
		align-items: center;
		gap: 0.8rem;
		padding: 0.35rem 0.8rem 0.35rem 0.35rem;
		border-radius: 999px;
		background: #fff;
		box-shadow: 0 3px 0 #ece3f8;
	}
	.lane.done {
		background: #fffbe6;
		box-shadow: 0 3px 0 #f1d98b;
	}
	.who {
		display: flex;
		align-items: center;
		gap: 0.45rem;
		min-width: 0;
	}
	.face {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.3rem;
		height: 2.3rem;
		overflow: hidden;
		border-radius: 50%;
		background: #f5ecff;
	}
	.name {
		overflow: hidden;
		font-weight: 800;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.stops {
		display: grid;
		grid-template-columns: repeat(var(--n), minmax(0, 1fr));
		gap: 3px;
	}
	.stop {
		display: block;
		height: 0.8rem;
		border-radius: 999px;
		background: #ede6f6;
	}
	.stop.s3 {
		background: #ffc93c;
	}
	.stop.s2 {
		background: #ff9fc3;
	}
	.stop.s1 {
		background: #9fd0ff;
	}
	.stop.s0 {
		background: #cfc6dd;
	}
	.stop.now {
		background: #fff;
		box-shadow: inset 0 0 0 2px #b98cff;
		animation: now 1.2s ease-in-out infinite;
	}
	.count {
		display: inline-flex;
		align-items: center;
		gap: 0.25rem;
		font: 600 1.15rem 'Fredoka Variable', ui-rounded, sans-serif;
	}
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 0.4rem 1rem;
		color: #5a4d70;
		font-size: 0.85rem;
		font-weight: 800;
	}
	.legend span {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
	}
	.legend .stop {
		width: 1.4rem;
	}
	@keyframes now {
		50% {
			box-shadow: inset 0 0 0 2px #b98cff, 0 0 0 4px rgb(185 140 255 / 0.25);
		}
	}
	@media (max-width: 640px) {
		.lane {
			grid-template-columns: minmax(0, 1fr) auto;
			border-radius: 20px;
		}
		.stops {
			grid-column: 1 / -1;
			grid-row: 2;
		}
	}
</style>
