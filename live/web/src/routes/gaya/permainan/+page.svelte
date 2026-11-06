<!--
	Art sheet for the newer 2D games: each one's scene with made-up state and a pretend room that
	answers its buttons the way the server would, for reviewing the look and the movement without a
	class. Not linked from the app.
-->
<script lang="ts">
	import FishingWorld from '$lib/games/fun/FishingWorld.svelte';
	import CastleWorld from '$lib/games/fun/CastleWorld.svelte';
	import TrainWorld from '$lib/games/fun/TrainWorld.svelte';
	import MarketWorld from '$lib/games/fun/MarketWorld.svelte';
	import SkyKites from '$lib/games/fun/SkyKites.svelte';
	import StarSky from '$lib/games/fun/StarSky.svelte';
	import FunHost from '$lib/games/fun/FunHost.svelte';
	import type { Fx, RoomClient } from '$lib/room.svelte';
	import type { Person } from '$lib/types';

	type Emit = (fx: Record<string, unknown>) => void;
	function pretend(handle: (m: Record<string, unknown>, emit: Emit) => void): RoomClient {
		const listeners = new Set<(fx: Fx) => void>();
		const emit: Emit = (fx) => listeners.forEach((fn) => fn({ t: 'fx', ...fx } as Fx));
		return {
			offset: 0,
			send: (m: Record<string, unknown>) => handle(m, emit),
			onFx: (fn: (fx: Fx) => void) => (listeners.add(fn), () => listeners.delete(fn))
		} as unknown as RoomClient;
	}
	const pickOne = <T,>(list: T[]) => list[Math.floor(Math.random() * list.length)];

	const people = new Map<string, Person>(
		[
			['a', 'Aisyah', 'kucing', 'jambu', 's1'],
			['b', 'Ben', 'harimau', 'biru', 's3'],
			['c', 'Chong', 'penyu', 'hijau', 's2'],
			['d', 'Devi', 'arnab', 'ungu', 's4'],
			['e', 'Ehsan', 'gajah', 'kuning', 's2'],
			['f', 'Farah', 'enggang', 'merah', 's1']
		].map(([id, name, avatar, colour, skin]) => [id, { id, name, avatar, colour, skin, team: null, online: true, bot: false, approved: true }])
	);
	const me = people.get('a')!;

	// ------------------------------------------------------------------ Pancing Ikan
	const FISH = {
		kasut: { name: 'Kasut buruk', value: 0 },
		bilis: { name: 'Ikan Bilis', value: 5 },
		puyu: { name: 'Ikan Puyu', value: 10 },
		keli: { name: 'Ikan Keli', value: 15 },
		patin: { name: 'Ikan Patin', value: 25 },
		kelah: { name: 'Ikan Kelah', value: 40 },
		arowana: { name: 'Arowana Emas', value: 80 }
	};
	let lake = $state({ fish: FISH, bait: 12, gold: 2, net: [] as string[], caught: 0, best: null as string | null });
	const lakeRoom = pretend((m, emit) => {
		if (m.t !== 'cast') return;
		const gold = !!m.gold;
		if (gold) lake.gold--;
		else lake.bait--;
		const fish = pickOne(gold ? ['patin', 'kelah', 'arowana', 'keli'] : ['kasut', 'bilis', 'bilis', 'puyu', 'puyu', 'keli', 'patin', 'kelah', 'arowana']);
		lake.net = [...lake.net, fish].slice(-8);
		lake.caught++;
		setTimeout(() => emit({ kind: 'catch', fish, value: FISH[fish as keyof typeof FISH].value, gold }), 120);
	});

	// ------------------------------------------------------------------ Kubu Pasir
	let castle = $state({ sand: 30, floors: 3, walls: 1, flags: 1, costs: { floor: 2, wall: 3, flag: 4 }, maxFloors: 12, maxWalls: 2, maxFlags: 3, waveAt: Date.now() + 45000, paused: false });
	const beachRoom = pretend((m, emit) => {
		if (m.t === 'build') {
			const part = m.part as 'floor' | 'wall' | 'flag';
			castle.sand -= castle.costs[part];
			if (part === 'floor') castle.floors++;
			if (part === 'wall') castle.walls++;
			if (part === 'flag') castle.flags++;
		}
		if (m.t === 'wave') {
			if (castle.walls) castle.walls--;
			else if (castle.floors) castle.floors--;
			castle.waveAt = Date.now() + 45000;
			emit({ kind: 'wave', n: 1 });
		}
	});

	// ------------------------------------------------------------------ Kereta Api
	let train = $state({ coal: 20, cars: 3, station: 0, stations: ['Kampung Durian', 'Pekan Rambutan', 'Bukit Merah', 'Tanjung Kelapa', 'Kuala Sungai', 'Bandar Bunga Raya'], carCost: 3, runCost: 2, kmPerCar: 10, maxCars: 8 });
	const railRoom = pretend((m, emit) => {
		if (m.t === 'car') {
			train.coal -= 3;
			train.cars++;
		}
		if (m.t === 'go') {
			train.coal -= 2;
			train.station = (train.station + 1) % train.stations.length;
			emit({ kind: 'arrive', station: train.station, km: train.cars * 10 });
		}
	});

	// ------------------------------------------------------------------ Pasar Malam
	const UPGRADES = { lampu: { name: 'Lampu meriah', cost: 10 }, kanopi: { name: 'Kanopi berwarna', cost: 20 }, papan: { name: 'Papan tanda bercahaya', cost: 35 }, muzik: { name: 'Muzik ceria', cost: 50 } };
	let market = $state({ stock: 8, cash: 60, earned: 0, mine: ['lampu'] as string[], good: 'satay', price: 2, upgrades: UPGRADES });
	const marketRoom = pretend((m, emit) => {
		if (m.t === 'sell' && market.stock) {
			const money = market.stock * market.price;
			market.cash += money;
			market.stock = 0;
			emit({ kind: 'sold', money });
			setTimeout(() => (market.stock = 6), 1500);
		}
		if (m.t === 'upgrade') {
			const item = m.item as keyof typeof UPGRADES;
			market.cash -= UPGRADES[item].cost;
			market.mine = [...market.mine, item];
			market.price = 1 + market.mine.length;
		}
	});

	// ------------------------------------------------------------------ Lumba Wau
	let race = $state({ length: 100, rapids: false, boats: [...people.keys()].map((id, i) => ({ id, m: [55, 30, 72, 12, 44, 90][i] })) });

	// ------------------------------------------------------------------ Kejar Bintang
	let sky = $state({
		teams: [
			{ key: 'harimau', name: 'Pasukan Harimau', stars: 23, lit: 2, players: 3 },
			{ key: 'penyu', name: 'Pasukan Penyu', stars: 17, lit: 1, players: 3 }
		],
		constellations: ['Bulan Sabit', 'Wau Bulan', 'Perahu', 'Gasing', 'Bunga Raya', 'Burung Enggang', 'Ketupat', 'Keris'],
		per: 10,
		myTeam: 'harimau',
		mine: 8
	});
	let skyEmit: Emit = () => {};
	const skyRoom = pretend((_m, emit) => (skyEmit = emit));
	skyRoom.send({});
	function catchStar(team: number) {
		const t = sky.teams[team];
		t.stars++;
		t.lit = Math.floor(t.stars / 10);
		skyEmit({ kind: 'star', team: t.key, by: 'x', caught: 1 });
	}

	// ------------------------------------------------------------------ the host's boards
	const castleTop = $derived([
		{ id: 'a', score: 80, ...castle },
		{ id: 'b', score: 40, floors: 4, walls: 0, flags: 0 },
		{ id: 'c', score: 20, floors: 2, walls: 2, flags: 1 }
	]);
	const trainTop = $derived([
		{ id: 'a', score: 120, cars: train.cars, station: train.station },
		{ id: 'b', score: 60, cars: 5, station: 2 },
		{ id: 'c', score: 30, cars: 1, station: 1 }
	]);
	const marketTop = $derived([
		{ id: 'a', score: 90, upgrades: market.mine, good: market.good },
		{ id: 'b', score: 50, upgrades: ['kanopi', 'lampu'], good: 'aiskrim' },
		{ id: 'c', score: 20, upgrades: [], good: 'jagung' }
	]);
	const fishTop = $derived([
		{ id: 'a', score: 120, best: lake.best ?? 'kelah', caught: lake.caught, net: lake.net },
		{ id: 'b', score: 60, best: 'patin', caught: 4, net: ['bilis', 'puyu', 'patin', 'kasut'] },
		{ id: 'c', score: 15, best: 'puyu', caught: 2, net: ['bilis', 'puyu'] }
	]);
	let host = $state(false);
</script>

<svelte:head><title>Gaya permainan · DIDIK Main Bersama</title></svelte:head>

<main class="wrap sheet">
	<label class="toggle"><input type="checkbox" bind:checked={host} /> Skrin hos</label>

	<section>
		<h2>Pancing Ikan</h2>
		{#if host}<FunHost game="pancing" world={{ fish: FISH, top: fishTop }} {people} unit="mata" />{:else}<FishingWorld client={lakeRoom} world={lake} {me} />{/if}
		<button type="button" class="btn" onclick={() => (lake.bait += 5)}>+5 umpan</button>
	</section>

	<section>
		<h2>Kubu Pasir</h2>
		{#if host}<FunHost game="kubu" world={{ top: castleTop }} {people} unit="mata" />{:else}<CastleWorld client={beachRoom} world={castle} />{/if}
		<button type="button" class="btn" onclick={() => beachRoom.send({ t: 'wave' })}>Ombak sekarang</button>
		<button type="button" class="btn" onclick={() => (castle.sand += 10)}>+10 pasir</button>
	</section>

	<section>
		<h2>Kereta Api Kampung</h2>
		{#if host}<FunHost game="keretapi" world={{ stations: train.stations, top: trainTop }} {people} unit="km" />{:else}<TrainWorld client={railRoom} world={train} />{/if}
		<button type="button" class="btn" onclick={() => (train.coal += 10)}>+10 arang</button>
	</section>

	<section>
		<h2>Pasar Malam</h2>
		{#if host}<FunHost game="pasar" world={{ upgrades: UPGRADES, top: marketTop }} {people} unit="RM" />{:else}<MarketWorld client={marketRoom} world={market} seller={me} />{/if}
		<button type="button" class="btn" onclick={() => (market.cash += 30)}>+RM 30</button>
	</section>

	<section>
		<h2>Lumba Wau</h2>
		<SkyKites {race} {people} me={host ? null : 'a'} compact={!host} />
		<button type="button" class="btn" onclick={() => race.boats.forEach((b) => (b.m = Math.min(100, b.m + Math.round(Math.random() * 15))))}>Naik</button>
		<button type="button" class="btn" onclick={() => (race.rapids = !race.rapids)}>Angin kencang</button>
	</section>

	<section>
		<h2>Kejar Bintang</h2>
		<StarSky client={skyRoom} world={sky} big={host} />
		<button type="button" class="btn" onclick={() => catchStar(0)}>Bintang Harimau</button>
		<button type="button" class="btn" onclick={() => catchStar(1)}>Bintang Penyu</button>
	</section>
</main>

<style>
	.sheet {
		display: grid;
		gap: 2rem;
		padding-block: 1.5rem 4rem;
	}
	section {
		display: grid;
		gap: 0.6rem;
	}
	section > .btn {
		justify-self: start;
	}
	.toggle {
		font-weight: 800;
	}
</style>
