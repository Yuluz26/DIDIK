<!--
	Didi the mouse-deer, the same drawing as on the DIDIK site. Moods change eyes, mouth and arms only.
-->
<script lang="ts">
	let {
		mood = 'happy',
		size = 140,
		label = ''
	}: { mood?: 'happy' | 'cheer' | 'think' | 'hint' | 'wave'; size?: number; label?: string } = $props();
</script>

<svg
	class="didi didi--{mood}"
	viewBox="0 0 200 222"
	style:width="var(--didi-w, {size}px)"
	focusable="false"
	role={label ? 'img' : undefined}
	aria-label={label || undefined}
	aria-hidden={label ? undefined : 'true'}
>
	{#if mood === 'cheer'}
		<path class="arm" d="M64 174 Q30 156 36 116" />
		<path class="arm" d="M136 174 Q170 156 164 116" />
	{:else if mood === 'wave'}
		<path class="arm wave" d="M136 174 Q170 156 166 120" />
	{/if}

	<ellipse class="fur" cx="100" cy="186" rx="54" ry="34" />
	<ellipse class="belly" cx="100" cy="192" rx="24" ry="26" />
	<circle class="belly" cx="64" cy="180" r="4.5" />
	<circle class="belly" cx="136" cy="180" r="4.5" />
	<circle class="belly" cx="76" cy="170" r="3.5" />
	<circle class="belly" cx="124" cy="170" r="3.5" />
	<path class="scarf" d="M62 154 Q100 174 138 154 L142 169 Q100 190 58 169 Z" />
	<path class="scarf" d="M108 174 L126 196 L110 192 Z" />

	<g class="head" transform={mood === 'hint' ? 'rotate(-5 100 130)' : mood === 'think' ? 'rotate(4 100 130)' : undefined}>
		<g transform="rotate(26 42 82)">
			<ellipse class="fur" cx="42" cy="82" rx="28" ry="16" />
			<ellipse class="ear" cx="44" cy="82" rx="18" ry="9" />
		</g>
		<g transform="rotate(-26 158 82)">
			<ellipse class="fur" cx="158" cy="82" rx="28" ry="16" />
			<ellipse class="ear" cx="156" cy="82" rx="18" ry="9" />
		</g>
		<ellipse class="fur" cx="100" cy="96" rx="50" ry="40" />
		<ellipse class="fur" cx="100" cy="126" rx="29" ry="28" />
		<ellipse class="belly" cx="100" cy="143" rx="20" ry="11" />
		<circle class="cheek" cx="63" cy="113" r="7.5" />
		<circle class="cheek" cx="137" cy="113" r="7.5" />
		<ellipse class="ink" cx="100" cy="131" rx="7.5" ry="5.5" />

		{#if mood === 'cheer'}
			<path class="line" d="M63 98 Q74 85 85 98M115 98 Q126 85 137 98" />
			<path class="ink" d="M89 140 Q100 158 111 140 Z" />
			<ellipse class="ear" cx="100" cy="150" rx="7" ry="4" />
		{:else if mood === 'think'}
			<ellipse class="ink" cx="74" cy="96" rx="9.5" ry="11.5" />
			<ellipse class="ink" cx="126" cy="96" rx="9.5" ry="11.5" />
			<circle class="white" cx="78" cy="91" r="3.6" />
			<circle class="white" cx="130" cy="91" r="3.6" />
			<path class="line" d="M61 78 Q72 71 86 77" />
			<ellipse class="line" cx="108" cy="145" rx="3.4" ry="4.2" />
		{:else if mood === 'hint'}
			<ellipse class="ink" cx="74" cy="97" rx="9.5" ry="11.5" />
			<ellipse class="ink" cx="126" cy="97" rx="9.5" ry="11.5" />
			<circle class="white" cx="77" cy="92" r="3.5" />
			<circle class="white" cx="129" cy="92" r="3.5" />
			<path class="line" d="M62 82 L86 73M138 82 L114 73" />
			<path class="line" d="M92 145 Q100 150 108 145" />
		{:else}
			<ellipse class="ink eye" cx="74" cy="96" rx="9.5" ry="11.5" />
			<ellipse class="ink eye" cx="126" cy="96" rx="9.5" ry="11.5" />
			<circle class="white" cx="77.5" cy="91" r="3.6" />
			<circle class="white" cx="129.5" cy="91" r="3.6" />
			<circle class="white" cx="71" cy="101" r="1.8" />
			<circle class="white" cx="123" cy="101" r="1.8" />
			<path class="line" d="M91 143 Q100 152 109 143" />
		{/if}
	</g>
</svg>

<style>
	.didi {
		height: auto;
		flex: none;
		overflow: visible;
	}
	.fur {
		fill: var(--didi-fur);
	}
	.belly {
		fill: var(--didi-belly);
	}
	.ear {
		fill: var(--didi-ear);
	}
	.scarf {
		fill: var(--brand);
	}
	.ink {
		fill: var(--ink);
	}
	.white {
		fill: #fff;
	}
	.cheek {
		fill: var(--didi-ear);
		opacity: 0.75;
	}
	.line {
		fill: none;
		stroke: var(--ink);
		stroke-width: 3.5;
		stroke-linecap: round;
		stroke-linejoin: round;
	}
	.arm {
		fill: none;
		stroke: var(--didi-fur);
		stroke-width: 16;
		stroke-linecap: round;
	}
	.wave {
		transform-origin: 136px 174px;
		animation: wave 1.4s ease-in-out infinite;
	}
	.didi--cheer .head {
		transform-origin: 100px 130px;
		animation: wiggle 0.9s ease-in-out 2;
	}
	.eye {
		transform-box: fill-box;
		transform-origin: center;
		animation: blink 4.6s infinite;
	}
	@keyframes wave {
		0%,
		100% {
			transform: rotate(0);
		}
		50% {
			transform: rotate(-12deg);
		}
	}
	@keyframes blink {
		0%,
		95%,
		100% {
			transform: scaleY(1);
		}
		97% {
			transform: scaleY(0.12);
		}
	}
</style>
