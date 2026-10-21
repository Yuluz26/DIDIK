<!--
	Kampung Kita's buildings in the same 3/4 view as the other props: front wall, roof seen from above
	and in front, a shadow on the grass. The foot (bottom centre) is the middle of the building's front
	edge.

	A building under construction rises from the ground as material arrives: the finished building
	stands faintly behind the scaffolding, and the built part fills in from the bottom up.
-->
<script lang="ts" module>
	export const BUILDING_KINDS = ['rumah', 'kedai', 'sekolah', 'jeti', 'masjid', 'rumahpanjang', 'balai'];
</script>

<script lang="ts">
	let {
		kind,
		tile = 44,
		state = 'done',
		progress = 0
	}: { kind: string; tile?: number; state?: string; progress?: number } = $props();

	const W = 3.2;
	const H = 3.2;
	const clip = `rise-${Math.random().toString(36).slice(2, 8)}`;
	// The line the walls have reached, from the ground (y 300) up to above the roof (y 20).
	const line = $derived(300 - Math.max(0, Math.min(1, progress)) * 280);
</script>

{#snippet art()}
	{#if kind === 'rumah'}
		<rect x="70" y="244" width="12" height="60" fill="#8e5a2e" /><rect x="238" y="244" width="12" height="60" fill="#8e5a2e" /><rect x="154" y="244" width="12" height="60" fill="#8e5a2e" />
		<rect x="56" y="150" width="208" height="100" rx="6" fill="#d9a066" />
		<path d="M56 186 H264 M56 220 H264" stroke="#c48a52" stroke-width="5" />
		<rect x="80" y="176" width="40" height="44" rx="4" fill="#4b6c7a" /><rect x="200" y="176" width="40" height="44" rx="4" fill="#4b6c7a" />
		<rect x="140" y="170" width="40" height="80" rx="4" fill="#8e5a2e" />
		<path d="M146 250 L132 304 M174 250 L188 304 M140 266 H180 M136 284 H184" stroke="#8e5a2e" stroke-width="6" />
		<path d="M30 160 L160 50 L290 160z" fill="#c0503a" />
		<path d="M160 50 L290 160 L262 160 L160 72z" fill="#a8432f" />
		<path d="M130 120 L160 96 L190 120 V136 H130z" fill="#f4d7a1" />
	{:else if kind === 'kedai'}
		<rect x="50" y="130" width="220" height="170" rx="6" fill="#fff4e6" />
		<rect x="50" y="110" width="220" height="30" rx="6" fill="#2e7d4f" />
		<text x="160" y="132" text-anchor="middle" font-family="Fredoka Variable, sans-serif" font-size="22" font-weight="600" fill="#fff">KEDAI RUNCIT</text>
		{#each [0, 1, 2, 3, 4, 5, 6] as i (i)}<path d="M{50 + i * 31.4} 140 h31.4 v26 q-15.7 12 -31.4 0z" fill={i % 2 ? '#fff' : '#3daa5c'} />{/each}
		<rect x="70" y="190" width="70" height="80" rx="4" fill="#cdebff" stroke="#8e5a2e" stroke-width="5" />
		<rect x="180" y="190" width="60" height="110" rx="4" fill="#8e5a2e" />
		<circle cx="84" cy="300" r="10" fill="#f28c28" /><circle cx="104" cy="302" r="9" fill="#ffd34d" /><rect x="66" y="288" width="60" height="14" rx="4" fill="#c98a54" />
	{:else if kind === 'sekolah'}
		<rect x="20" y="150" width="280" height="150" rx="6" fill="#f6e3b4" />
		<path d="M10 160 L40 100 H280 L310 160z" fill="#2f7fcf" />
		<path d="M40 100 H280 L292 124 H28z" fill="#1d5a99" />
		{#each [0, 1, 2, 3] as i (i)}<rect x={40 + i * 66} y="180" width="44" height="40" rx="4" fill="#4b6c7a" />{/each}
		<rect x="136" y="236" width="48" height="64" rx="4" fill="#8e5a2e" />
		<rect x="258" y="20" width="6" height="140" fill="#94a3ad" />
		<rect x="264" y="22" width="44" height="28" fill="#e2483d" />
		<path d="M264 26 h44 M264 34 h44 M264 42 h44" stroke="#fff" stroke-width="3" />
		<rect x="264" y="22" width="20" height="16" fill="#1d3a8f" />
		<circle cx="274" cy="30" r="4" fill="#ffd34d" />
	{:else if kind === 'jeti'}
		<rect x="20" y="230" width="280" height="80" rx="18" fill="#3ba7d9" />
		<path d="M40 250 q12 -6 24 0 M220 290 q12 -6 24 0" stroke="#9fd8f0" stroke-width="5" fill="none" stroke-linecap="round" />
		<rect x="40" y="200" width="240" height="36" rx="4" fill="#c98a54" />
		<path d="M70 200 v36 M110 200 v36 M150 200 v36 M190 200 v36 M230 200 v36" stroke="#a46a37" stroke-width="4" />
		<rect x="50" y="236" width="12" height="50" fill="#8e5a2e" /><rect x="258" y="236" width="12" height="50" fill="#8e5a2e" />
		<path d="M150 270 H250 Q244 296 222 296 H176 Q156 296 150 270z" fill="#e2483d" />
		<rect x="194" y="214" width="6" height="58" fill="#8e5a2e" /><path d="M200 214 L240 254 H200z" fill="#fff8ec" />
		<rect x="60" y="120" width="70" height="80" rx="4" fill="#d9a066" /><path d="M50 124 L95 84 L140 124z" fill="#a8432f" />
	{:else if kind === 'masjid'}
		<rect x="60" y="170" width="200" height="130" rx="6" fill="#ffffff" />
		<rect x="60" y="170" width="200" height="16" fill="#e8e2d6" />
		<path d="M100 170 q60 -110 120 0z" fill="#1f9d55" />
		<path d="M160 60 v-18 M152 48 a8 8 0 1 0 16 0" stroke="#e8a800" stroke-width="5" fill="none" />
		<rect x="262" y="70" width="28" height="230" rx="4" fill="#ffffff" />
		<path d="M258 74 L276 30 L294 74z" fill="#1f9d55" />
		<rect x="262" y="120" width="28" height="8" fill="#1f9d55" />
		<path d="M140 300 v-56 a20 20 0 0 1 40 0 v56z" fill="#8e5a2e" />
		{#each [0, 1] as i (i)}<path d="M{84 + i * 120} 260 v-34 a12 12 0 0 1 24 0 v34z" fill="#4b6c7a" />{/each}
	{:else if kind === 'rumahpanjang'}
		{#each [0, 1, 2, 3, 4, 5] as i (i)}<rect x={22 + i * 54} y="236" width="10" height="68" fill="#8e5a2e" />{/each}
		<rect x="12" y="160" width="296" height="80" rx="4" fill="#c98a54" />
		<path d="M12 186 H308 M12 214 H308" stroke="#a46a37" stroke-width="4" />
		{#each [0, 1, 2, 3, 4] as i (i)}<rect x={30 + i * 58} y="176" width="26" height="50" rx="3" fill="#6b4220" />{/each}
		<path d="M0 170 L40 110 H280 L320 170z" fill="#8e5a2e" />
		<path d="M40 110 H280 L292 128 H28z" fill="#6b4220" />
		<path d="M20 120 l-14 -26 M300 120 l14 -26" stroke="#8e5a2e" stroke-width="8" stroke-linecap="round" />
		<path d="M150 240 L140 304 M170 240 L180 304 M144 262 H176 M142 284 H178" stroke="#8e5a2e" stroke-width="6" />
	{:else if kind === 'balai'}
		<rect x="40" y="160" width="240" height="140" rx="6" fill="#fff4e6" />
		<path d="M20 170 L160 70 L300 170z" fill="#f28c28" />
		<path d="M160 70 L300 170 L270 170 L160 92z" fill="#d9761a" />
		<rect x="90" y="128" width="140" height="32" rx="6" fill="#1c6b4a" />
		<text x="160" y="151" text-anchor="middle" font-family="Fredoka Variable, sans-serif" font-size="20" font-weight="600" fill="#fff">BALAI RAYA</text>
		{#each [0, 1, 2, 3] as i (i)}<rect x={56 + i * 60} y="180" width="12" height="120" fill="#e8d4b0" />{/each}
		<rect x="128" y="220" width="64" height="80" rx="4" fill="#8e5a2e" />
	{/if}
{/snippet}

<svg class="building {state}" viewBox="0 0 320 320" width={W * tile} height={H * tile} aria-hidden="true" focusable="false">
	<ellipse cx="160" cy="306" rx="150" ry="14" fill="#000" opacity=".15" />
	{#if state === 'plot'}
		<rect x="40" y="200" width="240" height="100" rx="14" fill="#fff" opacity=".18" />
		<rect x="40" y="200" width="240" height="100" rx="14" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="14 10" opacity=".85" />
		<rect x="132" y="236" width="56" height="34" rx="6" fill="#d99a5b" />
		<rect x="156" y="270" width="8" height="34" fill="#8e5a2e" />
	{:else if state === 'building'}
		<rect x="30" y="288" width="260" height="16" rx="4" fill="#c3cdd3" />
		<g opacity=".22">{@render art()}</g>
		<defs>
			<clipPath id={clip}><rect class="rise" x="0" y={line} style:y="{line}px" width="320" height="320" /></clipPath>
		</defs>
		<g clip-path="url(#{clip})">{@render art()}</g>
		<!-- Scaffolding: two poles up to the line the walls have reached, and a plank across it. -->
		<rect class="rise" x="26" style:y="{line - 24}px" style:height="{324 - line}px" width="10" fill="#a46a37" />
		<rect class="rise" x="284" style:y="{line - 24}px" style:height="{324 - line}px" width="10" fill="#a46a37" />
		<rect class="rise" x="18" style:y="{line - 30}px" width="284" height="12" rx="4" fill="#d99a5b" />
		<!-- Material waiting at the site. -->
		<rect x="236" y="282" width="56" height="10" rx="2" fill="#c98a54" /><rect x="242" y="272" width="44" height="10" rx="2" fill="#d99a5b" />
		<rect x="28" y="280" width="18" height="12" rx="2" fill="#c0503a" /><rect x="48" y="280" width="18" height="12" rx="2" fill="#c0503a" /><rect x="38" y="268" width="18" height="12" rx="2" fill="#a8432f" />
	{:else}
		{@render art()}
	{/if}
</svg>

<style>
	.building {
		display: block;
		overflow: visible;
	}
	.rise {
		transition:
			y 700ms var(--ease-out),
			height 700ms var(--ease-out);
	}
	.done {
		transform-origin: 50% 96%;
		animation: stand-up 700ms var(--spring);
	}
	@keyframes stand-up {
		from {
			transform: scale(0.94, 0.9);
		}
	}
</style>
