<!-- The eight stickers children can send in the lobby and during games, drawn in pixels. -->
<script lang="ts">
	import { snapScale } from '$lib/pixel/cache';
	import { sticker } from '$lib/pixel/icons';
	import Sprite from '$lib/pixel/Sprite.svelte';

	let { name, size = 40 }: { name: string; size?: number } = $props();

	const sheet = $derived(sticker(name));
	const s = $derived(snapScale(size / 16, 1));
</script>

<Sprite {sheet} {s} />
