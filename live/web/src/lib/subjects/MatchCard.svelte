<!-- The card placed on a left-hand thing in a matching game: movable while playing, marked once shown. -->
<script lang="ts">
	import Mark from './Mark.svelte';
	import type { MatchView } from './MatchPlay.svelte';

	let { v, left, empty = 'Letak kad di sini', dark = false }: { v: MatchView; left: string; empty?: string; dark?: boolean } = $props();
	const card = $derived(v.placed(left));
	const ok = $derived(v.ok(left));
</script>

{#if card}
	<span class="wrap">
		<button type="button" class="placed" class:dark class:ok={ok === true} class:off={ok === false} disabled={v.locked} {@attach v.grab(left)} aria-label="{card.text}. Ketik untuk keluarkan">
			{card.text}
			{#if ok !== null}<Mark {ok} size={12} />{/if}
		</button>
		{#if v.should(left)}<span class="should">→ {v.should(left)}</span>{/if}
	</span>
{:else}
	<span class="empty" class:dark>{v.picked ? 'Ketik di sini' : empty}</span>
{/if}

<style>
	.wrap {
		display: inline-grid;
		justify-items: center;
		gap: 0.15rem;
	}
	.placed {
		position: relative;
		padding: 0.3rem 0.65rem;
		border: 0;
		border-radius: 8px;
		background: #fffdf6;
		color: var(--ink);
		font: 700 0.9rem/1.15 var(--font-body);
		box-shadow: 0 3px 0 rgb(0 0 0 / 0.15);
		cursor: grab;
		touch-action: none;
		animation: snap 0.3s var(--spring, ease-out);
	}
	.placed.dark {
		background: rgb(255 255 255 / 0.92);
	}
	.placed:disabled {
		cursor: default;
	}
	.placed.ok {
		box-shadow: 0 0 0 3px var(--good);
	}
	.placed.off {
		box-shadow: 0 0 0 3px var(--almost);
	}
	.placed:global(.dragging) {
		z-index: 50;
	}
	.should {
		padding: 0 0.3rem;
		border-radius: 4px;
		background: rgb(255 255 255 / 0.85);
		color: #8a2a00;
		font-weight: 800;
		font-size: 0.78rem;
	}
	.empty {
		color: var(--ink-3, #8a8a8a);
		font-weight: 700;
		font-size: 0.8rem;
	}
	.empty.dark {
		color: rgb(255 255 255 / 0.7);
	}
	@keyframes snap {
		from {
			transform: scale(0.7);
			opacity: 0;
		}
	}
</style>
