<!--
	A diagram or photograph (lib/diagrams.ts) as a question's picture: framed and kept to its shape while it
	loads. Its credit is in static/rajah/CREDITS.txt, not on the screen. It cannot be dragged out or saved
	with a long press.
-->
<script lang="ts">
	import { diagramOf, diagramUrl } from '$lib/diagrams';

	let { key, max = 240 }: { key: string; max?: number } = $props();
	const d = $derived(diagramOf(key));
</script>

{#if d}
	<figure class="rajah" class:photo={d.photo} style:--max="{max}px">
		<img src={diagramUrl(d.key)} alt="Gambar rajah soalan" width={d.w} height={d.h} style:aspect-ratio="{d.w} / {d.h}" loading="eager" decoding="async" draggable="false" />
	</figure>
{/if}

<style>
	.rajah {
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		margin: 0;
		padding: 0.5rem;
		border: 2px solid var(--line, #e2d6c4);
		border-radius: var(--r-md, 12px);
		background: #fff;
	}
	img {
		display: block;
		width: auto;
		max-width: 100%;
		height: auto;
		max-height: var(--max);
		object-fit: contain;
		user-select: none;
		pointer-events: none;
		-webkit-user-drag: none;
	}
	.photo img {
		border-radius: 8px;
	}
</style>
