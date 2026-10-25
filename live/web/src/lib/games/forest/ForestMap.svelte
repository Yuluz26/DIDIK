<!--
	Hutan Misteri's forest, drawn from the same rows the server walks on: flat ground (grass, paths,
	river, bridges) and, standing on it, trees, rocks, flowers, chests and the gate, with every child's
	character walking among them in depth order.
-->
<script lang="ts">
	import type { Person } from '$lib/types';
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';
	import { forestGround } from './sprites';

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
		tile = 48,
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

<World width={W} height={H} {tile} ground={forestGround(map)} props={items} {actors} {me} {follow} />
