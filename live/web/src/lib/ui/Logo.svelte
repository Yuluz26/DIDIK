<!-- The mark is Didi's head on a green tile, in pixels (lib/pixel/icons.ts), at twice its size. -->
<script lang="ts">
	import { logoMark } from '$lib/pixel/icons';
	import Sprite from '$lib/pixel/Sprite.svelte';

	// `compact`: on narrow screens only the mark shows, leaving room for a header's links.
	let { href = '/', light = false, compact = false }: { href?: string; light?: boolean; compact?: boolean } = $props();
</script>

<a class="logo" class:light class:compact {href} aria-label="DIDIK Main Bersama, laman utama">
	<span class="mark"><Sprite sheet={logoMark()} s={2} /></span>
	<span class="word">didik <span>main bersama</span></span>
</a>

<style>
	.logo {
		display: inline-flex;
		align-items: center;
		gap: 0.6rem;
		color: var(--ink);
		text-decoration: none;
		font: 600 1.35rem/1 var(--font-display);
	}
	.logo.light {
		color: #fff;
	}
	.mark {
		flex: none;
		line-height: 0;
		transition: transform var(--t-press) steps(2);
	}
	.logo:hover .mark {
		transform: translateY(-2px);
	}
	.word {
		white-space: nowrap;
	}
	.word span {
		color: var(--brand-ink);
		font-weight: 500;
	}
	.light .word span {
		color: inherit;
	}
	@media (max-width: 560px) {
		.compact .word {
			display: none;
		}
	}
</style>
