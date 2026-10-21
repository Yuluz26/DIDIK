<!--
	Hutan Misteri's forest, drawn from the same rows the server walks on: flat ground (grass, paths,
	river, bridges) and, standing on it, trees, rocks, flowers, chests and the gate, with every child's
	character walking among them in depth order.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';

	interface Chest {
		id: number;
		x: number;
		y: number;
		state?: 'closed' | 'open' | 'locked';
		opened?: number;
	}

	let {
		map,
		chests,
		gate,
		positions,
		moving = {},
		people,
		me = null,
		escaped = [],
		gateOpen = false,
		follow = false,
		tile = 44,
		onchest
	}: {
		map: string[];
		chests: Chest[];
		gate: { x: number; y: number };
		positions: Record<string, { x: number; y: number; f: number }>;
		moving?: Record<string, boolean>;
		people: Map<string, Person>;
		me?: string | null;
		escaped?: string[];
		gateOpen?: boolean;
		follow?: boolean;
		tile?: number;
		onchest?: (id: number) => void;
	} = $props();

	const W = $derived(map[0]?.length ?? 32);
	const H = $derived(map.length);
	const hash = (x: number, y: number) => ((x * 73856093) ^ (y * 19349663)) >>> 0;
	const at = (x: number, y: number) => map[y]?.[x] ?? '#';

	function cells(kinds: string): [number, number][] {
		const out: [number, number][] = [];
		map.forEach((row, y) => [...row].forEach((ch, x) => kinds.includes(ch) && out.push([x, y])));
		return out;
	}

	const paths = $derived(cells(':SG'));
	const water = $derived(cells('~'));
	const bridges = $derived(cells('='));
	const tufts = $derived(cells('.f m').filter(([x, y]) => hash(x, y) % 4 === 0));

	// Everything that stands up from the ground and so must be depth-sorted with the children.
	const scenery = $derived.by(() => {
		const out: WorldProp[] = [];
		map.forEach((row, y) =>
			[...row].forEach((ch, x) => {
				const h = hash(x, y);
				if (ch === '#') out.push({ id: `t${x}-${y}`, kind: h % 5 === 0 ? 'pine' : 'tree', x: x + 0.5 + ((h % 7) - 3) * 0.03, y: y + 0.95, variant: h % 3 });
				else if (ch === 'R') out.push({ id: `r${x}-${y}`, kind: 'rock', x: x + 0.5, y: y + 0.85 });
				else if (ch === 'f') out.push({ id: `f${x}-${y}`, kind: 'flowers', x: x + 0.5, y: y + 0.7, variant: h % 2 });
				else if (ch === 'm') out.push({ id: `m${x}-${y}`, kind: 'mushroom', x: x + 0.5, y: y + 0.75 });
				else if (ch === '.' && h % 23 === 0 && at(x, y - 1) !== '~') out.push({ id: `b${x}-${y}`, kind: 'bush', x: x + 0.5, y: y + 0.8, variant: h % 3 });
				else if (ch === '~' && h % 11 === 0) out.push({ id: `l${x}-${y}`, kind: 'lily', x: x + 0.5, y: y + 0.6 });
			})
		);
		return out;
	});

	// Not named `props`: a variable called props would make Svelte read `$props` as a store.
	const items = $derived<WorldProp[]>([
		...scenery,
		...chests.map((chest) => ({
			id: `chest${chest.id}`,
			kind: 'chest',
			x: chest.x,
			y: chest.y + 0.35,
			state: chest.state ?? 'closed',
			badge: chest.opened || undefined,
			label: chest.state === 'open' ? 'Peti sudah dibuka' : 'Buka peti soalan',
			action: onchest && chest.state !== 'open' ? () => onchest?.(chest.id) : undefined
		})),
		{ id: 'gate', kind: 'gate', x: gate.x, y: gate.y + 0.95, state: gateOpen ? 'open' : '' }
	]);

	const actors = $derived<WorldActor[]>(
		Object.entries(positions)
			.filter(([id]) => !escaped.includes(id) && people.has(id))
			.map(([id, pos]) => {
				const person = people.get(id)!;
				return {
					id,
					x: pos.x,
					y: pos.y + 0.3,
					facing: pos.f,
					walking: !!moving[id],
					animal: person.avatar,
					colour: person.colour,
					skin: person.skin,
					name: person.name
				};
			})
	);
</script>

<World width={W} height={H} {tile} props={items} {actors} {me} {follow}>
	{#snippet ground()}
		<rect width={W} height={H} fill="#8fd05e" />
		{#each tufts as [x, y] (`g${x}-${y}`)}
			<path d="M{x + 0.3} {y + 0.6} l0.06 -0.16 l0.06 0.16 M{x + 0.62} {y + 0.36} l0.05 -0.13 l0.05 0.13" stroke="#6cb33f" stroke-width="0.05" fill="none" stroke-linecap="round" />
		{/each}
		{#each paths as [x, y] (`p${x}-${y}`)}<rect x={x - 0.04} y={y - 0.04} width="1.08" height="1.08" rx="0.22" fill="#e9cf98" />{/each}
		{#each paths as [x, y] (`ps${x}-${y}`)}
			{#if hash(x, y) % 3 === 0}<circle cx={x + 0.3} cy={y + 0.6} r="0.05" fill="#cfae6c" /><circle cx={x + 0.7} cy={y + 0.3} r="0.04" fill="#cfae6c" />{/if}
		{/each}
		{#each water as [x, y] (`w${x}-${y}`)}
			<rect x={x - 0.01} y={y - 0.01} width="1.02" height="1.02" fill="#3ba7d9" />
			{#if at(x, y - 1) !== '~' && at(x, y - 1) !== '='}<rect x={x} y={y} width="1" height="0.14" fill="#bfe6f6" />{/if}
			{#if (x * 3 + y) % 4 === 0}<path d="M{x + 0.2} {y + 0.55} q0.15 -0.12 0.3 0 t0.3 0" stroke="#9fd8f0" stroke-width="0.06" fill="none" stroke-linecap="round" />{/if}
		{/each}
		{#each bridges as [x, y] (`b${x}-${y}`)}
			{@const across = at(x, y - 1) === '~' || at(x, y + 1) === '~'}
			<rect x={x - 0.02} y={y - 0.02} width="1.04" height="1.04" fill="#c98a54" />
			{#if across}
				<!-- Walked left to right: planks run up and down, rails along the top and bottom. -->
				<path d="M{x + 0.25} {y} v1 M{x + 0.5} {y} v1 M{x + 0.75} {y} v1" stroke="#a46a37" stroke-width="0.05" />
				<rect x={x - 0.02} y={y - 0.06} width="1.04" height="0.12" fill="#8e5a2e" />
				<rect x={x - 0.02} y={y + 0.94} width="1.04" height="0.12" fill="#8e5a2e" />
			{:else}
				<path d="M{x} {y + 0.25} h1 M{x} {y + 0.5} h1 M{x} {y + 0.75} h1" stroke="#a46a37" stroke-width="0.05" />
				<rect x={x - 0.06} y={y - 0.02} width="0.12" height="1.04" fill="#8e5a2e" />
				<rect x={x + 0.94} y={y - 0.02} width="0.12" height="1.04" fill="#8e5a2e" />
			{/if}
		{/each}
	{/snippet}
</World>
