<!--
	Stickers float up above the sender's animal. Rendered as an overlay on a wall of avatars: each
	avatar element carries data-player so the sticker can find where to appear.
-->
<script lang="ts">
	import type { RoomClient } from '$lib/room.svelte';
	import { play } from '$lib/sound';
	import StickerArt from '$ui/StickerArt.svelte';

	let { client, within }: { client: RoomClient; within: HTMLElement | undefined } = $props();

	interface Floating {
		id: number;
		sticker: string;
		x: number;
		y: number;
	}

	let floating = $state<Floating[]>([]);
	let seq = 0;

	$effect(() =>
		client.onFx((fx) => {
			if (fx.kind !== 'sticker' || !within) return;
			const target = within.querySelector<HTMLElement>(`[data-player="${fx.player}"]`);
			if (!target) return;
			const box = within.getBoundingClientRect();
			const at = target.getBoundingClientRect();
			const id = ++seq;
			floating = [...floating, { id, sticker: fx.sticker, x: at.left - box.left + at.width / 2, y: at.top - box.top }];
			play('sticker');
			setTimeout(() => (floating = floating.filter((f) => f.id !== id)), 1800);
		})
	);
</script>

{#each floating as item (item.id)}
	<span class="float" style:left="{item.x}px" style:top="{item.y}px" aria-hidden="true">
		<StickerArt name={item.sticker} size={44} />
	</span>
{/each}

<style>
	.float {
		position: absolute;
		z-index: 5;
		translate: -50% -60%;
		pointer-events: none;
		animation: float-up 1.8s var(--ease-out) forwards;
	}
	@keyframes float-up {
		0% {
			opacity: 0;
			transform: scale(0.4);
		}
		15% {
			opacity: 1;
			transform: scale(1.15);
		}
		30% {
			transform: scale(1) translateY(-6px);
		}
		100% {
			opacity: 0;
			transform: translateY(-70px) rotate(-8deg);
		}
	}
</style>
