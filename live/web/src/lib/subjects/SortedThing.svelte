<!-- A thing sitting in a group of a sorting game: its picture and name, a mark once shown, movable while playing. -->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import GameImage from './GameImage.svelte';
	import Mark from './Mark.svelte';
	import type { SortThing, SortView } from './SortPlay.svelte';

	let {
		v,
		item,
		group,
		size = 32,
		dark = false,
		photo
	}: { v: SortView; item: SortThing; group: string; size?: number; dark?: boolean; /** a picture from the games' library, shown instead of a sticker */ photo?: string | null } = $props();
	const pic = $derived(v.sticker(item));
	const ok = $derived(v.ok(item.id));
</script>

<span class="wrap">
	<button type="button" class="in" class:dark class:ok={ok === true} class:off={ok === false} disabled={v.locked} {@attach v.grab(item.id, group)} aria-label="{item.text}. Ketik untuk keluarkan">
		{#if photo}
			<span class="photo" style:width="{size}px" style:height="{size}px">
				<GameImage name={photo} fit="cover">
					{#snippet fallback()}{#if pic}<Sticker key={pic} {size} alt="" />{/if}{/snippet}
				</GameImage>
			</span>
		{:else if pic}<Sticker key={pic} {size} alt="" />{/if}
		<span>{item.text}</span>
		{#if ok !== null}<Mark {ok} size={12} />{/if}
	</button>
	{#if v.should(item.id)}<span class="should">→ {v.should(item.id)}</span>{/if}
</span>

<style>
	.photo {
		display: grid;
		place-items: center;
		flex: none;
		overflow: hidden;
		border-radius: 22%;
		background: #fff;
	}
	.photo :global(img.g-img) {
		width: 100%;
		height: 100%;
	}
	.wrap {
		display: inline-grid;
		justify-items: center;
		gap: 0.1rem;
		max-width: 100%;
	}
	.in {
		position: relative;
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		max-width: 100%;
		padding: 0.25rem 0.55rem 0.25rem 0.3rem;
		border: 0;
		border-radius: 10px;
		background: rgb(255 255 255 / 0.92);
		color: var(--ink);
		font: 700 0.85rem/1.1 var(--font-body);
		box-shadow: 0 2px 0 rgb(0 0 0 / 0.12);
		cursor: grab;
		touch-action: none;
		animation: land 0.3s var(--spring, ease-out);
	}
	.in.dark {
		background: rgb(0 0 0 / 0.35);
		color: #fff;
	}
	.in:disabled {
		cursor: default;
	}
	.in.ok {
		box-shadow: 0 0 0 3px var(--good);
	}
	.in.off {
		box-shadow: 0 0 0 3px var(--almost);
	}
	.in:global(.dragging) {
		z-index: 50;
	}
	.should {
		color: #8a2a00;
		background: rgb(255 255 255 / 0.85);
		border-radius: 4px;
		padding: 0 0.25rem;
		font-weight: 800;
		font-size: 0.72rem;
	}
	@keyframes land {
		from {
			transform: scale(0.6);
			opacity: 0;
		}
	}
</style>
