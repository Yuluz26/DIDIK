<!--
	One child's garden in Kebun Ajaib, in the worlds' 3/4 view: up to nine raised beds behind a fence,
	a hut, a water jar holding the child's water and a scarecrow, with the gardener standing among
	them. With `onbed`, every bed is a button. The garden always fits its container's width.
-->
<script lang="ts" module>
	export interface Plot {
		crop: string;
		stage: number;
	}

	export interface CropInfo {
		name: string;
		cost: number;
		water: number;
		value: number;
	}

	export const COLUMNS = [2.0, 5.6, 9.2];
	export const ROWS = [4.3, 7.0, 9.7];
	/** Where bed `i` stands: the middle of its front edge, in tiles. */
	export const bedAt = (i: number): [number, number] => [COLUMNS[i % 3], ROWS[Math.floor(i / 3)]];
</script>

<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { Person } from '$lib/types';
	import { fitTile } from '$lib/pixel/cache';
	import GardenBed from '$lib/worlds/GardenBed.svelte';
	import World, { type WorldActor, type WorldProp } from '$lib/worlds/World.svelte';
	import { gardenGround } from './sprites';

	let {
		plots,
		crops,
		maxPlots = 9,
		water = null,
		owner = null,
		spot = null,
		walking = false,
		labels = [],
		onbed,
		overlay,
		maxTile = 56
	}: {
		plots: (Plot | null)[];
		crops: Record<string, CropInfo>;
		maxPlots?: number;
		water?: number | null;
		owner?: Person | null;
		spot?: [number, number] | null;
		walking?: boolean;
		labels?: string[];
		onbed?: (index: number) => void;
		overlay?: Snippet<[number]>;
		maxTile?: number;
	} = $props();

	const W = 14;
	const H = 11;
	const HOME: [number, number] = [11.3, 6.7];

	const SCENERY: WorldProp[] = [
		...[0.8, 2.6, 4.4, 6.2, 8.0, 9.8, 11.6, 13.4].map((x, i) => ({ id: `back${i}`, kind: i % 3 === 2 ? 'palm' : 'tree', x, y: 1.0 + (i % 2) * 0.12, variant: i % 3 })),
		...Array.from({ length: 13 }, (_, i) => ({ id: `fence${i}`, kind: 'fence', x: 0.55 + i * 1.05, y: 1.75 })),
		{ id: 'pondok', kind: 'pondok', x: 12.3, y: 4.1 },
		{ id: 'scarecrow', kind: 'scarecrow', x: 12.7, y: 9.3 },
		{ id: 'bush', kind: 'bush', x: 11.2, y: 10.6, variant: 1 },
		{ id: 'flowers', kind: 'flowers', x: 13.4, y: 10.5 }
	];

	let width = $state(0);
	const tile = $derived(fitTile(width, W, { max: maxTile }));
	const ground = gardenGround(W, H);

	const items = $derived<WorldProp[]>([
		...SCENERY,
		{ id: 'tempayan', kind: 'tempayan', x: 11.6, y: 5.6, badge: water ?? undefined },
		...Array.from({ length: maxPlots }, (_, i) => {
			const [x, y] = bedAt(i);
			return {
				id: `bed-${i}`,
				kind: 'bed',
				custom: true,
				x,
				y,
				label: labels[i],
				action: onbed ? () => onbed?.(i) : undefined
			};
		})
	]);

	const actors = $derived<WorldActor[]>(
		owner
			? [
					{
						id: owner.id,
						x: (spot ?? HOME)[0],
						y: (spot ?? HOME)[1],
						facing: (spot ?? HOME)[0] > 7 ? -1 : 1,
						walking,
						animal: owner.avatar,
						colour: owner.colour,
						skin: owner.skin,
						name: owner.name
					}
				]
			: []
	);
</script>

{#snippet art(prop: WorldProp, tile: number)}
	{@const i = Number(prop.id.slice(4))}
	{@const plot = plots[i]}
	<GardenBed crop={plot?.crop ?? null} stage={plot?.stage ?? 0} need={plot ? (crops[plot.crop]?.water ?? 1) : 0} locked={i >= plots.length} {tile} />
{/snippet}

<div class="garden" bind:clientWidth={width}>
	<div class="fit" style:max-width="{W * tile}px">
		<World width={W} height={H} {tile} {ground} props={items} {actors} me={onbed ? (owner?.id ?? null) : null} names={onbed ? 'me' : true} step={520} {art} {overlay} />
	</div>
</div>

<style>
	.garden {
		min-width: 0;
	}
	.fit {
		margin-inline: auto;
	}
</style>
