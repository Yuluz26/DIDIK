<!--
	Things that stand in the worlds, drawn in a 3/4 top-down view: you see their front and their top,
	and each casts a soft shadow. The bottom centre of every drawing is its foot, so the world can sort
	props and characters by how far down the screen they stand (things lower down are in front).
	Kampung Kita's buildings are drawn by Building.
-->
<script lang="ts">
	import Building, { BUILDING_KINDS } from './Building.svelte';

	let {
		kind,
		variant = 0,
		tile = 44,
		state = '',
		progress = 0
	}: { kind: string; variant?: number; tile?: number; state?: string; progress?: number } = $props();

	// Size of each drawing in tiles (width, height) and its viewBox; the foot is at the bottom centre.
	const SIZES: Record<string, [number, number]> = {
		tree: [1.8, 2.3],
		pine: [1.4, 2.4],
		palm: [1.8, 2.5],
		bush: [1.2, 0.9],
		rock: [1.1, 0.8],
		flowers: [0.9, 0.55],
		mushroom: [0.6, 0.6],
		lamp: [0.6, 1.9],
		bench: [1.4, 0.9],
		sign: [1.1, 1.3],
		fence: [1.05, 0.8],
		chest: [0.95, 0.85],
		gate: [2.6, 2.9],
		stump: [0.9, 0.6],
		reeds: [0.8, 0.9],
		lily: [0.8, 0.4],
		hibiscus: [1.0, 0.95],
		pelita: [0.8, 1.4],
		wau: [1.3, 2.3],
		cat: [0.75, 0.7],
		hen: [0.75, 0.7],
		pot: [0.9, 1.4],
		banner: [2.4, 1.9],
		pondok: [2.4, 2.4],
		tempayan: [0.9, 0.95],
		scarecrow: [1.1, 1.9]
	};

	const size = $derived(SIZES[kind] ?? [1, 1]);
	const GREENS = [
		['#3e8e57', '#2e6e43', '#6cb33f'],
		['#4fa35b', '#3a8048', '#8fd05e'],
		['#357d4c', '#2a6440', '#5fa452']
	];
	const g = $derived(GREENS[variant % GREENS.length]);
</script>

{#snippet bloom(x: number, y: number, r: number, colour: string)}
	{#each [0, 72, 144, 216, 288] as a (a)}
		<circle cx={x + Math.sin((a * Math.PI) / 180) * r * 0.55} cy={y - Math.cos((a * Math.PI) / 180) * r * 0.55} r={r * 0.5} fill={colour} />
	{/each}
	<circle cx={x} cy={y} r={r * 0.28} fill="#ffd34d" />
{/snippet}

{#if BUILDING_KINDS.includes(kind)}
	<Building {kind} {tile} {state} {progress} />
{:else}
<svg
	class="prop prop-{kind}"
	viewBox="0 0 {size[0] * 100} {size[1] * 100}"
	width={size[0] * tile}
	height={size[1] * tile}
	aria-hidden="true"
	focusable="false"
>
	{#if kind === 'tree'}
		<ellipse cx="90" cy="222" rx="58" ry="12" fill="#000" opacity=".16" />
		<path d="M80 226 V150 h20 V226z" fill="#8e5a2e" /><path d="M91 226 V150 h9 V226z" fill="#6b4220" />
		<circle cx="90" cy="98" r="72" fill={g[1]} />
		<circle cx="58" cy="110" r="44" fill={g[0]} />
		<circle cx="120" cy="104" r="48" fill={g[0]} />
		<circle cx="90" cy="70" r="54" fill={g[0]} />
		<circle cx="72" cy="56" r="22" fill={g[2]} opacity=".7" />
		<circle cx="118" cy="82" r="13" fill={g[2]} opacity=".55" />
		{#if variant === 2}<circle cx="60" cy="118" r="7" fill="#e2483d" /><circle cx="112" cy="128" r="7" fill="#e2483d" /><circle cx="96" cy="96" r="6" fill="#e2483d" />{/if}
	{:else if kind === 'pine'}
		<ellipse cx="70" cy="232" rx="44" ry="10" fill="#000" opacity=".16" />
		<rect x="62" y="190" width="16" height="44" fill="#6b4220" />
		<path d="M70 20 L128 120 H12z" fill={g[0]} />
		<path d="M70 70 L136 176 H4z" fill={g[1]} />
		<path d="M70 120 L140 214 H0z" fill={g[0]} />
		<path d="M70 20 L88 52 H54z" fill={g[2]} opacity=".6" />
	{:else if kind === 'palm'}
		<ellipse cx="96" cy="242" rx="50" ry="10" fill="#000" opacity=".16" />
		<path d="M88 244 q-12 -80 10 -160" stroke="#8e5a2e" stroke-width="16" fill="none" stroke-linecap="round" />
		<path d="M84 220 h14 M86 190 h14 M90 160 h14 M94 130 h12" stroke="#6b4220" stroke-width="3" />
		<path d="M100 86 q-50 -26 -94 10 q46 -6 94 -10z M100 86 q-30 -60 -84 -60 q44 18 84 60z M100 86 q20 -64 76 -70 q-46 28 -76 70z M100 86 q52 -20 78 24 q-40 -20 -78 -24z M100 86 q-6 40 -50 70 q22 -36 50 -70z" fill={g[0]} />
		<circle cx="96" cy="92" r="9" fill="#8e5a2e" /><circle cx="108" cy="94" r="8" fill="#7a4a24" />
	{:else if kind === 'bush'}
		<ellipse cx="60" cy="84" rx="54" ry="8" fill="#000" opacity=".15" />
		<circle cx="38" cy="54" r="30" fill={g[1]} /><circle cx="82" cy="54" r="30" fill={g[1]} />
		<circle cx="60" cy="40" r="32" fill={g[0]} />
		<circle cx="48" cy="30" r="10" fill={g[2]} opacity=".7" />
		{#if variant % 2 === 0}<circle cx="36" cy="50" r="5" fill="#ff7aa2" /><circle cx="70" cy="36" r="5" fill="#ffd34d" /><circle cx="84" cy="58" r="5" fill="#ff7aa2" />{/if}
	{:else if kind === 'rock'}
		<ellipse cx="55" cy="72" rx="52" ry="9" fill="#000" opacity=".15" />
		<path d="M8 64 Q10 28 40 18 Q70 10 94 26 Q108 44 102 66 Q60 80 8 64z" fill="#94a3ad" />
		<path d="M14 40 Q30 18 56 16 Q84 16 96 34 Q70 44 40 44 Q24 44 14 40z" fill="#c3cdd3" />
		<path d="M60 52 l10 -6" stroke="#7d8a93" stroke-width="3" stroke-linecap="round" />
	{:else if kind === 'flowers'}
		<path d="M20 50 q4 -14 10 -18 M46 52 q0 -16 2 -22 M70 50 q-2 -14 -8 -20" stroke="#4a8424" stroke-width="3" fill="none" stroke-linecap="round" />
		<circle cx="30" cy="30" r="9" fill={variant % 2 ? '#ffd34d' : '#ff7aa2'} /><circle cx="30" cy="30" r="3.5" fill="#fff8ec" />
		<circle cx="48" cy="22" r="9" fill="#fff" /><circle cx="48" cy="22" r="3.5" fill="#ffd34d" />
		<circle cx="64" cy="30" r="9" fill={variant % 2 ? '#ff7aa2' : '#c99cff'} /><circle cx="64" cy="30" r="3.5" fill="#fff8ec" />
	{:else if kind === 'mushroom'}
		<ellipse cx="30" cy="56" rx="22" ry="4" fill="#000" opacity=".15" />
		<rect x="22" y="30" width="16" height="26" rx="6" fill="#fff4e6" />
		<path d="M4 34 a26 24 0 0 1 52 0z" fill="#e2483d" />
		<circle cx="20" cy="22" r="4" fill="#fff" /><circle cx="38" cy="16" r="3.5" fill="#fff" /><circle cx="42" cy="28" r="3" fill="#fff" />
	{:else if kind === 'lamp'}
		<ellipse cx="30" cy="186" rx="18" ry="5" fill="#000" opacity=".16" />
		<rect x="25" y="40" width="10" height="146" rx="4" fill="#3f4a5a" />
		<rect x="18" y="176" width="24" height="10" rx="4" fill="#2b2f36" />
		<path d="M14 40 h32 l-6 -22 h-20z" fill="#2b2f36" />
		<rect x="18" y="18" width="24" height="20" rx="4" fill="#ffd77a" />
		<circle cx="30" cy="28" r="24" fill="#ffe9a8" opacity=".25" />
	{:else if kind === 'bench'}
		<ellipse cx="70" cy="84" rx="62" ry="7" fill="#000" opacity=".15" />
		<rect x="14" y="56" width="10" height="28" fill="#3f4a5a" /><rect x="116" y="56" width="10" height="28" fill="#3f4a5a" />
		<rect x="6" y="46" width="128" height="14" rx="4" fill="#c98a54" />
		<rect x="6" y="20" width="128" height="10" rx="4" fill="#d99a5b" /><rect x="6" y="33" width="128" height="10" rx="4" fill="#c98a54" />
	{:else if kind === 'sign'}
		<ellipse cx="55" cy="124" rx="24" ry="5" fill="#000" opacity=".15" />
		<rect x="49" y="40" width="12" height="86" fill="#8e5a2e" />
		<path d="M10 22 h80 l14 18 -14 18 h-80z" fill="#d99a5b" stroke="#8e5a2e" stroke-width="4" />
		<path d="M24 40 h50 m-12 -9 l12 9 -12 9" stroke="#6b4220" stroke-width="6" fill="none" stroke-linecap="round" stroke-linejoin="round" />
	{:else if kind === 'fence'}
		<rect x="6" y="24" width="12" height="56" rx="3" fill="#a46a37" /><rect x="88" y="24" width="12" height="56" rx="3" fill="#a46a37" />
		<rect x="0" y="34" width="105" height="10" rx="3" fill="#c98a54" /><rect x="0" y="56" width="105" height="10" rx="3" fill="#c98a54" />
	{:else if kind === 'stump'}
		<ellipse cx="45" cy="56" rx="40" ry="6" fill="#000" opacity=".15" />
		<path d="M12 22 v28 q33 12 66 0 v-28z" fill="#8e5a2e" />
		<ellipse cx="45" cy="22" rx="33" ry="12" fill="#d9a066" /><ellipse cx="45" cy="22" rx="20" ry="7" fill="none" stroke="#b97842" stroke-width="2.5" />
	{:else if kind === 'reeds'}
		<path d="M22 90 q-4 -40 -10 -66 M40 90 q0 -50 4 -82 M58 90 q4 -40 14 -60" stroke="#4a8424" stroke-width="5" fill="none" stroke-linecap="round" />
		<rect x="38" y="14" width="10" height="24" rx="5" fill="#8e5a2e" />
	{:else if kind === 'lily'}
		<path d="M40 20 m-36 0 a36 16 0 1 0 72 0 a36 16 0 1 0 -72 0z M40 20 l30 -6 -2 10z" fill="#6cb33f" />
		<circle cx="52" cy="16" r="6" fill="#ff9ec4" />
	{:else if kind === 'chest'}
		<ellipse cx="47" cy="80" rx="42" ry="7" fill="#000" opacity=".18" />
		{#if state === 'open'}
			<rect x="10" y="40" width="74" height="40" rx="6" fill="#a8432f" />
			<path d="M10 40 L20 6 H74 L84 40z" fill="#c9572e" />
			<path d="M22 40 L28 18 H66 L72 40z" fill="#5a2a1d" />
			<circle cx="47" cy="32" r="7" fill="#ffd34d" />
		{:else}
			<rect x="10" y="36" width="74" height="44" rx="6" fill={state === 'locked' ? '#94a3ad' : '#a8432f'} />
			<path d="M10 40 Q47 0 84 40z" fill={state === 'locked' ? '#b8c4cb' : '#c9572e'} />
			<rect x="10" y="36" width="74" height="8" fill={state === 'locked' ? '#7d8a93' : '#7a2f1f'} />
			<rect x="40" y="40" width="14" height="18" rx="3" fill="#ffd34d" />
			<rect x="24" y="44" width="5" height="34" fill="#00000022" /><rect x="65" y="44" width="5" height="34" fill="#00000022" />
		{/if}
	{:else if kind === 'gate'}
		<ellipse cx="130" cy="282" rx="120" ry="10" fill="#000" opacity=".16" />
		<rect x="22" y="40" width="26" height="248" rx="6" fill="#8e5a2e" /><rect x="212" y="40" width="26" height="248" rx="6" fill="#8e5a2e" />
		<rect x="4" y="22" width="252" height="34" rx="10" fill="#a8432f" />
		<rect x="30" y="64" width="200" height="14" rx="4" fill="#8e5a2e" />
		<rect x="88" y="2" width="84" height="34" rx="8" fill="#fff4e6" stroke="#8e5a2e" stroke-width="4" />
		<text x="130" y="27" text-anchor="middle" font-family="Fredoka Variable, sans-serif" font-size="20" font-weight="600" fill="#6b4220">KELUAR</text>
		{#if state === 'open'}
			<path d="M48 88 l-30 18 v170 l30 -14z M212 88 l30 18 v170 l-30 -14z" fill="#c98a54" />
			<rect x="48" y="88" width="164" height="198" fill="#bfe8a5" opacity=".55" />
		{:else}
			<rect x="48" y="88" width="164" height="198" fill="#c98a54" />
			<path d="M48 130 h164 M48 180 h164 M48 230 h164 M130 88 v198" stroke="#a46a37" stroke-width="4" />
			<rect x="114" y="166" width="32" height="28" rx="5" fill="#ffd34d" />
			<path d="M120 166 v-8 a10 10 0 0 1 20 0 v8" stroke="#ffd34d" stroke-width="5" fill="none" />
		{/if}
	{:else if kind === 'hibiscus'}
		<!-- Bunga raya: a low bush with big red flowers. -->
		<ellipse cx="50" cy="88" rx="44" ry="7" fill="#000" opacity=".15" />
		<circle cx="28" cy="60" r="26" fill={g[1]} /><circle cx="72" cy="60" r="26" fill={g[1]} />
		<circle cx="50" cy="44" r="30" fill={g[0]} />
		<circle cx="40" cy="30" r="9" fill={g[2]} opacity=".7" />
		{@render bloom(30, 52, 22, '#e2483d')}
		{@render bloom(66, 40, 24, '#e2483d')}
		{@render bloom(58, 70, 16, '#f0605a')}
	{:else if kind === 'pelita'}
		<!-- Three oil lamps on bamboo poles, as in the last nights of Ramadan. -->
		<ellipse cx="40" cy="134" rx="32" ry="5" fill="#000" opacity=".15" />
		{#each [[16, 54], [40, 30], [64, 62]] as [x, top] (x)}
			<rect x={x - 3.5} y={top} width="7" height={136 - top} rx="2" fill="#c2a24a" />
			<path d="M{x - 3.5} {top + 30} h7 M{x - 3.5} {top + 64} h7" stroke="#8f7a2e" stroke-width="2.5" />
			<circle cx={x} cy={top - 10} r="13" fill="#ffe9a8" opacity=".35" />
			<rect x={x - 6} y={top - 6} width="12" height="9" rx="2" fill="#8e9aa5" />
			<path class="flame" d="M{x} {top - 22} q7 9 0 16 q-7 -7 0 -16z" fill="#ffb627" style:transform-origin="{x}px {top - 6}px" />
			<path d="M{x} {top - 14} q3 4 0 8 q-3 -4 0 -8z" fill="#fff3b0" />
		{/each}
	{:else if kind === 'wau'}
		<!-- A wau bulan flying on its string, tied to a peg in the ground. -->
		<ellipse cx="65" cy="226" rx="10" ry="3" fill="#000" opacity=".15" />
		<rect x="61" y="210" width="8" height="18" rx="2" fill="#8e5a2e" />
		<path d="M65 212 Q50 160 66 104" stroke="#fff" stroke-width="1.6" fill="none" opacity=".9" />
		<g class="kite">
			<path d="M65 22 C59 36 59 74 65 104 C71 74 71 36 65 22z" fill="#ffd34d" />
			<path d="M65 44 C46 38 18 40 8 62 C28 54 48 56 65 62 C82 56 102 54 122 62 C112 40 84 38 65 44z" fill="#e2483d" />
			<path d="M28 96 C38 122 92 122 102 96 C88 110 42 110 28 96z" fill="#2f7fcf" />
			<path d="M65 98 v8" stroke="#ffd34d" stroke-width="4" />
			<path d="M30 56 q35 -10 70 0" stroke="#fff" stroke-width="2.5" fill="none" opacity=".8" />
			<circle cx="65" cy="30" r="5" fill="#2f7fcf" />
		</g>
	{:else if kind === 'cat'}
		<!-- Kucing oren, sitting and swishing its tail. -->
		<ellipse cx="37" cy="64" rx="26" ry="5" fill="#000" opacity=".15" />
		<path class="tail" d="M52 58 q16 -2 15 -20 q-1 -6 -5 -4" stroke="#e08a3a" stroke-width="6" fill="none" stroke-linecap="round" />
		<ellipse cx="36" cy="50" rx="18" ry="15" fill="#f29c4b" />
		<ellipse cx="36" cy="54" rx="10" ry="9" fill="#fde7c8" />
		<path d="M23 23 l2 -16 l11 10z M49 23 l-2 -16 l-11 10z" fill="#f29c4b" />
		<path d="M26 19 l1 -7 l5 5z M46 19 l-1 -7 l-5 5z" fill="#f7b7b2" />
		<circle cx="36" cy="29" r="15" fill="#f29c4b" />
		<path d="M36 15 v6 M30 16 l1 5 M42 16 l-1 5" stroke="#d9762a" stroke-width="2.4" stroke-linecap="round" />
		<ellipse cx="30.5" cy="30" rx="2" ry="2.6" fill="#2a2433" /><ellipse cx="41.5" cy="30" rx="2" ry="2.6" fill="#2a2433" />
		<path d="M34.5 34.5 h3 l-1.5 2z" fill="#e8798a" />
		<ellipse cx="29" cy="63" rx="5" ry="3" fill="#fde7c8" /><ellipse cx="43" cy="63" rx="5" ry="3" fill="#fde7c8" />
	{:else if kind === 'banner'}
		<!-- A cloth banner on two poles; `state` is its word. The finish banner (variant 0) is chequered. -->
		<ellipse cx="120" cy="186" rx="108" ry="5" fill="#000" opacity=".14" />
		<rect x="16" y="30" width="9" height="158" rx="3" fill="#8e5a2e" /><rect x="215" y="30" width="9" height="158" rx="3" fill="#8e5a2e" />
		<circle cx="20.5" cy="28" r="7" fill="#ffd34d" /><circle cx="219.5" cy="28" r="7" fill="#ffd34d" />
		{#if variant === 0}
			<rect x="25" y="38" width="190" height="62" fill="#fff" />
			{#each Array.from({ length: 19 }, (_, i) => i) as i (i)}
				<rect x={25 + i * 10} y={i % 2 ? 38 : 48} width="10" height="10" fill="#1f2d27" />
				<rect x={25 + i * 10} y={i % 2 ? 90 : 80} width="10" height="10" fill="#1f2d27" />
			{/each}
			<text x="120" y="77" text-anchor="middle" font-family="Fredoka Variable, sans-serif" font-size="24" font-weight="600" fill="#e2483d">{state}</text>
		{:else}
			<rect x="25" y="40" width="190" height="56" rx="6" fill="#1f9d55" />
			<text x="120" y="77" text-anchor="middle" font-family="Fredoka Variable, sans-serif" font-size="26" font-weight="600" fill="#fff">{state}</text>
		{/if}
	{:else if kind === 'pot'}
		<!-- A leafy plant in a clay pot, for indoor places. -->
		<ellipse cx="45" cy="134" rx="30" ry="5" fill="#000" opacity=".15" />
		<path d="M45 96 q-30 -20 -36 -60 q24 14 36 50 M45 96 q30 -24 34 -66 q-22 18 -34 56 M45 96 q-6 -40 6 -82 q10 40 -6 82" fill="#3e8e57" />
		<path d="M45 92 q-14 -26 -16 -46" stroke="#2e6e43" stroke-width="3" fill="none" />
		<path d="M20 96 h50 l-6 38 h-38z" fill="#c9572e" />
		<rect x="16" y="92" width="58" height="10" rx="3" fill="#a8432f" />
	{:else if kind === 'pondok'}
		<!-- A small hut on stilts with a thatched attap roof. -->
		<ellipse cx="120" cy="230" rx="104" ry="9" fill="#000" opacity=".15" />
		<rect x="48" y="170" width="10" height="60" fill="#8e5a2e" /><rect x="182" y="170" width="10" height="60" fill="#8e5a2e" />
		<path d="M104 176 L94 230 M136 176 L146 230 M98 196 H142 M96 214 H144" stroke="#8e5a2e" stroke-width="5" />
		<rect x="36" y="162" width="168" height="14" rx="3" fill="#a46a37" />
		<rect x="50" y="104" width="140" height="60" fill="#d9a066" />
		<path d="M50 124 H190 M50 144 H190" stroke="#c48a52" stroke-width="4" />
		<rect x="100" y="116" width="40" height="48" rx="3" fill="#6b4220" />
		<path d="M22 114 L120 34 L218 114z" fill="#b8894a" />
		<path d="M120 34 L218 114 L190 114 L120 56z" fill="#9a7038" />
		<path d="M40 104 l-4 12 M64 84 l-4 12 M88 64 l-4 12 M152 64 l4 12 M176 84 l4 12 M200 104 l4 12" stroke="#8a6230" stroke-width="4" stroke-linecap="round" />
	{:else if kind === 'tempayan'}
		<!-- A clay water jar. -->
		<ellipse cx="45" cy="88" rx="34" ry="6" fill="#000" opacity=".15" />
		<path d="M20 30 q-16 22 -3 46 q8 12 28 12 q20 0 28 -12 q13 -24 -3 -46z" fill="#b5651d" />
		<path d="M24 42 q-6 14 0 28" stroke="#d98b4a" stroke-width="5" fill="none" stroke-linecap="round" />
		<ellipse cx="45" cy="28" rx="25" ry="8" fill="#9a531a" />
		<ellipse cx="45" cy="28" rx="18" ry="5" fill="#4fc3f7" />
	{:else if kind === 'scarecrow'}
		<!-- An orang-orang in a terendak hat, keeping birds off the crops. -->
		<ellipse cx="55" cy="184" rx="22" ry="5" fill="#000" opacity=".15" />
		<rect x="52" y="60" width="6" height="126" fill="#8e5a2e" />
		<rect x="12" y="80" width="86" height="6" rx="3" fill="#8e5a2e" />
		<path d="M14 78 l-8 -4 M14 88 l-8 4 M96 78 l8 -4 M96 88 l8 4" stroke="#e8c06a" stroke-width="3" stroke-linecap="round" />
		<path d="M18 76 H92 V92 H76 L72 130 H38 L34 92 H18z" fill="#2f7fcf" />
		<rect x="44" y="100" width="14" height="12" fill="#ffd34d" />
		<circle cx="55" cy="56" r="16" fill="#f0d9a6" />
		<path d="M48 54 l4 4 M52 54 l-4 4 M58 54 l4 4 M62 54 l-4 4 M49 64 q6 4 12 0" stroke="#8e5a2e" stroke-width="2.2" fill="none" stroke-linecap="round" />
		<path d="M20 46 L55 20 L90 46z" fill="#e8c06a" />
		<path d="M20 46 H90" stroke="#c9a24a" stroke-width="4" stroke-linecap="round" />
	{:else if kind === 'hen'}
		<!-- Ayam kampung, pecking now and then. -->
		<ellipse cx="37" cy="64" rx="24" ry="5" fill="#000" opacity=".15" />
		<path d="M32 52 v11 M42 52 v11 M29 63 h6 M39 63 h6" stroke="#e8a800" stroke-width="2.6" stroke-linecap="round" />
		<path d="M14 34 q-8 -12 2 -20 q2 10 8 14 q-4 -14 6 -18 q0 12 4 16z" fill="#3d2b22" />
		<path d="M10 22 q4 -6 8 -2" stroke="#2e6e43" stroke-width="3" fill="none" stroke-linecap="round" />
		<ellipse cx="34" cy="42" rx="22" ry="14" fill="#d9893f" />
		<path d="M22 40 q12 -6 22 4 q-10 8 -22 -4z" fill="#a8562b" />
		<g class="head">
			<circle cx="54" cy="28" r="10" fill="#d9893f" />
			<path d="M48 19 q2 -7 6 -3 q2 -6 6 -1 q3 -4 4 3 z" fill="#e2483d" />
			<path d="M63 27 l8 3 -8 3z" fill="#f2b33d" />
			<path d="M60 35 q2 6 -2 7 q-3 -3 0 -7z" fill="#e2483d" />
			<circle cx="56" cy="26" r="1.8" fill="#2a2433" />
		</g>
	{/if}
</svg>
{/if}

<style>
	.prop {
		display: block;
		overflow: visible;
	}
	.flame {
		animation: flicker 900ms ease-in-out infinite alternate;
	}
	.kite {
		transform-origin: 65px 104px;
		animation: sway 3.2s ease-in-out infinite alternate;
	}
	.tail {
		transform-origin: 52px 58px;
		animation: sway 1.6s ease-in-out infinite alternate;
	}
	.prop-hen .head {
		transform-origin: 46px 40px;
		animation: peck 4.5s ease-in-out infinite;
	}
	@keyframes flicker {
		to {
			transform: scale(0.82, 0.9);
		}
	}
	@keyframes sway {
		from {
			transform: rotate(-5deg);
		}
		to {
			transform: rotate(5deg);
		}
	}
	@keyframes peck {
		0%,
		70%,
		100% {
			transform: none;
		}
		78%,
		88% {
			transform: rotate(32deg);
		}
	}
</style>
