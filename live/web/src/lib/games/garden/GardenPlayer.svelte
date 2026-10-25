<!--
	A child's Kebun Ajaib: coins and water at the top, the garden in the middle (tap a bed to plant,
	water or harvest it, and the gardener walks over), and below it the seeds for an empty bed or the
	shop. Right answers fill the water jar.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { confetti } from '$lib/confetti';
	import { play } from '$lib/sound';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Crop from '$lib/worlds/Crop.svelte';
	import { shopSheet } from '$lib/worlds/garden';
	import Icon from '$ui/Icon.svelte';
	import GardenWorld, { bedAt, type CropInfo, type Plot } from './GardenWorld.svelte';

	interface Garden {
		coins: number;
		water: number;
		fert: number;
		earned: number;
		plots: (Plot | null)[];
		maxPlots: number;
		crops: Record<string, CropInfo>;
		shop: Record<string, { name: string; cost: number; note: string }>;
	}

	let { client, world, me }: { client: RoomClient; world: Garden; me: Person } = $props();

	let picking = $state<number | null>(null);
	let spot = $state<[number, number] | null>(null);
	let walking = $state(false);
	let pops = $state<{ key: number; bed: number; text: string; kind: 'drop' | 'coin' }[]>([]);
	let note = $state('');
	let counter = 0;
	let walkTimer: ReturnType<typeof setTimeout> | undefined;

	const needOf = (plot: Plot) => world.crops[plot.crop]?.water ?? 1;
	const isReady = (plot: Plot | null): boolean => !!plot && plot.stage >= needOf(plot);

	function walkTo(i: number) {
		const [x, y] = bedAt(i);
		spot = [x + 1.5, y + 0.2];
		walking = true;
		clearTimeout(walkTimer);
		walkTimer = setTimeout(() => (walking = false), 560);
	}

	function pop(bed: number, text: string, kind: 'drop' | 'coin') {
		const key = ++counter;
		pops = [...pops, { key, bed, text, kind }];
		setTimeout(() => (pops = pops.filter((p) => p.key !== key)), 1300);
	}

	function tapBed(i: number) {
		note = '';
		walkTo(i);
		if (i >= world.plots.length) {
			buy('tanah');
			return;
		}
		const plot = world.plots[i];
		if (!plot) {
			picking = i;
			play('tap');
			return;
		}
		picking = null;
		if (isReady(plot)) {
			client.send({ t: 'harvest', plot: i });
			return;
		}
		if (world.water < 1) {
			note = 'Air sudah habis. Jawab soalan untuk dapat titisan air.';
			play('almost');
			return;
		}
		client.send({ t: 'water', plot: i });
		play('water');
		pop(i, world.fert > 0 ? '+2' : '+1', 'drop');
	}

	function plant(crop: string) {
		if (picking === null) return;
		client.send({ t: 'plant', plot: picking, crop });
		play('pop');
		picking = null;
	}

	function buy(item: string) {
		const thing = world.shop[item];
		if (!thing || (item === 'tanah' && world.plots.length >= world.maxPlots)) return;
		if (world.coins < thing.cost) {
			note = `Perlu ${thing.cost} syiling untuk ${thing.name.toLowerCase()}. Tuai tanaman dahulu.`;
			play('almost');
			return;
		}
		client.send({ t: 'buy', item });
		play('coin');
	}

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind !== 'harvest') return;
			play('harvest');
			pop(fx.plot, `+${fx.value}`, 'coin');
			if (fx.crop === 'durian' || fx.crop === 'tembikai') confetti({ count: 50 });
		})
	);

	const labels = $derived(
		Array.from({ length: world.maxPlots }, (_, i) => {
			if (i >= world.plots.length) return `Batas ${i + 1}: tanah belum dibeli. Ketik untuk beli dengan ${world.shop.tanah?.cost} syiling.`;
			const plot = world.plots[i];
			if (!plot) return `Batas ${i + 1}: kosong. Ketik untuk menanam.`;
			const crop = world.crops[plot.crop];
			if (isReady(plot)) return `Batas ${i + 1}: ${crop.name} sudah masak. Ketik untuk menuai.`;
			return `Batas ${i + 1}: ${crop.name}, perlu ${needOf(plot) - plot.stage} siraman lagi. Ketik untuk siram.`;
		})
	);

	const hint = $derived.by(() => {
		if (note) return note;
		if (world.plots.some(isReady)) return 'Ada tanaman yang sudah masak. Ketik batas yang berkilau untuk menuai.';
		if (world.plots.some((p) => !p)) return 'Ketik batas kosong untuk menanam benih.';
		if (world.water < 1) return 'Jawab soalan untuk dapat air, kemudian siram tanaman.';
		return 'Ketik tanaman untuk menyiramnya. Setiap siraman menghampirkan tuaian.';
	});
</script>

{#snippet overlay(tile: number)}
	{#each pops as p (p.key)}
		{@const [x, y] = bedAt(p.bed)}
		<span class="pop {p.kind}" style:left="{x * tile}px" style:top="{(y - 1.9) * tile}px">
			<Icon name={p.kind} size={15} />{p.text}
		</span>
	{/each}
{/snippet}

<div class="kebun">
	<ul class="purse" aria-label="Simpanan kamu">
		<li class="coins"><Icon name="coin" size={20} /><strong>{world.coins}</strong> syiling</li>
		<li class="water"><Icon name="drop" size={20} /><strong>{world.water}</strong> air</li>
		{#if world.fert}<li class="fert"><strong>{world.fert}</strong> siraman berbaja</li>{/if}
	</ul>

	<GardenWorld
		plots={world.plots}
		crops={world.crops}
		maxPlots={world.maxPlots}
		water={world.water}
		owner={me}
		{spot}
		{walking}
		{labels}
		onbed={tapBed}
		{overlay}
	/>

	<p class="hint" class:warn={!!note} aria-live="polite">{hint}</p>

	{#if picking !== null}
		<section class="seeds" aria-label="Pilih benih">
			<header>
				<h3>Tanam apa di batas {picking + 1}?</h3>
				<button type="button" class="btn btn--plain" onclick={() => (picking = null)}>Batal</button>
			</header>
			<div class="list">
				{#each Object.entries(world.crops) as [key, crop] (key)}
					<button type="button" class="seed" disabled={world.coins < crop.cost} onclick={() => plant(key)}>
						<span class="art"><Crop crop={key} ready s={2} /></span>
						<strong>{crop.name}</strong>
						<span class="price">{crop.cost ? `${crop.cost} syiling` : 'Percuma'}</span>
						<small>{crop.water} siraman, tuai {crop.value}</small>
					</button>
				{/each}
			</div>
		</section>
	{:else}
		<section class="shop" aria-label="Kedai kebun">
			{#each Object.entries(world.shop) as [key, item] (key)}
				{@const full = key === 'tanah' && world.plots.length >= world.maxPlots}
				<button type="button" class="buy" disabled={world.coins < item.cost || full} onclick={() => buy(key)}>
					<span class="art"><Sprite sheet={shopSheet(key)} s={2} /></span>
					<span class="text"><strong>{item.name}</strong><small>{full ? 'Kebun kamu sudah penuh.' : item.note}</small></span>
					<span class="price"><Icon name="coin" size={16} />{item.cost}</span>
				</button>
			{/each}
		</section>
	{/if}
</div>

<style>
	.kebun {
		display: grid;
		gap: 0.7rem;
	}
	.purse {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.purse li {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		padding: 0.3rem 0.8rem;
		border-radius: var(--r-pill);
		background: var(--card);
		font-weight: 700;
		box-shadow: 0 2px 0 var(--line);
	}
	.purse strong {
		font: 600 1.15rem var(--font-display);
	}
	.coins :global(svg) {
		color: var(--sun-deep);
	}
	.water :global(svg) {
		color: var(--sky);
	}
	.purse .fert {
		background: var(--good-soft);
	}
	.hint {
		padding: 0.55rem 0.9rem;
		border-radius: var(--r-md);
		background: var(--brand-soft);
		font-weight: 700;
	}
	.hint.warn {
		background: var(--almost-soft);
	}
	.pop {
		position: absolute;
		display: inline-flex;
		align-items: center;
		gap: 0.15rem;
		translate: -50% 0;
		padding: 0 0.45rem 0 0.3rem;
		border-radius: var(--r-pill);
		font: 600 0.85rem/1.6 var(--font-display);
		white-space: nowrap;
		animation: gain 1.2s var(--ease-out) forwards;
	}
	.pop.drop {
		background: #dff3fd;
		color: var(--sky-deep);
	}
	.pop.coin {
		background: var(--sun);
	}
	.seeds,
	.shop {
		display: grid;
		gap: 0.6rem;
		padding: 0.8rem;
		border-radius: var(--r-md);
		background: var(--card);
		box-shadow: var(--card-shadow);
	}
	.seeds {
		background: #fff3d6;
		animation: pop-in 350ms var(--spring);
	}
	.seeds header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.6rem;
	}
	.seeds h3 {
		font-size: 1.15rem;
	}
	.list {
		display: grid;
		grid-template-columns: repeat(3, minmax(0, 1fr));
		gap: 0.5rem;
	}
	.seed,
	.buy {
		border: 0;
		border-radius: var(--r-sm);
		background: #fff;
		color: inherit;
		font: inherit;
		box-shadow: 0 3px 0 var(--line);
		cursor: pointer;
		transition: transform var(--t-press) var(--ease-out);
	}
	.seed:not(:disabled):hover,
	.buy:not(:disabled):hover {
		transform: translateY(-2px);
	}
	.seed:not(:disabled):active,
	.buy:not(:disabled):active {
		transform: translateY(1px);
	}
	.seed:disabled,
	.buy:disabled {
		cursor: not-allowed;
		opacity: 0.55;
	}
	.seed {
		display: grid;
		justify-items: center;
		gap: 0.1rem;
		padding: 0.5rem 0.3rem 0.6rem;
		text-align: center;
	}
	.seed .art {
		display: grid;
		place-items: end center;
		height: 4.4rem;
		line-height: 0;
	}
	.seed strong {
		font-size: 0.95rem;
	}
	.seed small {
		color: var(--ink-2);
		font-size: 0.78rem;
		line-height: 1.25;
	}
	.price {
		display: inline-flex;
		align-items: center;
		gap: 0.2rem;
		font: 600 0.95rem var(--font-display);
		color: var(--sun-deep);
	}
	.shop {
		grid-template-columns: minmax(0, 1fr);
	}
	.buy {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr) auto;
		align-items: center;
		gap: 0.7rem;
		padding: 0.6rem 0.8rem;
		text-align: left;
	}
	.buy .art {
		display: grid;
		place-items: center;
		line-height: 0;
	}
	.text {
		display: grid;
	}
	.text small {
		color: var(--ink-2);
		font-size: 0.85rem;
		line-height: 1.3;
	}
	@media (min-width: 560px) {
		.list {
			grid-template-columns: repeat(5, minmax(0, 1fr));
		}
		.shop {
			grid-template-columns: repeat(2, minmax(0, 1fr));
		}
	}
</style>
