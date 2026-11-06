<!--
	A plain figure in one of the positions of solat, read from the words of a step (takbir, rukuk, sujud...).
	Drawn as a silhouette in strokes, with no face.
-->
<script lang="ts" module>
	export type PoseKind = 'berdiri' | 'takbir' | 'rukuk' | 'iktidal' | 'sujud' | 'duduk' | 'salam';

	export function poseOf(text: string): PoseKind {
		const t = text.toLowerCase();
		if (/takbir/.test(t)) return 'takbir';
		if (/rukuk|ruku'/.test(t)) return 'rukuk';
		if (/iktidal|i'tidal|iktidāl/.test(t)) return 'iktidal';
		if (/sujud/.test(t) && !/antara/.test(t)) return 'sujud';
		if (/salam/.test(t)) return 'salam';
		if (/duduk|tahiyat|tasyahhud|antara dua sujud/.test(t)) return 'duduk';
		return 'berdiri';
	}
</script>

<script lang="ts">
	let { kind, size = 52 }: { kind: PoseKind; size?: number } = $props();
</script>

<svg class="pose" width={size} height={size} viewBox="0 0 60 60" aria-hidden="true">
	<line x1="4" y1="57" x2="56" y2="57" class="ground" />
	{#if kind === 'berdiri' || kind === 'takbir' || kind === 'iktidal'}
		<circle cx="30" cy="9" r="5.5" class="head" />
		<path d="M30 15 V38 M30 38 L26 56 M30 38 L34 56" />
		{#if kind === 'berdiri'}<path d="M30 21 L23 27 L35 27" />{/if}
		{#if kind === 'takbir'}<path d="M30 21 L23 19 L22 9 M30 21 L37 19 L38 9" />{/if}
		{#if kind === 'iktidal'}<path d="M30 21 L25 37 M30 21 L35 37" />{/if}
	{:else if kind === 'rukuk'}
		<circle cx="11" cy="33" r="5.5" class="head" />
		<path d="M17 33 H39 M39 33 L38 56 M39 33 L42 56 M24 33 L30 46" />
	{:else if kind === 'sujud'}
		<circle cx="12" cy="51" r="5.5" class="head" />
		<path d="M18 49 L38 38 M38 38 L44 54 M44 54 H56 M22 48 L16 56" />
	{:else}
		<circle cx={kind === 'salam' ? 37 : 34} cy="12" r="5.5" class="head" />
		<path d="M34 18 V42 M34 42 L20 47 L20 54 H42 M34 26 L24 44" />
	{/if}
</svg>

<style>
	.pose {
		display: block;
		flex: none;
	}
	path,
	line {
		fill: none;
		stroke: #4a2d18;
		stroke-width: 4.5;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
	.ground {
		stroke: #c9a46a;
		stroke-width: 2.5;
	}
	.head {
		fill: #4a2d18;
	}
</style>
