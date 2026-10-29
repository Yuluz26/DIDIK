<!--
	The DIDIK logo: Didi, the chihuahua mascot, drawn round and soft (not in pixels), and the word
	DIDIK in the rounded display face, each letter its own cheerful colour. The letters pop in once
	when the page opens; afterwards Didi blinks and twitches an ear now and then, and the letters hop
	when the logo is hovered or focused. With reduced motion nothing moves.
-->
<script lang="ts">
	// `light`: on a dark or blue backdrop (the front page's sea). `compact`: on narrow screens only
	// the mascot shows, leaving room for a header's links. `tagline`: the small "main bersama" line.
	let {
		href = '/',
		light = false,
		compact = false,
		tagline = true
	}: { href?: string; light?: boolean; compact?: boolean; tagline?: boolean } = $props();

	const LETTERS = [
		{ ch: 'D', tone: 'sun' },
		{ ch: 'I', tone: 'coral' },
		{ ch: 'D', tone: 'sea' },
		{ ch: 'I', tone: 'leaf' },
		{ ch: 'K', tone: 'berry' }
	];
</script>

<a class="logo" class:light class:compact {href} aria-label="DIDIK Main Bersama, laman utama">
	<svg class="didi" viewBox="0 0 64 64" width="44" height="44" aria-hidden="true" focusable="false">
		<ellipse class="shadow" cx="32" cy="60" rx="17" ry="2.6" />
		<g class="head">
			<g class="ear ear-l">
				<path d="M15 27 C8 13 9 6 13 4 C18 3 24 12 27 20 Z" class="fur" />
				<path d="M16 23 C12 14 13 9 15 8 C18 8 21 14 23 19 Z" class="inner" />
			</g>
			<g class="ear ear-r">
				<path d="M49 27 C56 13 55 6 51 4 C46 3 40 12 37 20 Z" class="fur" />
				<path d="M48 23 C52 14 51 9 49 8 C46 8 43 14 41 19 Z" class="inner" />
			</g>
			<ellipse cx="32" cy="35" rx="21" ry="19" class="fur" />
			<ellipse cx="32" cy="44" rx="11" ry="8" class="muzzle" />
			<g class="eyes">
				<ellipse cx="23.5" cy="33" rx="4.2" ry="4.8" class="eye" />
				<ellipse cx="40.5" cy="33" rx="4.2" ry="4.8" class="eye" />
				<circle cx="25" cy="31.3" r="1.5" class="shine" />
				<circle cx="42" cy="31.3" r="1.5" class="shine" />
			</g>
			<ellipse cx="32" cy="40.5" rx="2.6" ry="1.9" class="nose" />
			<path d="M28.6 44 Q30.4 46.2 32 44.6 Q33.6 46.2 35.4 44" class="mouth" />
			<ellipse cx="16.5" cy="40" rx="3.4" ry="2.1" class="blush" />
			<ellipse cx="47.5" cy="40" rx="3.4" ry="2.1" class="blush" />
		</g>
	</svg>
	<span class="word">
		<span class="letters" aria-hidden="true">
			{#each LETTERS as letter, i (i)}<span class="letter tone-{letter.tone}" style:--i={i}>{letter.ch}</span>{/each}
		</span>
		{#if tagline}<span class="tag" aria-hidden="true">main bersama</span>{/if}
	</span>
</a>

<style>
	.logo {
		--logo-ink: var(--ink);
		display: inline-flex;
		align-items: center;
		gap: 0.55rem;
		color: var(--logo-ink);
		text-decoration: none;
		border-radius: 14px;
	}
	.logo.light {
		--logo-ink: #ffffff;
	}
	.logo:focus-visible {
		outline: 3px solid var(--sun);
		outline-offset: 4px;
	}

	/* Didi */
	.didi {
		flex: none;
		overflow: visible;
		filter: drop-shadow(0 2px 0 rgb(31 45 39 / 0.18));
	}
	.fur {
		fill: var(--didi-fur);
		stroke: #6b4a2e;
		stroke-width: 1.6;
		stroke-linejoin: round;
	}
	.inner {
		fill: var(--didi-ear);
	}
	.muzzle {
		fill: var(--didi-belly);
	}
	.eye {
		fill: #2b2133;
	}
	.shine {
		fill: #ffffff;
	}
	.nose {
		fill: #2b2133;
	}
	.mouth {
		fill: none;
		stroke: #2b2133;
		stroke-width: 1.4;
		stroke-linecap: round;
	}
	.blush {
		fill: #f59aa5;
		opacity: 0.75;
	}
	.shadow {
		fill: rgb(0 0 0 / 0.16);
	}
	.head {
		transform-box: fill-box;
		transform-origin: 50% 90%;
	}
	.eyes {
		transform-box: fill-box;
		transform-origin: 50% 50%;
		animation: blink 5.2s ease-in-out infinite;
	}
	.ear {
		transform-box: fill-box;
	}
	.ear-l {
		transform-origin: 85% 90%;
		animation: ear-l 6.5s ease-in-out infinite;
	}
	.ear-r {
		transform-origin: 15% 90%;
		animation: ear-r 6.5s ease-in-out 1.3s infinite;
	}
	.logo:hover .head,
	.logo:focus-visible .head {
		animation: nod 520ms cubic-bezier(0.3, 1.6, 0.5, 1);
	}

	/* the word */
	.word {
		display: grid;
		line-height: 1;
	}
	.letters {
		display: inline-flex;
		font: 700 1.6rem/1 var(--font-display);
		letter-spacing: 0.02em;
	}
	.letter {
		display: inline-block;
		color: var(--tone);
		/* a soft ink edge under each letter, so the colours read on cream and on the blue sea */
		text-shadow:
			0 2px 0 var(--tone-deep),
			0 3px 6px rgb(31 45 39 / 0.18);
		animation: pop-in 520ms cubic-bezier(0.25, 1.6, 0.5, 1) both;
		animation-delay: calc(var(--i) * 70ms);
	}
	.logo:hover .letter,
	.logo:focus-visible .letter {
		animation: hop 480ms cubic-bezier(0.3, 1.5, 0.5, 1) both;
		animation-delay: calc(var(--i) * 45ms);
	}
	.tone-sun {
		--tone: var(--sun);
		--tone-deep: var(--sun-deep);
	}
	.tone-coral {
		--tone: #f0654d;
		--tone-deep: var(--coral-deep);
	}
	.tone-sea {
		--tone: #19a99c;
		--tone-deep: var(--sea-deep);
	}
	.tone-leaf {
		--tone: var(--leaf);
		--tone-deep: var(--leaf-deep);
	}
	.tone-berry {
		--tone: #e2549f;
		--tone-deep: var(--berry-deep);
	}
	.tag {
		margin-top: 0.18rem;
		color: var(--logo-ink);
		opacity: 0.85;
		font: 700 0.7rem/1 var(--font-display);
		letter-spacing: 0.14em;
		text-transform: uppercase;
	}

	@keyframes pop-in {
		from {
			opacity: 0;
			transform: translateY(0.5rem) scale(0.6);
		}
	}
	@keyframes hop {
		40% {
			transform: translateY(-0.28rem) rotate(-4deg);
		}
	}
	@keyframes nod {
		45% {
			transform: rotate(-7deg) scale(1.05);
		}
	}
	@keyframes blink {
		0%,
		92%,
		100% {
			transform: scaleY(1);
		}
		95% {
			transform: scaleY(0.12);
		}
	}
	@keyframes ear-l {
		0%,
		86%,
		100% {
			transform: rotate(0deg);
		}
		90% {
			transform: rotate(-12deg);
		}
		94% {
			transform: rotate(4deg);
		}
	}
	@keyframes ear-r {
		0%,
		86%,
		100% {
			transform: rotate(0deg);
		}
		90% {
			transform: rotate(12deg);
		}
		94% {
			transform: rotate(-4deg);
		}
	}
	@media (max-width: 560px) {
		.compact .word {
			display: none;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.letter,
		.eyes,
		.ear-l,
		.ear-r,
		.logo:hover .letter,
		.logo:hover .head,
		.logo:focus-visible .letter,
		.logo:focus-visible .head {
			animation: none;
		}
	}
</style>
