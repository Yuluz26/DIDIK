<!--
	A child's Kubu Pasir (and, with `big`, a castle on the host's board): the beach with the sea at the
	top, the castle built floor by floor with flags on top and a sea wall in front, a countdown to the
	next wave, and, for the child, the sand in their bucket and what it builds.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Icon from '$ui/Icon.svelte';
	import { castleFloor, flag, seaWall } from './art';

	interface Castle {
		sand?: number;
		floors: number;
		walls: number;
		flags: number;
		costs?: Record<string, number>;
		maxFloors?: number;
		maxWalls?: number;
		maxFlags?: number;
		waveAt?: number;
		paused?: boolean;
	}
	let { client = null, world, s = 3, offset = 0 }: { client?: RoomClient | null; world: Castle; s?: number; offset?: number } = $props();

	let now = $state(Date.now());
	let splash = $state(0);
	$effect(() => {
		const timer = setInterval(() => (now = Date.now()), 500);
		return () => clearInterval(timer);
	});
	$effect(() => {
		if (!client) return;
		return client.onFx((fx) => {
			if (fx.kind !== 'wave') return;
			splash++;
			play('splash');
		});
	});
	const left = $derived(world.waveAt ? Math.max(0, Math.ceil((world.waveAt - (now + offset)) / 1000)) : null);

	function build(part: 'floor' | 'wall' | 'flag') {
		if (!client || !world.costs || (world.sand ?? 0) < world.costs[part]) return;
		client.send({ t: 'build', part });
		play('pop');
	}
	const can = (part: string) => !!world.costs && (world.sand ?? 0) >= world.costs[part];
</script>

<div class="fun kubu">
	{#if client}
		<ul class="stats" aria-label="Simpanan kamu">
			<li><Icon name="coin" size={20} /><strong>{world.sand}</strong> baldi pasir</li>
			<li><strong>{world.floors}</strong> tingkat</li>
			{#if left !== null && !world.paused}<li class="wave" class:soon={left <= 10}>Ombak dalam <strong>{left}</strong> s</li>{/if}
		</ul>
	{/if}

	<div class="scene beach" style:--s={s}>
		{#key splash}<span class="sea" class:hit={splash > 0} aria-hidden="true"></span>{/key}
		<div class="castle" aria-label="Istana {world.floors} tingkat, {world.flags} bendera, {world.walls} tembok">
			{#if world.floors > 0}
				<div class="flags">{#each Array(world.flags) as _, i (i)}<Sprite sheet={flag(i)} {s} />{/each}</div>
			{/if}
			{#each Array(world.floors) as _, i (i)}
				<span class="floor"><Sprite sheet={castleFloor(i === 0)} {s} /></span>
			{/each}
			{#if world.floors === 0}<p class="empty">Belum ada istana</p>{/if}
		</div>
		{#if world.walls > 0}
			<div class="walls">{#each Array(world.walls) as _, i (i)}<Sprite sheet={seaWall()} {s} />{/each}</div>
		{/if}
	</div>

	{#if client && world.costs}
		<div class="acts">
			<button type="button" class="btn btn--sun" disabled={!can('floor') || world.floors >= (world.maxFloors ?? 12)} onclick={() => build('floor')}>Tambah tingkat · {world.costs.floor}</button>
			<button type="button" class="btn btn--sea" disabled={!can('wall') || world.walls >= (world.maxWalls ?? 2)} onclick={() => build('wall')}>Bina tembok · {world.costs.wall}</button>
			<button type="button" class="btn" disabled={!can('flag') || world.floors === 0 || world.flags >= (world.maxFlags ?? 3)} onclick={() => build('flag')}>Pacak bendera · {world.costs.flag}</button>
		</div>
		<p class="hint" aria-live="polite">
			{world.walls ? 'Tembok kamu akan menahan ombak seterusnya.' : 'Tiada tembok: ombak akan meruntuhkan satu tingkat!'}
		</p>
	{/if}
</div>

<style>
	.fun {
		display: grid;
		gap: 0.7rem;
	}
	.stats {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.stats li {
		display: inline-flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0.35rem 0.8rem;
		border-radius: var(--r-pill);
		background: var(--card);
		box-shadow: var(--card-shadow);
		font-weight: 800;
	}
	.stats .wave {
		background: #c9eef5;
	}
	.stats .soon {
		background: #ffe3d6;
		animation: pulse 1s ease-in-out infinite;
	}
	.scene {
		position: relative;
		overflow: hidden;
		border-radius: var(--r-lg);
		box-shadow: var(--card-shadow);
		image-rendering: pixelated;
	}
	.beach {
		display: grid;
		align-content: end;
		justify-items: center;
		min-height: calc(var(--s) * 120px);
		padding-bottom: 1rem;
		background: linear-gradient(180deg, #2a88a6 0 18%, #7fd2d2 18% 22%, #f5dfaa 22% 100%);
	}
	.sea {
		position: absolute;
		inset: 0 0 auto;
		height: 22%;
		background: repeating-linear-gradient(90deg, #47b0bd 0 24px, #7fd2d2 24px 30px);
	}
	.sea.hit {
		animation: wave 1.4s ease-in-out;
	}
	.castle {
		position: relative;
		z-index: 1;
		display: grid;
		justify-items: center;
		line-height: 0;
	}
	.flags {
		display: flex;
		gap: calc(var(--s) * 4px);
		margin-bottom: -2px;
	}
	.floor {
		display: block;
		margin-top: -2px;
	}
	.walls {
		position: relative;
		z-index: 2;
		display: flex;
		margin-top: -4px;
	}
	.empty {
		padding: 1rem;
		color: #8a6a3a;
		font-weight: 800;
		line-height: 1.2;
	}
	.acts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.acts .btn {
		flex: 1 1 10rem;
	}
	.hint {
		color: var(--ink-2);
		font-weight: 800;
		text-align: center;
	}
	@keyframes wave {
		50% {
			height: 70%;
			opacity: 0.85;
		}
	}
	@keyframes pulse {
		50% {
			transform: scale(1.05);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.sea.hit,
		.stats .soon {
			animation: none;
		}
	}
</style>
