<!--
	A child in Hutan Misteri: walk with the stick or the arrow keys, open chests to answer questions,
	collect keys, then find the gate. The map follows your own animal.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Me, Person } from '$lib/types';
	import { play } from '$lib/sound';
	import { confetti } from '$lib/confetti';
	import Answer from '$lib/questions/Answer.svelte';
	import Feedback from '$lib/questions/Feedback.svelte';
	import QuestionCard from '$lib/questions/QuestionCard.svelte';
	import Countdown from '$ui/Countdown.svelte';
	import Icon from '$ui/Icon.svelte';
	import Timer from '$ui/Timer.svelte';
	import Hud from '../Hud.svelte';
	import ForestMap from './ForestMap.svelte';
	import Joystick from './Joystick.svelte';
	import { livePositions } from './positions.svelte';

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	let { client, game, me, people }: { client: RoomClient; game: any; me: Me; people: Map<string, Person> } = $props();

	const world = $derived(game.world);
	const seat = $derived(game.seat ?? {});
	// The room connection never changes for the life of this screen.
	// svelte-ignore state_referenced_locally
	const positions = livePositions(client);
	const mine = $derived(positions.all[me.id]);
	const asking = $derived(seat.step === 'question' || seat.step === 'result');
	const escaped = $derived((world?.escaped ?? []).includes(me.id));
	const keys = $derived(world?.keys ?? 0);
	const need = $derived(world?.need ?? 5);
	const order = $derived((world?.escaped ?? []).indexOf(me.id) + 1);

	const distance = (a: { x: number; y: number }, b: { x: number; y: number }) => Math.hypot(a.x - b.x, a.y - b.y);
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	const nearChest = $derived(mine && world ? world.chests.find((c: any) => c.state === 'closed' && distance(c, mine) <= 1.3) : undefined);
	const nearGate = $derived(!!mine && !!world && keys >= need && distance(world.gate, mine) <= 1.85);

	let hint = $state('');
	let lastKeys = 0;
	let sent = { dx: 0, dy: 0 };
	const held = new Set<string>();

	$effect(() => {
		if (keys > lastKeys) {
			play('key');
			confetti({ count: 30 });
		}
		lastKeys = keys;
	});

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind === 'escaped' && fx.player === me.id) {
				play('fanfare');
				confetti({ count: 140, spread: 1.3 });
			}
		})
	);

	function move(dx: number, dy: number) {
		if (asking || escaped) {
			dx = 0;
			dy = 0;
		}
		if (dx === sent.dx && dy === sent.dy) return;
		sent = { dx, dy };
		client.send({ t: 'move', dx, dy });
	}

	const KEYS: Record<string, [number, number]> = {
		ArrowUp: [0, -1], w: [0, -1], W: [0, -1],
		ArrowDown: [0, 1], s: [0, 1], S: [0, 1],
		ArrowLeft: [-1, 0], a: [-1, 0], A: [-1, 0],
		ArrowRight: [1, 0], d: [1, 0], D: [1, 0]
	};

	function fromKeys() {
		let dx = 0;
		let dy = 0;
		for (const key of held) {
			dx += KEYS[key][0];
			dy += KEYS[key][1];
		}
		move(Math.sign(dx), Math.sign(dy));
	}

	function down(event: KeyboardEvent) {
		if ((event.target as HTMLElement)?.closest('input, textarea') || asking) return;
		if (KEYS[event.key]) {
			event.preventDefault();
			held.add(event.key);
			fromKeys();
		} else if ((event.key === ' ' || event.key === 'Enter' || event.key === 'e') && !asking) {
			act();
		}
	}

	function up(event: KeyboardEvent) {
		if (KEYS[event.key]) {
			held.delete(event.key);
			fromKeys();
		}
	}

	function act() {
		if (nearGate) client.send({ t: 'escape' });
		else if (nearChest) open(nearChest.id);
	}

	function open(id: number) {
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		const chest = world.chests.find((c: any) => c.id === id);
		if (!mine || !chest) return;
		if (chest.state === 'locked') {
			hint = 'Peti ini berkunci sebentar. Cuba peti lain dahulu.';
			return;
		}
		if (distance(chest, mine) > 1.3) {
			hint = 'Jalan lebih dekat ke peti dahulu.';
			return;
		}
		hint = '';
		move(0, 0);
		play('pop');
		client.send({ t: 'open', chest: id });
	}

	$effect(() => {
		if (!hint) return;
		const timer = setTimeout(() => (hint = ''), 2200);
		return () => clearTimeout(timer);
	});
</script>

<svelte:window onkeydown={down} onkeyup={up} onblur={() => (held.clear(), move(0, 0))} />

<Hud {me} score={game.score} rank={game.rank}>
	<span class="keys" aria-label="{keys} daripada {need} kunci">
		{#each Array(need) as _, i (i)}
			<svg viewBox="0 0 24 24" class:got={i < keys} aria-hidden="true"><path d="M8 15a4 4 0 1 1 3.5-6L20 9v3h-2v2h-2v-2h-4.5A4 4 0 0 1 8 15z" /></svg>
		{/each}
	</span>
</Hud>

{#if game.stage === 'intro'}
	<main class="wrap"><Countdown clock={game.clock} offset={client.offset} title="Hutan Misteri" /></main>
{:else if world}
	<div class="forest">
		<div class="top">
			<Timer clock={game.clock} offset={client.offset} total={game.length ?? 300} compact />
			{#if !escaped}
				<p class="goal">{keys >= need ? 'Semua kunci ada! Cari pintu hutan di bucu kanan bawah.' : `Cari peti soalan dan kumpul ${need} kunci.`}</p>
			{/if}
		</div>
		<div class="stage">
			<ForestMap
				map={world.map}
				chests={world.chests}
				gate={world.gate}
				positions={positions.all}
				moving={positions.moving}
				{people}
				me={me.id}
				escaped={world.escaped}
				gateOpen={keys >= need}
				follow
				tile={48}
				onchest={open}
			/>

			{#if !asking && !escaped}
				<div class="controls">
					<Joystick onmove={move} />
					{#if nearGate}
						<button type="button" class="btn btn--sun btn--big action" onclick={act}><Icon name="door" /> Keluar!</button>
					{:else if nearChest}
						<button type="button" class="btn btn--sun btn--big action" onclick={act}><Icon name="key" /> Buka peti</button>
					{/if}
				</div>
			{/if}
			{#if hint}<p class="hint" role="status">{hint}</p>{/if}

			{#if escaped}
				<div class="escaped">
					<h2>Kamu berjaya keluar!</h2>
					<p>Tempat ke-{order}. Tunggu kawan-kawan keluar atau masa tamat.</p>
				</div>
			{/if}
		</div>
	</div>

	{#if asking && seat.question}
		<div class="sheet-backdrop">
			<section class="sheet" aria-label="Soalan dari peti">
				<QuestionCard question={seat.question} />
				{#if seat.step === 'result' && seat.result}
					<Feedback
						correct={seat.result.correct}
						fraction={seat.result.fraction}
						extra={seat.result.reward?.key ? `Kamu dapat kunci! (${keys}/${need})` : ''}
					/>
				{/if}
				<Answer
					question={seat.question}
					disabled={seat.step !== 'question'}
					mine={seat.step === 'result' ? seat.result?.answer : undefined}
					reveal={seat.step === 'result' ? seat.result?.reveal : null}
					allRight={seat.result?.correct}
					onanswer={(a) => client.send({ t: 'answer', a })}
				/>
				{#if seat.step === 'result'}
					<button type="button" class="btn btn--sun btn--big" onclick={() => client.send({ t: 'next' })}>
						Teruskan jelajah <Icon name="next" />
					</button>
					{#if !seat.result?.correct}<p class="lock-note">Peti ini berkunci beberapa saat. Cuba peti lain dahulu.</p>{/if}
				{/if}
			</section>
		</div>
	{/if}
{/if}

<style>
	.keys {
		display: inline-flex;
		gap: 0.05rem;
	}
	.keys svg {
		width: 1.25rem;
		height: 1.25rem;
		fill: #e1d6c3;
		transition: transform var(--t-state) var(--spring);
	}
	.keys svg.got {
		fill: var(--sun);
		transform: scale(1.12) rotate(-12deg);
	}
	.forest {
		display: grid;
		grid-template-columns: minmax(0, 1fr);
		grid-template-rows: auto minmax(0, 1fr);
		gap: 0.5rem;
		height: calc(100dvh - 4.2rem);
		padding: 0.5rem var(--gutter-r) max(0.6rem, env(safe-area-inset-bottom, 0px)) var(--gutter);
	}
	.stage {
		position: relative;
		min-height: 0;
		min-width: 0;
	}
	.stage :global(.viewport) {
		height: 100%;
	}
	.controls {
		position: absolute;
		left: 0.8rem;
		right: 0.8rem;
		bottom: 0.8rem;
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		pointer-events: none;
	}
	.controls > :global(*) {
		pointer-events: auto;
	}
	.action {
		animation: pop-in 400ms var(--spring);
	}
	.top {
		display: grid;
		gap: 0.35rem;
	}
	.goal {
		font-weight: 800;
		font-size: 0.9rem;
		color: var(--ink-2);
		text-align: center;
	}
	.hint {
		position: absolute;
		left: 50%;
		top: 0.7rem;
		translate: -50% 0;
		width: max-content;
		max-width: calc(100% - 1.4rem);
		padding: 0.35rem 0.9rem;
		border-radius: var(--r-pill);
		background: #fff3cf;
		font-weight: 800;
		font-size: 0.9rem;
		text-align: center;
	}
	.escaped {
		position: absolute;
		inset: auto 1rem 1rem;
		display: grid;
		gap: 0.3rem;
		padding: 1rem 1.2rem;
		border-radius: var(--r-lg);
		background: var(--sun);
		text-align: center;
		animation: pop-in 520ms var(--spring);
	}
	.escaped h2 {
		font-size: 1.6rem;
	}
	.sheet-backdrop {
		position: fixed;
		inset: 0;
		z-index: 40;
		display: grid;
		align-items: end;
		justify-items: center;
		background: rgb(20 40 30 / 0.45);
	}
	.sheet {
		display: grid;
		gap: 0.9rem;
		width: min(44rem, 100%);
		max-height: 88dvh;
		overflow-y: auto;
		padding: 1.2rem var(--gutter-r) max(1.2rem, env(safe-area-inset-bottom, 0px)) var(--gutter);
		border-radius: var(--r-lg) var(--r-lg) 0 0;
		background: var(--paper);
		animation: rise-in var(--t-enter) var(--spring);
	}
	.lock-note {
		color: var(--ink-2);
		font-weight: 700;
		text-align: center;
	}
	@media (min-width: 760px) {
		.sheet-backdrop {
			align-items: center;
		}
		.sheet {
			border-radius: var(--r-lg);
		}
	}
</style>
