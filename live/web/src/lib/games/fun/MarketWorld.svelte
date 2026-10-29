<!--
	A child's Pasar Malam (and, with no client, a stall on the host's board): the night market under a
	string of lights, the child's stall with the decorations they have bought, a crowd that grows with
	them, and, for the child, their stock, their ringgit and the shop of decorations.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import { confetti } from '$lib/confetti';
	import { play } from '$lib/sound';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import Chibi from '$ui/Chibi.svelte';
	import Icon from '$ui/Icon.svelte';
	import { stall } from './art';

	interface Market {
		stock?: number;
		cash?: number;
		earned?: number;
		price?: number;
		mine: string[];
		good: string;
		upgrades: Record<string, { name: string; cost: number }>;
	}
	let { client = null, world, s = 3 }: { client?: RoomClient | null; world: Market; s?: number } = $props();

	const CROWD = [
		['kucing', 'jingga'],
		['arnab', 'jambu'],
		['penyu', 'teal'],
		['gajah', 'biru'],
		['enggang', 'kuning'],
		['harimau', 'merah'],
		['beruang', 'hijau'],
		['kancil', 'ungu']
	] as const;
	const crowd = $derived(CROWD.slice(0, 2 + world.mine.length * 2));
	let sale = $state<{ key: number; money: number } | null>(null);
	let n = 0;

	$effect(() => {
		if (!client) return;
		return client.onFx((fx) => {
			if (fx.kind !== 'sold') return;
			const key = ++n;
			sale = { key, money: fx.money };
			play('coin');
			if (fx.money >= 15) confetti({ count: 40 });
			setTimeout(() => sale?.key === key && (sale = null), 1600);
		});
	});

	function upgrade(item: string) {
		if (!client) return;
		client.send({ t: 'upgrade', item });
		play('pop');
	}
	const GOOD_NAME: Record<string, string> = { satay: 'satay', air: 'air tebu', kuih: 'kuih', jagung: 'jagung bakar', aiskrim: 'aiskrim' };
</script>

<div class="fun pasar">
	{#if client}
		<ul class="stats" aria-label="Simpanan kamu">
			<li><strong>{world.stock}</strong> {GOOD_NAME[world.good] ?? 'barang'}</li>
			<li class="cash"><Icon name="coin" size={20} />RM <strong>{world.cash}</strong></li>
			<li>RM {world.price} sebiji</li>
		</ul>
	{/if}

	<div class="scene night" style:--s={s}>
		<span class="lights" aria-hidden="true"></span>
		<div class="stall"><Sprite sheet={stall(world.mine, world.good)} {s} /></div>
		<div class="crowd" aria-label="{crowd.length} pelanggan">
			{#each crowd as [animal, colour], i (i)}
				<span class="who" style:--i={i}><Chibi {animal} {colour} s={Math.max(2, s - 1)} mood={sale ? 'cheer' : 'happy'} /></span>
			{/each}
		</div>
		{#if world.mine.includes('muzik')}<span class="notes" aria-hidden="true">♪ ♫</span>{/if}
		{#if sale}{#key sale.key}<p class="sale" role="status">+RM {sale.money}</p>{/key}{/if}
	</div>

	{#if client}
		<div class="acts">
			<button type="button" class="btn btn--sun btn--big" disabled={!world.stock} onclick={() => client?.send({ t: 'sell' })}>
				Jual {world.stock} · RM {(world.stock ?? 0) * (world.price ?? 1)}
			</button>
		</div>
		<ul class="shop" aria-label="Hiasan gerai">
			{#each Object.entries(world.upgrades) as [key, u] (key)}
				{@const owned = world.mine.includes(key)}
				<li>
					<button type="button" class="btn" disabled={owned || (world.cash ?? 0) < u.cost} onclick={() => upgrade(key)}>
						{u.name} {owned ? '✓' : `· RM ${u.cost}`}
					</button>
				</li>
			{/each}
		</ul>
		<p class="hint" aria-live="polite">Setiap hiasan menaikkan harga RM 1 dan menarik lebih ramai pelanggan.</p>
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
	.stats .cash {
		background: #fff3cf;
	}
	.scene {
		position: relative;
		overflow: hidden;
		border-radius: var(--r-lg);
		box-shadow: var(--card-shadow);
		image-rendering: pixelated;
	}
	.night {
		display: grid;
		justify-items: center;
		align-content: end;
		min-height: calc(var(--s) * 78px);
		padding-bottom: calc(var(--s) * 6px);
		background: linear-gradient(180deg, #1b1a33 0 60%, #2f2c48 60% 100%);
	}
	.lights {
		position: absolute;
		inset: 0.6rem 0 auto;
		height: 1.2rem;
		background: radial-gradient(circle, #ffe070 0 30%, transparent 34%) 0 0 / 1.6rem 1.2rem repeat-x;
		filter: drop-shadow(0 0 6px #ffcf5a);
		animation: twinkle 1.6s steps(2) infinite;
	}
	.stall {
		position: relative;
		z-index: 1;
		line-height: 0;
	}
	.crowd {
		position: absolute;
		inset: auto 0 calc(var(--s) * 2px);
		display: flex;
		justify-content: space-between;
		padding: 0 4%;
		z-index: 2;
		pointer-events: none;
	}
	.who {
		animation: bob 1.4s ease-in-out calc(var(--i) * -0.3s) infinite;
	}
	.notes {
		position: absolute;
		right: 8%;
		top: 30%;
		color: #ffcf5a;
		font-size: 1.4rem;
		animation: bob 1.2s ease-in-out infinite;
	}
	.sale {
		position: absolute;
		left: 50%;
		top: 22%;
		translate: -50% 0;
		padding: 0.4rem 0.9rem;
		border-radius: var(--r-pill);
		background: #ffcf5a;
		font: 700 1.2rem var(--font-display);
		z-index: 3;
	}
	.acts .btn {
		width: 100%;
	}
	.shop {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.shop .btn {
		width: 100%;
	}
	.hint {
		color: var(--ink-2);
		font-weight: 800;
		text-align: center;
	}
	@keyframes twinkle {
		50% {
			opacity: 0.7;
		}
	}
	@keyframes bob {
		50% {
			transform: translateY(-3px);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.lights,
		.who,
		.notes {
			animation: none;
		}
	}
</style>
