<!--
	Litar Elektrik: a real series circuit on a workbench mat. A battery, a bulb, a knife switch and a gap
	between two crocodile clips are joined in one loop by wires. Clip one thing from the tray into the
	gap (drag it there, or tap it), then close the switch.

	What happens then is physics, not a reward: the bulb lights only if the thing in the gap lets a
	current through (the lexicon knows that an iron key conducts and a rubber eraser does not), so a wrong
	choice shows a dark bulb and why. Nothing happens before the switch is closed, which is also when the
	answer is sent, so the bulb never gives an answer away. The server gives this game only to questions
	whose answers are all things whose conductivity is known.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import { dragTap } from '$lib/questions/drag';
	import Sticker from '$ui/Sticker.svelte';
	import Checks from '../Checks.svelte';
	import GameImage from '../GameImage.svelte';
	import Mark from '../Mark.svelte';
	import { find, type Entry } from '../assets';
	import { type GameProps, isLocked, stickerFor } from '../kit.svelte';

	let p: GameProps = $props();

	interface Material extends Entry {
		conducts: boolean | null;
	}
	const choices = $derived(p.question.choices ?? []);
	const locked = $derived(isLocked(p));
	let chosen = $state<string | null>(null);
	const pick = $derived<string | null>(p.mine !== undefined ? p.mine : p.reveal ? p.reveal.correct[0] : chosen);
	const right = $derived<string | null>(p.reveal ? p.reveal.correct[0] : null);
	const inGap = $derived(choices.find((c) => c.id === pick));
	const material = $derived(inGap ? find<Material>('materials', inGap.text) : undefined);
	// The switch is closed once the answer is in (or shown). The loop is complete only through a conductor.
	// Something the lexicon does not know cannot be simulated: then the bulb follows the answer, once shown.
	const closed = $derived(locked && !!inGap);
	const flows = $derived(closed && (material?.conducts != null ? material.conducts : !!right && pick === right));
	const known = $derived(material?.conducts != null);

	function put(id: string) {
		if (locked) return;
		chosen = id;
		play('pop');
	}
</script>

<div class="bench">
	<div class="board" class:flows class:closed>
		<svg viewBox="0 0 320 232" class="wires" aria-hidden="true">
			<defs>
				<linearGradient id="lt-brass" x1="0" x2="1">
					<stop offset="0" stop-color="#7a5a18" /><stop offset="0.4" stop-color="#f3d27a" /><stop offset="1" stop-color="#8a6418" />
				</linearGradient>
				<linearGradient id="lt-steel" x1="0" x2="0" y2="1">
					<stop offset="0" stop-color="#f4f6f9" /><stop offset="0.5" stop-color="#aab2c0" /><stop offset="1" stop-color="#6b7383" />
				</linearGradient>
			</defs>
			<!-- the wires, as one loop: battery, up and across to the bulb, across and down to the switch, down and back along the bottom through the gap -->
			<g class="wire red">
				<path d="M46 98 V52 Q46 44 54 44 H140" />
				<path d="M180 44 H266 Q274 44 274 52 V96" />
			</g>
			<g class="wire black">
				<path d="M274 148 V182 Q274 190 266 190 H206" />
				<path d="M114 190 H54 Q46 190 46 182 V150" />
			</g>
			<!-- the current, shown only while it really flows -->
			<g class="current">
				<path d="M46 98 V52 Q46 44 54 44 H140" />
				<path d="M180 44 H266 Q274 44 274 52 V96" />
				<path d="M274 148 V182 Q274 190 266 190 H206" />
				<path d="M114 190 H54 Q46 190 46 182 V150" />
			</g>
			<!-- bulb holder -->
			<rect x="136" y="38" width="48" height="14" rx="4" fill="#2a2f3a" stroke="#0e1118" />
			<circle cx="142" cy="45" r="3.2" fill="url(#lt-brass)" /><circle cx="178" cy="45" r="3.2" fill="url(#lt-brass)" />
			<!-- battery holder -->
			<rect x="28" y="92" width="36" height="64" rx="6" fill="#1b1f29" stroke="#0b0d13" stroke-width="1.5" />
			<rect x="38" y="88" width="16" height="6" rx="2" fill="url(#lt-brass)" /><rect x="38" y="154" width="16" height="6" rx="2" fill="url(#lt-brass)" />
			<!-- knife switch: a base, two posts, and a blade that swings shut -->
			<rect x="256" y="92" width="36" height="62" rx="5" fill="#e9e2d3" stroke="#b5aa93" />
			<circle cx="274" cy="100" r="5" fill="url(#lt-brass)" stroke="#5c430f" /><circle cx="274" cy="146" r="5" fill="url(#lt-brass)" stroke="#5c430f" />
			<g class="blade">
				<rect x="271" y="98" width="6" height="50" rx="2" fill="url(#lt-brass)" stroke="#5c430f" stroke-width="0.6" />
				<rect x="266" y="92" width="16" height="12" rx="4" fill="#7a1f1f" stroke="#3d0d0d" />
			</g>
			<!-- crocodile clips either side of the gap -->
			<g class="clip">
				<path d="M96 184 H118 L126 188 V192 L118 196 H96 Z" fill="url(#lt-steel)" stroke="#4c5362" />
				<rect x="92" y="183" width="12" height="14" rx="3" fill="#1c1f27" />
				<path d="M224 184 H202 L194 188 V192 L202 196 H224 Z" fill="url(#lt-steel)" stroke="#4c5362" />
				<rect x="216" y="183" width="12" height="14" rx="3" fill="#b3261e" />
			</g>
		</svg>

		<span class="battery" aria-hidden="true"><GameImage name="circuit/battery" eager /></span>
		<span class="pole plus" aria-hidden="true">+</span>
		<span class="pole minus" aria-hidden="true">−</span>
		<span class="glow" aria-hidden="true"></span>
		<span class="bulb" aria-hidden="true"><GameImage name="circuit/bulb" eager /></span>
		<span class="part bulb-name">Mentol</span>
		<span class="part battery-name">Bateri</span>
		<span class="part switch-name">{closed ? 'Suis tutup' : 'Suis buka'}</span>

		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="gap" class:filled={!!inGap} data-zone="gap">
			{#if inGap}
				<span class="thing">
					<span class="pic">
						<GameImage name={material?.key} eager fit="cover">
							{#snippet fallback()}
								{#if inGap.sticker ?? stickerFor(inGap.text)}<Sticker key={inGap.sticker ?? stickerFor(inGap.text) ?? ''} size={36} alt="" />{/if}
							{/snippet}
						</GameImage>
						{#if right}<Mark ok={inGap.id === right} />{/if}
					</span>
					<span class="label">{inGap.text}</span>
				</span>
			{:else}
				<span class="hint">Kepit bahan di sini</span>
			{/if}
		</div>
	</div>

	{#if closed && inGap}
		<p class="finding" class:on={flows} aria-live="polite">
			{#if known}
				{#if flows}
					<strong>Mentol menyala.</strong> {material?.name ?? inGap.text} ialah konduktor: arus mengalir melaluinya dan litar lengkap.
				{:else}
					<strong>Mentol tidak menyala.</strong> {material?.name ?? inGap.text} ialah penebat: arus tidak dapat mengalir, jadi litar terputus.
				{/if}
			{:else if right}
				{flows ? 'Mentol menyala: litar lengkap.' : 'Mentol tidak menyala.'}
			{:else}
				Suis ditutup. Tunggu keputusannya…
			{/if}
		</p>
	{/if}
	{#if right && pick !== right}
		<p class="should">Jawapan yang betul: <strong>{choices.find((c) => c.id === right)?.text}</strong></p>
	{/if}

	{#if !locked}
		<ul class="tray" aria-label="Bahan untuk diuji">
			{#each choices as c (c.id)}
				{@const m = find<Material>('materials', c.text)}
				<li>
					<button
						type="button"
						class="item"
						class:on={chosen === c.id}
						aria-pressed={chosen === c.id}
						{@attach dragTap({ enabled: () => !locked, home: () => (chosen === c.id ? 'gap' : 'tray'), tap: () => put(c.id), drop: (zone) => zone === 'gap' && put(c.id) })}
					>
						<span class="pic">
							<GameImage name={m?.key} fit="cover">
								{#snippet fallback()}
									{#if c.sticker ?? stickerFor(c.text)}<Sticker key={c.sticker ?? stickerFor(c.text) ?? ''} size={40} alt="" />{/if}
								{/snippet}
							</GameImage>
						</span>
						<span>{c.text}</span>
					</button>
				</li>
			{/each}
		</ul>
		<Checks tip={chosen ? 'Tutup suis untuk menguji litar.' : 'Seret atau ketik satu bahan untuk mengepitnya di dalam litar.'} label="Tutup suis" ready={!!chosen} dirty={!!chosen} onreset={() => (chosen = null)} oncheck={() => p.onanswer?.(chosen)} />
	{/if}
</div>

<style>
	.bench {
		display: grid;
		gap: 0.7rem;
	}
	/* a green workbench mat with its measuring grid */
	.board {
		position: relative;
		container-type: inline-size;
		width: 100%;
		aspect-ratio: 320 / 232;
		overflow: hidden;
		border-radius: var(--r-lg);
		background:
			linear-gradient(rgb(255 255 255 / 0.07) 1px, transparent 1px) 0 0 / 100% 12.5%,
			linear-gradient(90deg, rgb(255 255 255 / 0.07) 1px, transparent 1px) 0 0 / 10% 100%,
			radial-gradient(120% 90% at 50% 20%, #2f7a66, #17443a);
		box-shadow:
			inset 0 0 0 3px #123229,
			inset 0 0 40px rgb(0 0 0 / 0.35);
	}
	.wires {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
	}
	.wire path {
		fill: none;
		stroke-width: 5;
		stroke-linecap: round;
		filter: drop-shadow(0 2px 1.5px rgb(0 0 0 / 0.45));
	}
	.wire.red path {
		stroke: #c9352b;
	}
	.wire.black path {
		stroke: #1d2129;
	}
	.current path {
		fill: none;
		stroke: #ffe680;
		stroke-width: 2.2;
		stroke-linecap: round;
		stroke-dasharray: 2 12;
		opacity: 0;
	}
	.flows .current path {
		opacity: 1;
		animation: flow 0.7s linear infinite;
	}
	@keyframes flow {
		to {
			stroke-dashoffset: -14;
		}
	}
	.blade {
		transform-origin: 274px 146px;
		transform-box: view-box;
		rotate: -34deg;
		transition: rotate 0.35s cubic-bezier(0.5, 1.6, 0.5, 1);
	}
	.closed .blade {
		rotate: 0deg;
	}

	.battery {
		position: absolute;
		left: 10.2%;
		top: 40.5%;
		width: 8.6%;
	}
	.battery :global(img) {
		width: 100%;
		filter: drop-shadow(0 2px 3px rgb(0 0 0 / 0.5));
	}
	.pole {
		position: absolute;
		left: 21.5%;
		color: #fff;
		font: 700 0.85rem var(--font-display);
		text-shadow: 0 1px 2px #000;
	}
	.plus {
		top: 36%;
	}
	.minus {
		top: 62%;
	}
	.bulb {
		position: absolute;
		left: 50%;
		top: -9.5%;
		width: 13.5%;
		translate: -50% 0;
		rotate: 180deg;
		transform-origin: 50% 50%;
		transition: filter 0.35s;
	}
	.bulb :global(img) {
		width: 100%;
		filter: drop-shadow(0 3px 4px rgb(0 0 0 / 0.5));
	}
	/* the lit filament: a warm glow through the real glass */
	.glow {
		position: absolute;
		left: 50%;
		top: 2%;
		width: 34%;
		aspect-ratio: 1;
		translate: -50% -42%;
		border-radius: 50%;
		background: radial-gradient(circle, rgb(255 244 190 / 0.95) 0 12%, rgb(255 214 90 / 0.75) 26%, rgb(255 190 40 / 0.25) 48%, transparent 68%);
		opacity: 0;
		transition: opacity 0.4s;
		pointer-events: none;
	}
	.flows .glow {
		opacity: 1;
		animation: shine 2.2s ease-in-out infinite;
	}
	.flows .bulb {
		filter: brightness(1.5) sepia(0.6) saturate(2.4) hue-rotate(-12deg);
	}
	@keyframes shine {
		50% {
			transform: scale(1.06);
		}
	}
	.part {
		position: absolute;
		padding: 0.05rem 0.4rem;
		border-radius: 999px;
		background: rgb(8 24 20 / 0.7);
		color: #d9f3ea;
		font: 700 0.64rem/1.4 var(--font-body);
		white-space: nowrap;
	}
	.bulb-name {
		left: 63%;
		top: 4%;
	}
	.battery-name {
		left: 3%;
		top: 71%;
	}
	.switch-name {
		right: 3%;
		top: 71%;
	}

	.gap {
		position: absolute;
		left: 50%;
		bottom: 3%;
		display: grid;
		place-items: center;
		width: 31%;
		min-height: 31%;
		translate: -50% 0;
		border: 2px dashed rgb(255 255 255 / 0.55);
		border-radius: var(--r-md);
		background: rgb(8 30 24 / 0.5);
	}
	.gap.filled {
		border-color: transparent;
		background: transparent;
	}
	.gap:global(.zone-hover) {
		border-color: #ffd23f;
		background: rgb(255 210 63 / 0.18);
	}
	.hint {
		padding: 0.2rem;
		color: #e6f6ef;
		font: 700 0.7rem/1.2 var(--font-body);
		text-align: center;
	}
	.thing {
		display: grid;
		justify-items: center;
		gap: 0.1rem;
	}
	.pic {
		position: relative;
		display: grid;
		place-items: center;
		width: 3.1rem;
		height: 3.1rem;
		border-radius: 0.7rem;
		background: #fff;
		box-shadow:
			0 0 0 2px #fff,
			0 3px 8px rgb(0 0 0 / 0.35);
	}
	.pic :global(img.g-img) {
		width: 100%;
		height: 100%;
		border-radius: 0.6rem;
	}
	.thing .pic {
		width: clamp(2.4rem, 15cqw, 3.4rem);
		height: clamp(2.4rem, 15cqw, 3.4rem);
	}
	.label {
		max-width: 30cqw;
		padding: 0 0.4rem;
		border-radius: 999px;
		background: rgb(8 24 20 / 0.8);
		color: #fff;
		font: 700 0.68rem/1.4 var(--font-body);
		text-align: center;
		overflow-wrap: anywhere;
	}

	.finding {
		padding: 0.5rem 0.8rem;
		border-radius: var(--r-md);
		background: #eef1f4;
		color: #2c3540;
		font-size: 0.92rem;
		line-height: 1.35;
	}
	.finding.on {
		background: #fff6d6;
		color: #5a3d00;
	}
	.should {
		padding: 0.4rem 0.8rem;
		border-radius: var(--r-md);
		background: #fff1e6;
		color: #8a3b12;
		font-weight: 700;
	}

	.tray {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(7.2rem, 1fr));
		gap: 0.5rem;
		margin: 0;
		padding: 0.6rem;
		list-style: none;
		border-radius: var(--r-lg);
		background: var(--paper-2, #f6efe3);
	}
	.item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		width: 100%;
		min-height: 3.6rem;
		padding: 0.3rem 0.6rem 0.3rem 0.3rem;
		border: 0;
		border-radius: var(--r-md);
		background: #fff;
		color: var(--ink);
		font: 700 0.92rem/1.15 var(--font-body);
		text-align: left;
		box-shadow:
			0 4px 0 #e2d6c4,
			0 6px 12px rgb(31 45 39 / 0.08);
		cursor: grab;
		touch-action: none;
	}
	.item .pic {
		flex: none;
		box-shadow: 0 0 0 1px #e7dccb;
	}
	.item.on {
		background: #fff7d6;
		box-shadow:
			0 4px 0 #f0c64a,
			0 0 0 2px #f0c64a;
	}
	.item:global(.dragging) {
		z-index: 50;
		cursor: grabbing;
	}
	@media (prefers-reduced-motion: reduce) {
		.flows .current path,
		.flows .glow {
			animation: none;
		}
		.blade {
			transition: none;
		}
	}
</style>
