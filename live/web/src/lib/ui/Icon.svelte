<!--
	The interface's small icons, drawn a pixel at a time on an 11 × 11 grid (lib/pixel/glyphs.ts) and
	filled with the colour of the text they sit in. They stay sharp at whole multiples of eleven
	pixels, so `size` picks the nearest one (11, 22 or 33). Decorative by default; pass `label` when
	the icon is the only content of a control.
-->
<script lang="ts">
	import { GLYPH, glyphPath } from '$lib/pixel/glyphs';

	let { name, size = 22, label = '' }: { name: string; size?: number; label?: string } = $props();

	const px = $derived(size < 17 ? GLYPH : Math.round(size / GLYPH) * GLYPH);
</script>

<svg
	class="icon"
	viewBox="0 0 {GLYPH} {GLYPH}"
	width={px}
	height={px}
	shape-rendering="crispEdges"
	focusable="false"
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	aria-hidden={label ? undefined : 'true'}
>
	<path d={glyphPath(name)} />
</svg>

<style>
	.icon {
		flex: none;
		fill: currentColor;
	}
</style>
