<!--
	A child's Pasar Malam (and, without a client, a stall on the host's board), as one pixel scene: a
	starry night over the kampung, a string of coloured lights between two bamboo poles, other stalls
	glowing down the lane, and the child's own stall in the middle with the child behind the counter
	and the decorations they have bought. Customers queue in front, facing the stall, more of them the
	finer it is; smoke rises off the grill, music notes float up from the speaker, and on a sale the
	coins jump. For the child, their stock, their ringgit and the shop of decorations.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';
	import { confetti } from '$lib/confetti';
	import { play } from '$lib/sound';
	import { ROW, chibiSheet } from '$lib/pixel/chibi';
	import Scene from '$lib/pixel/Scene.svelte';
	import { type G, block, cell, css, dot, hash, hex, put, sagLine, stillWanted } from '$lib/pixel/scene';
	import Icon from '$ui/Icon.svelte';
	import { stall } from './art';
	import { BULBS, MARKET, bamboo, lightPool, nightBack, note } from './night';
	import { puff } from './rail';

	interface Market {
		stock?: number;
		cash?: number;
		earned?: number;
		price?: number;
		mine: string[];
		good: string;
		upgrades: Record<string, { name: string; cost: number }>;
	}
	let { client = null, world, seller = null }: { client?: RoomClient | null; world: Market; s?: number; seller?: Person | null } = $props();

	const { w: W, h: H, poles: POLES, poleTop: POLE_TOP, stall: FOOT } = MARKET;
	const STALL_X = (W - 56) / 2;
	const STALL_Y = FOOT - 46;
	const still = stillWanted();

	const CROWD = [
		['kucing', 'jingga', 's2'],
		['arnab', 'jambu', 's1'],
		['penyu', 'teal', 's3'],
		['gajah', 'biru', 's2'],
		['enggang', 'kuning', 's4'],
		['harimau', 'merah', 's1'],
		['beruang', 'hijau', 's3'],
		['kancil', 'ungu', 's2'],
		['kucing', 'biru', 's4'],
		['arnab', 'kuning', 's3']
	] as const;
	// where each customer stands (the left of their cell, their feet): at the two ends of the counter
	// first, so the goods stay in sight, and in front of it once the crowd grows
	const SPOTS: [number, number][] = [
		[44, 99],
		[114, 99],
		[26, 102],
		[132, 102],
		[8, 99],
		[150, 99],
		[60, 104],
		[98, 104],
		[40, 105],
		[118, 105]
	];
	const crowd = $derived(CROWD.slice(0, Math.min(CROWD.length, 2 + world.mine.length * 2)));

	let sale = $state<{ key: number; money: number; at: number } | null>(null);
	let n = 0;
	$effect(() => {
		if (!client) return;
		return client.onFx((fx) => {
			if (fx.kind !== 'sold') return;
			const key = ++n;
			sale = { key, money: fx.money, at: performance.now() };
			play('coin');
			if (fx.money >= 15) confetti({ count: 40 });
			setTimeout(() => sale?.key === key && (sale = null), 1600);
		});
	});

	function upgrade(item: string) {
		if (!client) return;
		client.send({ t: 'upgrade', item });
		play('build');
	}
	const GOOD_NAME: Record<string, string> = { satay: 'satay', air: 'air tebu', kuih: 'kuih', jagung: 'jagung bakar', aiskrim: 'aiskrim' };

	// ------------------------------------------------------------------ the picture

	const WIRE = hex('#1a1626');

	/** The point `t` (0..1) along the string of lights, which sags in the middle. */
	function along(t: number): [number, number] {
		const [a, b] = [POLES[0] + 1, POLES[1] + 1];
		const sag = 12;
		const x = a + (b - a) * t;
		const y = POLE_TOP + 2 + sag * 4 * t * (1 - t);
		return [x, y];
	}

	function paint(g: G, t: number) {
		const now = still ? 0 : t;
		put(g, nightBack(), 0, 0);

		// a few stars twinkle
		for (let i = 0; i < 6; i++) if ((((now / 400) | 0) + i) % 5 === 0) dot(g, hash(i, 1) * W, hash(i, 2) * 36, hex('#ffffff'));

		// the warm light the stall throws on the ground, brighter with lamps
		const lit = world.mine.includes('lampu');
		put(g, lightPool(lit ? 58 : 44, lit ? 12 : 9), W / 2 - (lit ? 59 : 45), FOOT - (lit ? 6 : 4));

		// poles and the string of lights, the bulbs taking turns to glow
		put(g, bamboo(), POLES[0], POLE_TOP);
		put(g, bamboo(), POLES[1], POLE_TOP);
		sagLine(g, [POLES[0] + 1, POLE_TOP + 2], [POLES[1] + 1, POLE_TOP + 2], 6, WIRE);
		const blink = ((now / 500) | 0) % 2;
		for (let k = 1; k < 20; k++) {
			const [x, y] = along(k / 20);
			const c = BULBS[k % BULBS.length];
			const on = (k + blink) % 2 === 0 || still;
			if (on) {
				g.fillStyle = css((c & 0x00ffffff) | (60 << 24));
				g.fillRect(Math.round(x) - 2, Math.round(y), 5, 5);
			}
			block(g, x - 1, y + 1, 2, 3, on ? c : hex('#5a5068'));
			dot(g, x - 1, y + 1, on ? hex('#ffffff') : hex('#6a6078'));
		}

		// the child behind the counter, then the stall in front of them
		if (seller) {
			const sheet = chibiSheet(seller.avatar, seller.colour, seller.skin ?? 's2');
			const cheering = sale && now - sale.at < 1200;
			cell(g, sheet, cheering ? ((now / 280) | 0) % 2 : 0, cheering ? ROW.mood : ROW.front, STALL_X + 19, STALL_Y + 7);
		}
		put(g, stall(world.mine, world.good).pix, STALL_X, STALL_Y);

		// smoke off the grill
		if (world.good === 'satay' || world.good === 'jagung') {
			for (let k = 0; k < 4; k++) {
				const born = Math.floor(now / 500) * 500 - k * 500;
				const age = (now - born) / 2000;
				if (age < 0 || age > 1) continue;
				g.globalAlpha = 0.5 * (1 - age);
				put(g, puff(age < 0.4 ? 0 : 1), STALL_X + 16 + k * 7 + Math.sin(born) * 3, STALL_Y + 18 - age * 26);
				g.globalAlpha = 1;
			}
		}
		// music from the speaker
		if (world.mine.includes('muzik') && !still) {
			for (let k = 0; k < 3; k++) {
				const age = ((now + k * 700) % 2100) / 2100;
				g.globalAlpha = 1 - age;
				put(g, note(k % 2), STALL_X + 52 + Math.sin(age * 6 + k) * 3, STALL_Y + 30 - age * 30);
				g.globalAlpha = 1;
			}
		}

		// customers, facing the stall, in the order they arrived; they hop when something sells
		crowd.forEach(([animal, colour, skin], i) => {
			const [x, feet] = SPOTS[i];
			const hop = sale && now - sale.at < 900 && ((now / 150 + i) | 0) % 2 ? 2 : 0;
			cell(g, chibiSheet(animal, colour, skin), 0, ROW.back, x, feet - 30 - hop);
		});

		// coins jumping off the counter on a sale
		if (sale && !still) {
			const s = (now - sale.at) / 1000;
			for (let k = 0; k < 8; k++) {
				const x = STALL_X + 10 + hash(k, 3) * 36 + (hash(k, 4) - 0.5) * 30 * s;
				const y = STALL_Y + 26 - (40 + hash(k, 5) * 20) * s + 90 * s * s;
				if (s < 0.9) {
					block(g, x, y, 2, 2, hex('#f5c43a'));
					dot(g, x, y, hex('#fff6b0'));
				}
			}
		}
	}

	const label = $derived(`Pasar malam. Gerai ${GOOD_NAME[world.good] ?? 'kamu'} dengan ${world.mine.length} hiasan dan ${crowd.length} pelanggan.`);
</script>

<div class="fun pasar">
	{#if client}
		<ul class="stats" aria-label="Simpanan kamu">
			<li><strong>{world.stock}</strong> {GOOD_NAME[world.good] ?? 'barang'}</li>
			<li class="cash"><Icon name="coin" size={20} />RM <strong>{world.cash}</strong></li>
			<li>RM {world.price} sebiji</li>
		</ul>
	{/if}

	<div class="frame">
		<Scene w={W} h={H} {paint} fps={15} {label}>
			{#if sale}{#key sale.key}<p class="sale" role="status">+RM {sale.money}</p>{/key}{/if}
		</Scene>
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
	.frame {
		overflow: hidden;
		border: 3px solid #2a1f2d;
		border-radius: 6px;
		box-shadow: 0 4px 0 #2a1f2d;
		background: #17152a;
	}
	.sale {
		position: absolute;
		left: 50%;
		top: 30%;
		translate: -50% 0;
		padding: 0.3rem 0.8rem;
		border: 2px solid #2a1f2d;
		border-radius: 4px;
		background: #ffcf5a;
		box-shadow: 0 3px 0 #2a1f2d;
		font: 700 1.1rem/1.2 var(--font-display);
		animation: rise 1.6s steps(10) both;
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
	@keyframes rise {
		from {
			opacity: 0;
			transform: translateY(0.6rem);
		}
		20%,
		80% {
			opacity: 1;
			transform: translateY(0);
		}
		to {
			opacity: 0;
			transform: translateY(-0.6rem);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.sale {
			animation: none;
		}
	}
</style>
