<!--
	A child's Kereta Api Kampung (and, with no client, a train on the host's board): hills and the track,
	the engine with its carriages full of passengers, the station it stands at and the next one, and,
	for the child, the coal they have and what it buys. A run slides the scenery past.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Icon from '$ui/Icon.svelte';
	import { carriage, engine } from './art';

	interface Train {
		coal?: number;
		cars: number;
		station: number;
		stations: string[];
		carCost?: number;
		runCost?: number;
		kmPerCar?: number;
		maxCars?: number;
	}
	let { client = null, world, s = 3 }: { client?: RoomClient | null; world: Train; s?: number } = $props();

	let moving = $state(0);
	let gained = $state<{ key: number; km: number } | null>(null);
	$effect(() => {
		if (!client) return;
		return client.onFx((fx) => {
			if (fx.kind !== 'arrive') return;
			moving++;
			gained = { key: moving, km: fx.km };
			play('go');
			const key = moving;
			setTimeout(() => gained?.key === key && (gained = null), 1800);
		});
	});
	const here = $derived(world.stations[world.station] ?? '');
	const next = $derived(world.stations[(world.station + 1) % world.stations.length] ?? '');
</script>

<div class="fun keretapi">
	{#if client}
		<ul class="stats" aria-label="Simpanan kamu">
			<li><Icon name="coin" size={20} /><strong>{world.coal}</strong> arang</li>
			<li><strong>{world.cars}</strong> gerabak</li>
		</ul>
	{/if}

	<div class="scene land" style:--s={s}>
		{#key moving}<span class="hills" class:run={moving > 0} aria-hidden="true"></span>{/key}
		<p class="sign"><span>Stesen</span> {here}</p>
		<div class="train" aria-label="Kereta api dengan {world.cars} gerabak di stesen {here}">
			{#each Array(world.cars) as _, i (i)}<Sprite sheet={carriage(world.cars - 1 - i, 3)} {s} />{/each}
			<Sprite sheet={engine()} {s} />
		</div>
		<span class="rails" aria-hidden="true"></span>
		{#if gained}{#key gained.key}<p class="km" role="status">+{gained.km} km</p>{/key}{/if}
	</div>

	{#if client && world.carCost !== undefined}
		<div class="acts">
			<button type="button" class="btn btn--sun btn--big" disabled={(world.coal ?? 0) < (world.runCost ?? 2)} onclick={() => client?.send({ t: 'go' })}>
				Jalan ke {next} · {world.runCost} arang
			</button>
			<button type="button" class="btn btn--sea" disabled={(world.coal ?? 0) < world.carCost || world.cars >= (world.maxCars ?? 8)} onclick={() => (client?.send({ t: 'car' }), play('pop'))}>
				Tambah gerabak · {world.carCost} arang
			</button>
		</div>
		<p class="hint" aria-live="polite">Setiap gerabak menambah {world.kmPerCar} km bagi setiap perjalanan.</p>
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
	.scene {
		position: relative;
		overflow: hidden;
		border-radius: var(--r-lg);
		box-shadow: var(--card-shadow);
		image-rendering: pixelated;
	}
	.land {
		min-height: calc(var(--s) * 70px);
		background: linear-gradient(180deg, #9ed8f2 0 45%, #72bc4c 45% 100%);
	}
	.hills {
		position: absolute;
		inset: 20% -50% 40% 0;
		background:
			radial-gradient(ellipse 12% 60% at 10% 100%, #3d8858 98%, transparent) 0 0 / 50% 100% repeat-x,
			radial-gradient(ellipse 16% 80% at 70% 100%, #589a46 98%, transparent) 0 0 / 50% 100% repeat-x;
	}
	.hills.run {
		animation: slide 1.4s ease-in-out;
	}
	.sign {
		position: absolute;
		left: 0.8rem;
		top: 0.7rem;
		display: grid;
		padding: 0.3rem 0.8rem;
		border: 3px solid #6e4a30;
		border-radius: var(--r-sm);
		background: #fff6e6;
		font: 700 1rem/1.1 var(--font-display);
	}
	.sign span {
		color: var(--ink-3);
		font-size: 0.7rem;
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}
	.train {
		position: absolute;
		right: 0.8rem;
		bottom: calc(var(--s) * 6px);
		z-index: 1;
		display: flex;
		align-items: flex-end;
		gap: calc(var(--s) * 1px);
		line-height: 0;
		max-width: calc(100% - 1.6rem);
		overflow: hidden;
	}
	.rails {
		position: absolute;
		inset: auto 0 calc(var(--s) * 4px);
		height: calc(var(--s) * 3px);
		background: repeating-linear-gradient(90deg, #6e4a30 0 6px, #555766 6px 18px);
	}
	.km {
		position: absolute;
		left: 50%;
		top: 30%;
		translate: -50% 0;
		padding: 0.4rem 0.9rem;
		border-radius: var(--r-pill);
		background: #ffcf5a;
		font: 700 1.2rem var(--font-display);
		animation: rise 1.8s ease-out both;
	}
	.acts {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	.acts .btn {
		flex: 1 1 12rem;
	}
	.hint {
		color: var(--ink-2);
		font-weight: 800;
		text-align: center;
	}
	@keyframes slide {
		to {
			transform: translateX(-50%);
		}
	}
	@keyframes rise {
		from {
			opacity: 0;
			transform: translateY(0.8rem);
		}
		80% {
			opacity: 1;
		}
		to {
			opacity: 0;
			transform: translateY(-0.8rem);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.hills.run,
		.km {
			animation: none;
		}
	}
</style>
