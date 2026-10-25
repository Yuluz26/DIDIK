<!--
	Kampung Kita's buildings in the same front-and-above view as the other props, in pixels (see
	buildings.ts). The foot (bottom centre) is the middle of the building's front edge.

	A building under construction rises from the ground as material arrives: the finished building
	stands faintly behind the scaffolding, and the built part fills in from the bottom up, a row of
	pixels at a time.
-->
<script lang="ts" module>
	export const BUILDING_KINDS = ['rumah', 'kedai', 'sekolah', 'jeti', 'masjid', 'rumahpanjang', 'balai'];
</script>

<script lang="ts">
	import { TILE } from '$lib/pixel/cache';
	import Sprite from '$lib/pixel/Sprite.svelte';
	import { B, buildingArt, materialsSheet, plotSheet } from './buildings';

	let {
		kind,
		tile = 44,
		state = 'done',
		progress = 0
	}: { kind: string; tile?: number; state?: string; progress?: number } = $props();

	const s = $derived(tile / TILE);
	const art = $derived(buildingArt(kind));
	// The rows above the walls' height are still empty.
	const hidden = $derived(Math.round((1 - Math.max(0, Math.min(1, progress))) * (B.h - 6)) + 6);
	const sign = $derived(art?.sign);
</script>

{#if art}
	<span class="building {state}" style:width="{B.w * s}px" style:height="{B.h * s}px" style:--s="{s}px">
		{#if state === 'plot'}
			<span class="layer"><Sprite sheet={plotSheet()} {s} /></span>
		{:else if state === 'building'}
			<span class="layer ghost"><Sprite sheet={art.sheet} {s} /></span>
			<span class="layer built" style:clip-path="inset({hidden * s}px 0 0 0)"><Sprite sheet={art.sheet} {s} /></span>
			<span class="pole" style:left="{3 * s}px" style:top="{(hidden - 5) * s}px" style:height="{(B.h - hidden + 4) * s}px"></span>
			<span class="pole" style:left="{46 * s}px" style:top="{(hidden - 5) * s}px" style:height="{(B.h - hidden + 4) * s}px"></span>
			<span class="plank" style:top="{(hidden - 6) * s}px"></span>
			<span class="layer"><Sprite sheet={materialsSheet()} {s} /></span>
		{:else}
			<span class="layer"><Sprite sheet={art.sheet} {s} /></span>
			{#if sign}
				<span
					class="sign"
					style:left="{sign.x * s}px"
					style:top="{sign.y * s}px"
					style:width="{sign.w * s}px"
					style:height="{sign.h * s}px"
					style:color={sign.colour}
					style:font-size="{Math.min(sign.h * s * 0.8, (sign.w * s) / (sign.text.length * 0.62))}px">{sign.text}</span
				>
			{/if}
		{/if}
	</span>
{/if}

<style>
	.building {
		position: relative;
		display: block;
		line-height: 0;
	}
	.layer {
		position: absolute;
		inset: 0;
	}
	.ghost {
		opacity: 0.22;
	}
	.built {
		transition: clip-path 700ms steps(8);
	}
	.pole,
	.plank {
		position: absolute;
		background: #b98657;
		box-shadow:
			inset var(--s) 0 0 #d8a877,
			inset calc(var(--s) * -1) 0 0 #8c5e41,
			0 0 0 var(--s) #4a2c22;
		transition:
			top 700ms steps(8),
			height 700ms steps(8);
	}
	.pole {
		width: calc(var(--s) * 3);
	}
	.plank {
		left: calc(var(--s) * 1);
		width: calc(var(--s) * 50);
		height: calc(var(--s) * 2);
	}
	.sign {
		position: absolute;
		display: grid;
		place-items: center;
		font-family: var(--font-pixel);
		font-weight: 700;
		line-height: 1;
		letter-spacing: 0.03em;
		white-space: nowrap;
		pointer-events: none;
	}
	.done {
		transform-origin: 50% 96%;
		animation: stand-up 500ms steps(3);
	}
	@keyframes stand-up {
		from {
			transform: translateY(calc(var(--s) * 3));
		}
	}
</style>
