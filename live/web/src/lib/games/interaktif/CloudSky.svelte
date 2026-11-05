<!--
	The backdrop of Kuiz Interaktif: a candy-floss sky over soft hills, a pastel rainbow, puffy clouds that
	drift by and a few twinkles. Drawn with CSS and one SVG, so it is sharp on any screen and costs no
	download. Decorative only; it sits behind everything and never takes a tap. Still with reduced motion.
-->
<script lang="ts">
	let { mood = 'day' }: { mood?: 'day' | 'party' } = $props();

	const CLOUDS = [
		{ top: 8, size: 1.1, speed: 70, delay: -10 },
		{ top: 22, size: 0.7, speed: 95, delay: -60 },
		{ top: 40, size: 0.9, speed: 80, delay: -35 },
		{ top: 15, size: 0.55, speed: 120, delay: -90 }
	];
	const TWINKLES = [
		{ x: 12, y: 18, d: 0 },
		{ x: 84, y: 12, d: 0.8 },
		{ x: 68, y: 34, d: 1.6 },
		{ x: 22, y: 46, d: 2.2 },
		{ x: 92, y: 52, d: 1.1 }
	];
</script>

<div class="sky" class:party={mood === 'party'} aria-hidden="true">
	<div class="sun"></div>
	<svg class="rainbow" viewBox="0 0 200 100" preserveAspectRatio="xMidYMax meet">
		{#each ['#ffb3c7', '#ffd59e', '#fff3a6', '#bff0c4', '#b9dcff', '#d9c6ff'] as colour, i (colour)}
			<path d="M {10 + i * 7} 100 A {90 - i * 7} {90 - i * 7} 0 0 1 {190 - i * 7} 100" stroke={colour} />
		{/each}
	</svg>
	{#each CLOUDS as c, i (i)}
		<span class="cloud" style:--top="{c.top}%" style:--size={c.size} style:--speed="{c.speed}s" style:--delay="{c.delay}s"></span>
	{/each}
	{#each TWINKLES as t, i (i)}
		<span class="twinkle" style:left="{t.x}%" style:top="{t.y}%" style:--d="{t.d}s"></span>
	{/each}
	<svg class="hills" viewBox="0 0 1200 220" preserveAspectRatio="none">
		<path class="far" d="M0 120 C150 60 300 70 420 110 C560 155 700 60 860 80 C1000 98 1100 60 1200 90 V220 H0 Z" />
		<path class="near" d="M0 170 C180 120 320 140 480 160 C640 182 760 120 920 130 C1060 140 1140 160 1200 150 V220 H0 Z" />
		{#each [80, 230, 390, 560, 700, 860, 1010, 1130] as x, i (x)}
			<g class="flower" transform="translate({x} {178 - (i % 3) * 10})">
				<circle r="5" cx="-5" fill="#fff" /><circle r="5" cx="5" fill="#fff" /><circle r="5" cy="-5" fill="#fff" /><circle r="5" cy="5" fill="#fff" />
				<circle r="4" fill={['#ffd166', '#ff9fb8', '#b9a3ff'][i % 3]} />
			</g>
		{/each}
	</svg>
</div>

<style>
	.sky {
		position: fixed;
		inset: 0;
		z-index: 0;
		overflow: hidden;
		pointer-events: none;
		background: linear-gradient(180deg, #ffdcee 0%, #eadfff 34%, #d4efff 66%, #e6fbe8 100%);
	}
	.sky.party {
		background: linear-gradient(180deg, #ffe7a8 0%, #ffd6ea 40%, #e2d6ff 75%, #d8f6ff 100%);
	}
	.sun {
		position: absolute;
		top: -6vmin;
		right: -4vmin;
		width: 34vmin;
		height: 34vmin;
		border-radius: 50%;
		background: radial-gradient(circle, #fff6c2 0 38%, rgb(255 236 150 / 0.55) 55%, transparent 70%);
		animation: glow 6s ease-in-out infinite;
	}
	.rainbow {
		position: absolute;
		left: -8vmin;
		bottom: 14vh;
		width: 70vmin;
		opacity: 0.55;
	}
	.rainbow path {
		fill: none;
		stroke-width: 7;
	}
	.cloud {
		position: absolute;
		top: var(--top);
		left: 0;
		width: calc(9rem * var(--size));
		height: calc(3rem * var(--size));
		border-radius: 999px;
		background: #fff;
		box-shadow:
			0 6px 0 rgb(214 200 240 / 0.6),
			calc(1.6rem * var(--size)) calc(-1.4rem * var(--size)) 0 calc(0.4rem * var(--size)) #fff,
			calc(4.4rem * var(--size)) calc(-1rem * var(--size)) 0 calc(0.9rem * var(--size)) #fff;
		opacity: 0.92;
		animation: drift var(--speed) linear infinite;
		animation-delay: var(--delay);
	}
	.twinkle {
		position: absolute;
		width: 14px;
		height: 14px;
		background: #fff;
		clip-path: polygon(50% 0, 62% 38%, 100% 50%, 62% 62%, 50% 100%, 38% 62%, 0 50%, 38% 38%);
		animation: twinkle 2.6s ease-in-out infinite;
		animation-delay: var(--d);
	}
	.hills {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		width: 100%;
		height: 22vh;
		min-height: 120px;
	}
	.far {
		fill: #bfe8c9;
	}
	.near {
		fill: #9fdcae;
	}
	@keyframes drift {
		from {
			transform: translateX(-30vw);
		}
		to {
			transform: translateX(120vw);
		}
	}
	@keyframes twinkle {
		0%,
		100% {
			opacity: 0.2;
			transform: scale(0.6);
		}
		50% {
			opacity: 1;
			transform: scale(1.1) rotate(20deg);
		}
	}
	@keyframes glow {
		50% {
			transform: scale(1.06);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.cloud,
		.twinkle,
		.sun {
			animation: none;
		}
		.cloud {
			transform: translateX(calc(var(--top) * 4));
		}
	}
</style>
