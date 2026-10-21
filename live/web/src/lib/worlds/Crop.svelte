<!--
	One crop of Kebun Ajaib, drawn upward from its base point (x, y) inside an existing SVG. `grow`
	runs from 0 (just planted) to 1 (fully grown); fruit and flowers appear only when `ready`.
-->
<svelte:options namespace="svg" />

<script lang="ts">
	let {
		crop,
		x = 0,
		y = 0,
		grow = 1,
		ready = false,
		scale = 1
	}: { crop: string; x?: number; y?: number; grow?: number; ready?: boolean; scale?: number } = $props();

	// A young plant is a smaller copy of the grown one; a fresh seed is just a sprout.
	const size = $derived(scale * (ready ? 1 : 0.55 + 0.35 * Math.max(0, Math.min(1, grow))));

	function star(cx: number, cy: number, points: number, outer: number, inner: number): string {
		return Array.from({ length: points * 2 }, (_, i) => {
			const r = i % 2 ? inner : outer;
			const a = (Math.PI * i) / points;
			return `${(cx + r * Math.sin(a)).toFixed(1)},${(cy - r * Math.cos(a)).toFixed(1)}`;
		}).join(' ');
	}
</script>

{#snippet leaf(lx: number, ly: number, angle: number, length: number, fill: string)}
	<ellipse cx={lx} cy={ly} rx={length / 2} ry={length / 5.5} {fill} transform="rotate({angle} {lx} {ly})" />
{/snippet}

{#snippet bloom(bx: number, by: number, r: number, fill: string)}
	{#each [0, 72, 144, 216, 288] as a (a)}
		<circle cx={bx + Math.sin((a * Math.PI) / 180) * r * 0.55} cy={by - Math.cos((a * Math.PI) / 180) * r * 0.55} r={r * 0.5} {fill} />
	{/each}
	<circle cx={bx} cy={by} r={r * 0.26} fill="#ffd34d" />
{/snippet}

<g transform="translate({x} {y}) scale({size})">
	{#if grow <= 0 && !ready}
		<ellipse cx="0" cy="0" rx="16" ry="5" fill="#6f4326" />
		<path d="M0 0 v-14" stroke="#4a8424" stroke-width="4" stroke-linecap="round" />
		{@render leaf(-7, -16, -30, 16, '#6cb33f')}
		{@render leaf(7, -18, 30, 16, '#8fd05e')}
	{:else if crop === 'bunga'}
		<path d="M0 0 V-62" stroke="#4a8424" stroke-width="5" stroke-linecap="round" />
		{@render leaf(-16, -22, -25, 34, '#4fa35b')}
		{@render leaf(16, -30, 25, 34, '#3e8e57')}
		{@render leaf(-14, -48, -35, 28, '#6cb33f')}
		{@render leaf(14, -56, 35, 26, '#4fa35b')}
		{#if ready}
			{@render bloom(0, -72, 26, '#e2483d')}
			{@render bloom(-22, -40, 18, '#f0605a')}
		{:else}
			<ellipse cx="0" cy="-70" rx="7" ry="11" fill="#6cb33f" />
		{/if}
	{:else if crop === 'cili'}
		<path d="M0 0 V-58 M0 -30 l-18 -16 M0 -40 l18 -14" stroke="#4a8424" stroke-width="5" stroke-linecap="round" fill="none" />
		{@render leaf(-22, -50, -20, 30, '#3e8e57')}
		{@render leaf(22, -58, 20, 30, '#4fa35b')}
		{@render leaf(-10, -66, -60, 26, '#6cb33f')}
		{@render leaf(12, -24, 30, 26, '#3e8e57')}
		{#if ready}
			{#each [[-18, -44, 18], [16, -50, -14], [4, -30, 8], [-6, -56, -6]] as [cx, cy, tilt] (`${cx}`)}
				<path d="M{cx} {cy} q5 2 3 14 q-2 12 -6 16 q-1 -14 3 -30z" fill="#e2483d" transform="rotate({tilt} {cx} {cy})" />
				<path d="M{cx - 2} {cy - 1} h6" stroke="#2e6e43" stroke-width="3" stroke-linecap="round" />
			{/each}
		{/if}
	{:else if crop === 'jagung'}
		<path d="M0 0 V-118" stroke="#6cb33f" stroke-width="7" stroke-linecap="round" />
		<path d="M0 -20 q-30 -4 -40 -34 q18 14 40 18z M0 -46 q30 -6 40 -38 q-16 18 -40 22z M0 -74 q-26 -8 -32 -36 q14 16 32 20z" fill="#4fa35b" />
		<path d="M0 -118 l-8 -14 M0 -118 l8 -15 M0 -118 v-16" stroke="#e8c06a" stroke-width="3.5" stroke-linecap="round" />
		{#if ready}
			<ellipse cx="9" cy="-62" rx="9" ry="19" fill="#ffd34d" transform="rotate(14 9 -62)" />
			<path d="M3 -46 q-2 -20 10 -34 q-2 16 6 30z" fill="#8fd05e" />
			<ellipse cx="-9" cy="-86" rx="7" ry="15" fill="#ffd34d" transform="rotate(-14 -9 -86)" />
		{/if}
	{:else if crop === 'tembikai'}
		<path d="M-60 -4 q20 -20 40 -6 q16 10 34 -4 q18 -14 44 4" stroke="#4a8424" stroke-width="4" fill="none" stroke-linecap="round" />
		{@render leaf(-46, -14, -20, 30, '#4fa35b')}
		{@render leaf(40, -16, 25, 30, '#3e8e57')}
		{@render leaf(-8, -22, 0, 26, '#6cb33f')}
		{#if ready}
			<ellipse cx="2" cy="-26" rx="50" ry="32" fill="#2e7d4f" />
			<path d="M-34 -48 q-10 22 0 44 M-14 -56 q-8 30 0 60 M8 -58 q-6 32 0 62 M30 -52 q8 26 0 50" stroke="#8fd05e" stroke-width="5" fill="none" stroke-linecap="round" />
			<ellipse cx="-16" cy="-44" rx="12" ry="5" fill="#fff" opacity=".35" />
		{:else}
			<circle cx="0" cy="-12" r="11" fill="#6cb33f" />
		{/if}
	{:else if crop === 'durian'}
		<path d="M0 0 V-62" stroke="#8e5a2e" stroke-width="10" stroke-linecap="round" />
		<path d="M0 -40 l-22 -18 M0 -46 l20 -20" stroke="#8e5a2e" stroke-width="6" stroke-linecap="round" />
		<circle cx="0" cy="-92" r="38" fill="#2e6e43" />
		<circle cx="-28" cy="-70" r="26" fill="#3e8e57" />
		<circle cx="28" cy="-72" r="27" fill="#3e8e57" />
		<circle cx="0" cy="-104" r="26" fill="#4fa35b" />
		<circle cx="-10" cy="-112" r="9" fill="#6cb33f" opacity=".7" />
		{#if ready}
			{#each [[-24, -52], [20, -56], [0, -66]] as [cx, cy] (`${cx}`)}
				<polygon points={star(cx, cy, 12, 13, 10.5)} fill="#b5c23a" stroke="#8a9a28" stroke-width="2" stroke-linejoin="round" />
				<path d="M{cx} {cy - 13} v-6" stroke="#8e5a2e" stroke-width="3" />
			{/each}
		{/if}
	{/if}
</g>
