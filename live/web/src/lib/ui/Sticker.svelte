<!-- One 3D sticker (lib/stickers.ts). Named for screen readers unless `alt` is "" (when words beside it
	already say what it is). It cannot be dragged out of the page or saved with a long press. -->
<script lang="ts">
	import { stickerOf, stickerUrl } from '$lib/stickers';

	let { key, size = 64, alt = undefined, eager = false }: { key: string; size?: number; alt?: string; eager?: boolean } = $props();

	const name = $derived(alt ?? stickerOf(key)?.name ?? '');
</script>

<img
	class="sticker"
	src={stickerUrl(key)}
	alt={name}
	width={size}
	height={size}
	loading={eager ? 'eager' : 'lazy'}
	decoding="async"
	draggable="false"
/>

<style>
	.sticker {
		display: block;
		flex: none;
		object-fit: contain;
		pointer-events: none;
		user-select: none;
		-webkit-user-drag: none;
	}
</style>
