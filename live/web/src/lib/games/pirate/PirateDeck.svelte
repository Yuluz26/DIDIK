<!--
	Peti Lanun on a phone: the deck with three chests. After a right answer the player picks one; the
	chosen chest opens, then the other two. A chest that lets you raid or swap asks whose ship, with
	shielded ships greyed out and their shield counting down. When someone raids this ship, it says
	who and for how much.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { play } from '$lib/sound';
	import Avatar from '$ui/Avatar.svelte';
	import Stage3D from '$lib/three/Stage3D.svelte';
	import type { DeckWorld, Found } from './deck';
	import { chestLabel } from './lines';

	interface Target {
		id: string;
		gold: number;
		shieldUntil: number | null;
	}
	interface Seen {
		shieldUntil?: number | null;
		opened?: number;
		chests?: Found[];
		pending?: 'curi' | 'tukar';
		targets?: Target[];
	}

	let { client, world: seen, step, people }: { client: RoomClient; world: Seen; step: string; people: Map<string, Person> } = $props();

	let world = $state<DeckWorld | null>(null);
	let now = $state(Date.now());
	let raided = $state<string | null>(null);

	const create = () => import('./deck').then(({ DeckWorld }) => new DeckWorld());

	$effect(() => {
		world?.set(seen.opened ?? null, seen.chests ?? null, step === 'chest');
	});

	// Shields count down on screen (the server sends when they drop, in its own clock).
	$effect(() => {
		const timer = setInterval(() => (now = Date.now() + client.offset), 500);
		return () => clearInterval(timer);
	});

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind !== 'plunder') return;
			const by = people.get(String(fx.by))?.name ?? 'Seseorang';
			raided = fx.swap ? `${by} bertukar emas dengan kapal kamu!` : `${by} merampas ${fx.amount} emas daripada kamu!`;
			play('steal');
			setTimeout(() => (raided = null), 4000);
		})
	);

	const secondsLeft = (until: number | null | undefined) => (until ? Math.max(0, Math.ceil((until - now) / 1000)) : 0);
	const myShield = $derived(secondsLeft(seen.shieldUntil));
	const choosable = $derived((seen.targets ?? []).filter((t) => secondsLeft(t.shieldUntil) === 0));

	function open(index: number) {
		play('pop');
		client.send({ t: 'open', chest: index });
	}
	function choose(id: string) {
		play('steal');
		client.send({ t: 'target', player: id });
	}

	const label = $derived(
		seen.opened !== undefined && seen.chests
			? `Tiga peti terbuka. Kamu pilih peti ${seen.opened + 1}: ${chestLabel(seen.chests[seen.opened])}.`
			: step === 'chest'
				? 'Tiga peti tertutup di atas geladak. Pilih satu.'
				: 'Geladak kapal kamu dengan tiga peti.'
	);
</script>

<div class="deck">
	{#if raided}<p class="raided" role="alert">{raided}</p>{/if}
	{#if myShield}<p class="shield">Kapal kamu berperisai: {myShield} saat lagi</p>{/if}

	<div class="stage">
		<Stage3D {create} bind:world {label}>
			{#snippet fallback()}
				<p class="plain">{step === 'chest' ? 'Pilih satu peti.' : 'Jawab soalan untuk membuka peti.'}</p>
			{/snippet}
			{#if seen.opened !== undefined && seen.chests}
				<div class="labels" aria-hidden="true">
					{#each seen.chests as found, i (i)}
						<span class="found found--{found.kind}" class:picked={i === seen.opened}>{chestLabel(found)}</span>
					{/each}
				</div>
			{/if}
		</Stage3D>
		{#if step === 'chest'}
			<div class="choose">
				{#each [0, 1, 2] as i (i)}
					<button type="button" class="pick" onclick={() => open(i)} aria-label="Buka peti {i + 1}">
						<span>Peti {i + 1}</span>
					</button>
				{/each}
			</div>
		{/if}
	</div>

	{#if step === 'chest'}
		<p class="hint">Pilih satu peti. Dua lagi akan dibuka selepas itu.</p>
	{:else if step === 'target' && seen.targets}
		<section class="targets" aria-labelledby="target-title">
			<h2 id="target-title">{seen.pending === 'curi' ? 'Rampas suku emas daripada siapa?' : 'Tukar semua emas dengan siapa?'}</h2>
			<ul>
				{#each seen.targets as target (target.id)}
					{@const person = people.get(target.id)}
					{@const shield = secondsLeft(target.shieldUntil)}
					<li>
						<button type="button" class="target" disabled={shield > 0} onclick={() => choose(target.id)}>
							<Avatar animal={person?.avatar} colour={person?.colour} skin={person?.skin} size={36} />
							<span class="who">{person?.name ?? 'Pemain'}</span>
							<span class="gold">{shield ? `Perisai ${shield} s` : `${target.gold} emas`}</span>
						</button>
					</li>
				{/each}
			</ul>
			{#if seen.pending === 'tukar'}
				<button type="button" class="btn btn--plain keep" onclick={() => client.send({ t: 'keep' })}>Tak jadi tukar</button>
			{:else if !choosable.length}
				<button type="button" class="btn btn--sun keep" onclick={() => client.send({ t: 'keep' })}>Semua berperisai: ambil 25 emas</button>
			{/if}
		</section>
	{/if}
</div>

<style>
	.deck {
		display: grid;
		gap: 0.8rem;
	}
	.stage {
		position: relative;
		height: clamp(13rem, 36svh, 20rem);
		border-radius: var(--r-lg);
		overflow: hidden;
		--stage-bg: #7c5f7d;
	}
	.labels {
		position: absolute;
		inset: 12% 4% auto;
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		justify-items: center;
	}
	.found {
		padding: 0.15rem 0.6rem;
		border-radius: var(--r-pill);
		border: 2px solid #071418;
		background: #0f1f24;
		color: #fff;
		font: 600 1rem var(--font-display);
		opacity: 0.75;
		animation: rise-in 420ms var(--ease-out) both;
		animation-delay: 550ms;
	}
	.found.picked {
		opacity: 1;
		font-size: 1.25rem;
		background: var(--sun);
		color: var(--on-bright);
		animation-delay: 250ms;
	}
	.found--ribut.picked {
		background: #9fb2c8;
	}
	.found--curi.picked {
		background: var(--coral);
		color: #fff;
	}
	.found--tukar.picked {
		background: var(--sky);
		color: #fff;
	}
	/* Each button covers its chest: the whole chest is the target. */
	.choose {
		position: absolute;
		inset: 34% 0 0;
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0.5rem;
		padding: 0 0.6rem 0.6rem;
	}
	.pick {
		display: grid;
		place-items: end center;
		padding: 0.5rem;
		border: 1.5px solid rgb(255 255 255 / 0.35);
		border-radius: var(--r-md);
		background: rgb(255 255 255 / 0.06);
		color: #fff;
		font: 600 1rem var(--font-display);
		cursor: pointer;
		transition:
			background var(--t-state),
			transform var(--t-press) var(--ease-out);
	}
	.pick span {
		padding: 0.1rem 0.6rem;
		border-radius: var(--r-pill);
		border: 2px solid #071418;
		background: #0f1f24;
	}
	.pick:hover {
		background: rgb(255 214 120 / 0.18);
	}
	.pick:active {
		transform: scale(0.96);
	}
	.hint {
		color: var(--ink-2);
		font-weight: 700;
		text-align: center;
	}
	.raided,
	.shield {
		padding: 0.55rem 0.9rem;
		border-radius: var(--r-md);
		font-weight: 800;
		text-align: center;
	}
	.raided {
		background: var(--almost-soft);
		color: var(--on-almost-soft);
		animation: shake 420ms ease-in-out;
	}
	.shield {
		background: var(--brand-soft);
		color: var(--on-brand-soft);
	}
	.targets {
		display: grid;
		gap: 0.6rem;
		padding: 1rem;
		border-radius: var(--r-lg);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	.targets h2 {
		font-size: 1.25rem;
	}
	.targets ul {
		display: grid;
		gap: 0.45rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.target {
		display: flex;
		align-items: center;
		gap: 0.7rem;
		width: 100%;
		min-height: 3.2rem;
		padding: 0.4rem 0.8rem;
		border: 2px solid var(--line);
		border-radius: var(--r-md);
		background: var(--paper-2);
		color: var(--ink);
		font-weight: 800;
		text-align: left;
		cursor: pointer;
		transition: border-color var(--t-state);
	}
	.target:not(:disabled):hover {
		border-color: var(--sun);
	}
	.target:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
	.who {
		flex: 1;
		min-width: 0;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	.gold {
		color: var(--sun);
		font-variant-numeric: tabular-nums;
	}
	.target:disabled .gold {
		color: var(--ink-3);
	}
	.keep {
		justify-self: start;
	}
	.plain {
		padding: 2rem 1rem;
		font-weight: 800;
		text-align: center;
	}
</style>
