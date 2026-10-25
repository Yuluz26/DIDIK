<!--
	One cell of a pixel sheet on screen, `s` CSS pixels per base pixel. With `frames`, it plays the
	cells of one row from `col` onwards in steps, the way an old game flips its sprites.
-->
<script lang="ts">
	import { type Sheet, prescale, rowUrl } from './cache';

	let {
		sheet,
		s,
		col = 0,
		row = 0,
		frames = 1,
		ms = 600,
		delay = 0,
		flip = false,
		play = true
	}: {
		sheet: Sheet;
		s: number;
		col?: number;
		row?: number;
		frames?: number;
		ms?: number;
		delay?: number;
		flip?: boolean;
		play?: boolean;
	} = $props();

	const k = $derived(prescale(s));
	const url = $derived(rowUrl(sheet, row, k));
	// Cells are an even number of pixels wide, so a sprite centred on a point never sits on half a pixel.
	const cw = $derived(2 * Math.round((sheet.cw * s) / 2));
	const ch = $derived(Math.round(sheet.ch * s));
	const full = $derived(cw * sheet.cols);
	const x0 = $derived(-col * cw);
</script>

<span class="cell" style:width="{cw}px" style:height="{ch}px" style:transform={flip ? 'scaleX(-1)' : undefined} aria-hidden="true">
	{#if frames > 1 && play}
		<img
			class="sheet play"
			src={url}
			alt=""
			draggable="false"
			style:width="{full}px"
			style:height="{ch}px"
			style:--x0="{x0}px"
			style:--x1="{x0 - frames * cw}px"
			style:--ms="{ms}ms"
			style:--n={frames}
			style:--delay="{delay}ms"
		/>
	{:else}
		<img class="sheet" src={url} alt="" draggable="false" style:width="{full}px" style:height="{ch}px" style:transform="translateX({x0}px)" />
	{/if}
</span>

<style>
	.cell {
		position: relative;
		display: inline-block;
		flex: none;
		overflow: hidden;
		line-height: 0;
		vertical-align: top;
	}
	.sheet {
		position: absolute;
		left: 0;
		top: 0;
		max-width: none;
		user-select: none;
		pointer-events: none;
	}
	.play {
		transform: translateX(var(--x0));
		animation: px-frames var(--ms) steps(var(--n)) var(--delay) infinite;
	}
	@keyframes px-frames {
		from {
			transform: translateX(var(--x0));
		}
		to {
			transform: translateX(var(--x1));
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.play {
			animation: none;
		}
	}
</style>
