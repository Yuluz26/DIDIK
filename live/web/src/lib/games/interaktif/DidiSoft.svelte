<!--
	Didi, whole and soft (the logo's round face on a small round body), the guide of Kuiz Interaktif.
	Moods: `happy` (idle, bobbing), `cheer` (arms up, hopping), `oops` (a sweat drop, a gentle tilt),
	`think` (eyes up, a paw at the chin), `wave` (one arm waving). Decorative unless `label` is given.
	With reduced motion Didi stays still.
-->
<script lang="ts" module>
	export type DidiMood = 'happy' | 'cheer' | 'oops' | 'think' | 'wave';
</script>

<script lang="ts">
	let { mood = 'happy', size = 120, label = '' }: { mood?: DidiMood; size?: number; label?: string } = $props();
</script>

<svg
	class="didi mood-{mood}"
	viewBox="0 0 120 132"
	width={size}
	height={Math.round(size * 1.1)}
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	aria-hidden={label ? undefined : 'true'}
	focusable="false"
>
	<ellipse class="shadow" cx="60" cy="127" rx="30" ry="4.5" />
	<g class="whole">
		<!-- tail -->
		<path class="tail fur" d="M86 104 C100 100 104 88 99 82 C96 90 90 95 84 97 Z" />
		<!-- body -->
		<ellipse class="fur" cx="60" cy="100" rx="27" ry="24" />
		<ellipse class="belly" cx="60" cy="104" rx="16" ry="16" />
		<!-- feet -->
		<ellipse class="fur dark" cx="47" cy="122" rx="9" ry="5" />
		<ellipse class="fur dark" cx="73" cy="122" rx="9" ry="5" />
		<!-- arms -->
		<g class="arm arm-l"><ellipse class="fur" cx="36" cy="98" rx="7" ry="11" /></g>
		<g class="arm arm-r"><ellipse class="fur" cx="84" cy="98" rx="7" ry="11" /></g>
		<!-- head: the logo's face, larger -->
		<g class="head" transform="translate(16 2) scale(1.375)">
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
			{#if mood === 'cheer'}
				<path d="M19.5 34 Q23.5 28 27.5 34" class="line" />
				<path d="M36.5 34 Q40.5 28 44.5 34" class="line" />
			{:else if mood === 'oops'}
				<ellipse cx="23.5" cy="33.5" rx="3.2" ry="3.6" class="eye" />
				<ellipse cx="40.5" cy="33.5" rx="3.2" ry="3.6" class="eye" />
				<circle cx="24.6" cy="32.3" r="1.1" class="shine" />
				<circle cx="41.6" cy="32.3" r="1.1" class="shine" />
				<path class="drop" d="M50 22 C52 26 53 28 51 29.5 C49 30.5 47.5 28.5 48.5 26.5 Z" />
			{:else}
				<g class="eyes" class:up={mood === 'think'}>
					<ellipse cx="23.5" cy="33" rx="4.2" ry="4.8" class="eye" />
					<ellipse cx="40.5" cy="33" rx="4.2" ry="4.8" class="eye" />
					<circle cx="25" cy="31.3" r="1.5" class="shine" />
					<circle cx="42" cy="31.3" r="1.5" class="shine" />
				</g>
			{/if}
			<ellipse cx="32" cy="40.5" rx="2.6" ry="1.9" class="nose" />
			{#if mood === 'cheer'}
				<path d="M27 43.5 Q32 51 37 43.5 Z" class="open" />
			{:else if mood === 'oops'}
				<path d="M28.8 46 Q32 44 35.2 46" class="mouth" />
			{:else}
				<path d="M28.6 44 Q30.4 46.2 32 44.6 Q33.6 46.2 35.4 44" class="mouth" />
			{/if}
			<ellipse cx="16.5" cy="40" rx="3.4" ry="2.1" class="blush" />
			<ellipse cx="47.5" cy="40" rx="3.4" ry="2.1" class="blush" />
		</g>
	</g>
</svg>

<style>
	.didi {
		display: block;
		overflow: visible;
	}
	.shadow {
		fill: rgb(60 40 90 / 0.14);
	}
	.fur {
		fill: var(--didi-fur, #e7b98a);
	}
	.fur.dark {
		fill: #d9a370;
	}
	.belly,
	.muzzle {
		fill: var(--didi-belly, #fff4e6);
	}
	.inner {
		fill: var(--didi-ear, #f7c6c0);
	}
	.eye {
		fill: #2a1f2d;
	}
	.shine {
		fill: #fff;
	}
	.nose {
		fill: #3a2a2a;
	}
	.mouth,
	.line {
		fill: none;
		stroke: #3a2a2a;
		stroke-width: 1.6;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
	.line {
		stroke-width: 2.4;
	}
	.open {
		fill: #c84b5b;
		stroke: #3a2a2a;
		stroke-width: 1.2;
		stroke-linejoin: round;
	}
	.blush {
		fill: #ff9aa8;
		opacity: 0.7;
	}
	.drop {
		fill: #7cc7ff;
	}
	.whole,
	.arm,
	.head,
	.eyes,
	.tail {
		transform-box: fill-box;
	}
	.arm-l {
		transform-origin: 80% 15%;
	}
	.arm-r {
		transform-origin: 20% 15%;
	}
	.tail {
		transform-origin: 0% 100%;
		animation: wag 0.9s ease-in-out infinite;
	}
	.whole {
		transform-origin: 50% 100%;
		animation: bob 2.6s ease-in-out infinite;
	}
	.eyes.up {
		transform: translateY(-1.4px) translateX(1px);
	}
	.mood-cheer .whole {
		animation: hop 0.62s cubic-bezier(0.34, 1.56, 0.64, 1) infinite alternate;
	}
	.mood-cheer .arm-l {
		transform: rotate(150deg);
	}
	.mood-cheer .arm-r {
		transform: rotate(-150deg);
	}
	.mood-cheer .tail {
		animation-duration: 0.35s;
	}
	.mood-oops .whole {
		animation: tilt 2.2s ease-in-out infinite;
	}
	.mood-think .arm-r {
		transform: rotate(-120deg) translateY(2px);
	}
	.mood-wave .arm-r {
		animation: wave 0.7s ease-in-out infinite alternate;
	}
	@keyframes bob {
		50% {
			transform: translateY(-3px) scale(1.01, 0.99);
		}
	}
	@keyframes hop {
		from {
			transform: translateY(0) scale(1.04, 0.96);
		}
		to {
			transform: translateY(-12px) scale(0.98, 1.03);
		}
	}
	@keyframes tilt {
		50% {
			transform: rotate(-5deg);
		}
	}
	@keyframes wave {
		from {
			transform: rotate(-120deg);
		}
		to {
			transform: rotate(-165deg);
		}
	}
	@keyframes wag {
		50% {
			transform: rotate(-14deg);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.whole,
		.tail,
		.arm {
			animation: none !important;
		}
	}
</style>
