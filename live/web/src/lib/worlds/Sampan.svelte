<!--
	A sampan with a child paddling it, drawn in the worlds' 3/4 view: the back of the hull, the child,
	then the front of the hull, so the child sits inside the boat. The flag is the child's colour.
	`rowing` swings the paddle and leaves a little wake. Anything passed as children (a name tag) is
	placed by the caller inside the boat's box.
-->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { COLOURS } from '$lib/names';
	import Chibi from '$ui/Chibi.svelte';

	let {
		tile,
		animal,
		colour,
		skin,
		mood = 'happy',
		rowing = false,
		facing = 1,
		children
	}: {
		tile: number;
		animal: string;
		colour: string;
		skin?: string;
		mood?: 'happy' | 'cheer' | 'oops' | 'sleep';
		rowing?: boolean;
		facing?: number;
		children?: Snippet;
	} = $props();
</script>

<div class="boat" class:rowing class:back={facing < 0} style:--t="{tile}px" style:--flag={COLOURS[colour] ?? COLOURS.hijau}>
	{@render children?.()}
	<svg class="hull" viewBox="0 0 120 50" aria-hidden="true" focusable="false">
		<ellipse cx="60" cy="46" rx="56" ry="5" fill="#bfe6f6" opacity=".8" />
		<path class="wake" d="M-6 40 q8 -6 16 0 M-20 44 q8 -6 16 0" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" />
		<rect x="11" y="-16" width="3" height="32" fill="#8e5a2e" />
		<path d="M14 -16 l18 6 -18 6z" fill="var(--flag)" />
		<ellipse cx="60" cy="16" rx="57" ry="12" fill="#c9572e" />
		<ellipse cx="60" cy="16.5" rx="51" ry="8.5" fill="#6b3a20" />
	</svg>
	<span class="rider">
		<Chibi {animal} {colour} {skin} size={Math.round(tile * 0.95)} {mood} walking={false} facing={facing < 0 ? -1 : 1} />
	</span>
	<svg class="hull" viewBox="0 0 120 50" aria-hidden="true" focusable="false">
		<path class="paddle" d="M78 2 L96 44" stroke="#8e5a2e" stroke-width="4" stroke-linecap="round" />
		<ellipse class="paddle blade" cx="97" cy="45" rx="5" ry="8" fill="#a46a37" transform="rotate(-24 97 45)" />
		<path d="M3 16 Q8 44 60 46 Q112 44 117 16 Q60 31 3 16z" fill="#c9572e" />
		<path d="M12 27 Q60 41 108 27" stroke="#f7c948" stroke-width="3.5" fill="none" stroke-linecap="round" />
		<path d="M3 16 Q60 31 117 16" stroke="#e8774c" stroke-width="3" fill="none" />
	</svg>
</div>

<style>
	.boat {
		position: relative;
		width: calc(var(--t) * 2.4);
		height: calc(var(--t) * 1.75);
		animation: bob-boat 2.8s ease-in-out infinite;
	}
	/* Sailing left: the whole boat turns round, the child with it. */
	.back .hull {
		scale: -1 1;
	}
	.hull {
		position: absolute;
		left: 0;
		bottom: 0;
		width: 100%;
		height: calc(var(--t) * 1);
		overflow: visible;
	}
	.rider {
		position: absolute;
		left: 50%;
		bottom: calc(var(--t) * 0.45);
		translate: -46% 0;
		line-height: 0;
	}
	.wake {
		opacity: 0;
	}
	.rowing .wake {
		animation: wake 0.7s ease-out 2;
	}
	.paddle {
		transform-box: view-box;
		transform-origin: 78px 2px;
	}
	.rowing .paddle {
		animation: row 0.45s ease-in-out 3;
	}
	/* At rest the paddle lies in the boat; its blade only shows in the water while rowing. */
	.blade {
		opacity: 0;
		transition: opacity var(--t-state);
	}
	.rowing .blade {
		opacity: 1;
	}
	@keyframes bob-boat {
		0%,
		100% {
			transform: translateY(0) rotate(-1deg);
		}
		50% {
			transform: translateY(-2px) rotate(1deg);
		}
	}
	@keyframes row {
		50% {
			transform: rotate(28deg);
		}
	}
	@keyframes wake {
		from {
			opacity: 1;
			transform: translateX(0);
		}
		to {
			opacity: 0;
			transform: translateX(-10px);
		}
	}
</style>
