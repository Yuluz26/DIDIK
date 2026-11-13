<!--
	Label rajah: a diagram with numbered pins on its parts, a numbered line for each pin underneath, and
	the labels to put on them. Drag a label onto a pin or its line, or tap a label and then the pin. Tap a
	placed label to take it back. The lines keep labels from piling up on a small screen, as on a school
	worksheet. `skin` dresses it as the game it is: an X-ray scan (Tubuh Manusia), a microscope's eyepiece
	(Mikroskop), an old map (Peta Nusantara), or plain.
-->
<script lang="ts">
	import { diagramOf, diagramUrl } from '$lib/diagrams';
	import Sticker from '$ui/Sticker.svelte';
	import GameImage from './GameImage.svelte';
	import { dragTap } from '$lib/questions/drag';
	import Checks from './Checks.svelte';
	import Mark from './Mark.svelte';
	import { type GameProps, Pairs, isLocked, rightOf, shown } from './kit.svelte';

	let { skin = 'plain', ...p }: GameProps & { skin?: 'plain' | 'xray' | 'scope' | 'parchment' } = $props();

	const d = $derived(diagramOf(p.question.diagram));
	const spots = $derived(p.question.spots ?? []);
	const labels = $derived(p.question.labels ?? []);
	const text = $derived(new Map(labels.map((l) => [l.id, l.text])));
	const locked = $derived(isLocked(p));
	const pairs = new Pairs(true);
	const map = $derived(shown<Record<string, string>>(p, pairs.map));
	const right = $derived(rightOf<Record<string, string>>(p));
	const tray = $derived(labels.filter((l) => !Object.values(map).includes(l.id)));
	let lit = $state<string | null>(null);

	// Mikroskop: the specimen starts out of focus, as it does on a real stage. The focus knob brings it
	// sharp; where "sharp" is differs from one question to the next. Labels go on once it can be seen.
	const sharpAt = $derived(28 + ([...p.question.id].reduce((sum, ch) => sum + ch.charCodeAt(0), 0) % 46));
	let focus = $state(6);
	const blur = $derived(skin === 'scope' && !locked ? Math.max(0, Math.abs(focus - sharpAt) - 4) : 0);
	const sharp = $derived(blur === 0);

	function drop(label: string, zone: string) {
		if (zone.startsWith('s-')) pairs.set(zone.slice(2), label);
		else if (zone === 'tray') {
			const at = pairs.keyOf(label);
			if (at) pairs.unset(at);
		}
	}
	function placeAt(spot: string) {
		if (locked || !pairs.picked) return;
		pairs.set(spot, pairs.picked);
	}
	// Down the eyepiece a drawing sits whole inside the round field. A photograph taken through a microscope
	// fills the field instead, as it would, as long as every place to label is still inside the circle.
	const scopeWidth = $derived.by(() => {
		if (!d) return 78;
		const whole = d.w >= d.h ? 78 : (78 * d.w) / d.h;
		if (!d.photo) return whole;
		const wide = Math.max(100, (100 * d.w) / d.h);
		const tall = (wide * d.h) / d.w;
		const inside = spots.every((s) => Math.hypot(((s.x - 50) * wide) / 100, ((s.y - 50) * tall) / 100) <= 43);
		return inside ? wide : whole;
	});
	const LOOK = { plain: '', xray: 'Imbasan X-ray', scope: 'Pembesaran 400×', parchment: 'Peta lama' };
</script>

<div class="board {skin}" class:picking={!!pairs.picked}>
	<div class="view">
		{#if skin === 'parchment'}<span class="rose" aria-hidden="true"><Sticker key="kompas" size={44} alt="" /></span>{/if}
		{#if LOOK[skin]}<span class="tag">{LOOK[skin]}</span>{/if}
		<div class="frame" style:width={d && skin !== 'scope' ? `min(100%, 30rem, calc(58vh * ${d.w} / ${d.h}))` : undefined}>
			<!-- the picture's own box: the pins are placed in it, so they sit on the parts however it is framed -->
			<div class="stage" style:aspect-ratio={d ? `${d.w} / ${d.h}` : '4 / 3'} style:width={skin === 'scope' && d ? `${scopeWidth}%` : '100%'} style:filter={blur ? `blur(${Math.min(10, blur / 3.2).toFixed(1)}px)` : undefined}>
			{#if d}<img src={diagramUrl(d.key)} alt="Rajah untuk dilabel" draggable="false" />{/if}
			{#if skin === 'xray'}<span class="scan" aria-hidden="true"></span>{/if}
			{#each sharp ? spots : [] as spot, i (spot.id)}
				{@const placed = map[spot.id]}
				{@const ok = right ? right[spot.id] === placed : null}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div
					class="pin"
					class:filled={!!placed}
					class:ok={ok === true}
					class:off={ok === false}
					class:lit={lit === spot.id}
					style:left="{spot.x}%"
					style:top="{spot.y}%"
					data-zone="s-{spot.id}"
					onclick={() => placeAt(spot.id)}
				>
					{i + 1}
				</div>
			{/each}
			</div>
		</div>
	</div>

	{#if skin === 'scope' && !locked}
		<div class="rig" class:sharp>
			<span class="instrument" aria-hidden="true"><GameImage name="micro/scope" eager /></span>
			<label class="focus">
				<span>Tombol fokus {sharp ? '· imej jelas' : ''}</span>
				<input type="range" min="0" max="100" step="1" bind:value={focus} aria-label="Tombol fokus mikroskop" />
				<small>{sharp ? 'Sel sudah jelas. Sekarang labelkan bahagiannya.' : 'Pusing tombol sehingga sel kelihatan jelas.'}</small>
			</label>
		</div>
	{/if}

	{#if sharp}
	<ol class="lines">
		{#each spots as spot, i (spot.id)}
			{@const placed = map[spot.id]}
			{@const ok = right ? right[spot.id] === placed : null}
			<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_noninteractive_element_interactions -->
			<li
				class="line"
				data-zone="s-{spot.id}"
				onclick={() => placeAt(spot.id)}
				onpointerenter={() => (lit = spot.id)}
				onpointerleave={() => (lit = null)}
			>
				<span class="num">{i + 1}</span>
				{#if placed}
					<button
						type="button"
						class="chip placed"
						class:ok={ok === true}
						class:off={ok === false}
						disabled={locked}
						aria-label="{text.get(placed)} pada nombor {i + 1}. Ketik untuk keluarkan"
						{@attach dragTap({ enabled: () => !locked, home: () => `s-${spot.id}`, tap: () => pairs.unset(spot.id), drop: (zone) => drop(placed, zone) })}
					>
						{text.get(placed)}
						{#if ok !== null}<Mark {ok} />{/if}
					</button>
					{#if ok === false && right}<span class="should">→ {text.get(right[spot.id])}</span>{/if}
				{:else}
					<span class="empty">{pairs.picked ? 'Ketik untuk letak di sini' : 'Seret label ke sini'}</span>
				{/if}
			</li>
		{/each}
	</ol>

	{#if !locked}
		<ul class="tray" data-zone="tray" aria-label="Label">
			{#each tray as label (label.id)}
				<li>
					<button
						type="button"
						class="chip"
						class:picked={pairs.picked === label.id}
						aria-pressed={pairs.picked === label.id}
						{@attach dragTap({ enabled: () => !locked, home: () => 'tray', tap: () => pairs.pick(label.id), drop: (zone) => drop(label.id, zone) })}
					>
						{label.text}
					</button>
				</li>
			{/each}
		</ul>
		<Checks
			tip={pairs.picked ? 'Sekarang ketik nombor yang betul pada rajah.' : tray.length ? 'Seret setiap label ke nombornya, atau ketik label kemudian ketik nombor.' : 'Semua sudah dilabel!'}
			ready={pairs.count() === spots.length}
			dirty={pairs.count() > 0}
			onreset={() => pairs.clear()}
			oncheck={() => p.onanswer?.(pairs.map)}
		/>
	{/if}
	{/if}
</div>

<style>
	.board {
		display: grid;
		gap: 0.8rem;
	}
	.view {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		padding: 0.7rem;
		border-radius: var(--r-lg);
		background: #fff;
		box-shadow: var(--card-shadow);
	}
	.frame {
		position: relative;
		display: grid;
		place-items: center;
		width: min(100%, 30rem);
		margin-inline: auto;
	}
	.stage {
		position: relative;
	}
	.frame img {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: contain;
		user-select: none;
		pointer-events: none;
		-webkit-user-drag: none;
	}
	.pin {
		position: absolute;
		z-index: 2;
		display: grid;
		place-items: center;
		width: 2.1rem;
		height: 2.1rem;
		translate: -50% -50%;
		border: 3px solid #fff;
		border-radius: 50%;
		background: var(--berry, #e0457b);
		color: #fff;
		font: 700 1rem/1 var(--font-display);
		box-shadow: 0 3px 8px rgb(0 0 0 / 0.3);
		transition:
			transform var(--t-state) var(--spring),
			background var(--t-state);
	}
	.pin.filled {
		background: var(--sky-deep, #1f7fb8);
	}
	.pin.ok {
		background: var(--good);
	}
	.pin.off {
		background: var(--almost);
	}
	.pin.lit,
	.pin:global(.zone-hover),
	.picking .pin {
		transform: scale(1.18);
	}
	.picking .pin {
		cursor: pointer;
		animation: pulse 1.2s ease-in-out infinite;
	}
	.tag {
		position: absolute;
		top: 0.5rem;
		left: 0.6rem;
		z-index: 3;
		padding: 0.15rem 0.55rem;
		border-radius: 999px;
		background: rgb(0 0 0 / 0.55);
		color: #fff;
		font: 700 0.72rem/1.4 var(--font-display);
		letter-spacing: 0.04em;
	}
	.lines {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr));
		gap: 0.45rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.line {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.45rem;
		min-height: 3rem;
		padding: 0.35rem 0.5rem;
		border: 2px dashed var(--line, #e2d6c4);
		border-radius: var(--r-md);
		background: var(--card);
	}
	.line:global(.zone-hover) {
		border-style: solid;
		border-color: var(--sky);
	}
	.picking .line {
		cursor: pointer;
		border-color: var(--berry, #e0457b);
	}
	.num {
		display: grid;
		place-items: center;
		flex: none;
		width: 1.7rem;
		height: 1.7rem;
		border-radius: 50%;
		background: var(--ink, #2a1f2d);
		color: #fff;
		font: 700 0.9rem/1 var(--font-display);
	}
	.empty {
		color: var(--ink-3, #9a9a9a);
		font-size: 0.85rem;
		font-weight: 700;
	}
	.tray {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.5rem;
		min-height: 3.2rem;
		margin: 0;
		padding: 0.5rem;
		border-radius: var(--r-lg);
		background: var(--paper-2, #f6efe3);
		list-style: none;
	}
	.chip {
		position: relative;
		min-height: 2.6rem;
		padding: 0.35rem 0.8rem;
		border: 0;
		border-radius: var(--r-md);
		background: #fff;
		color: var(--ink);
		font: 700 0.98rem/1.15 var(--font-body);
		box-shadow:
			0 4px 0 #e2d6c4,
			0 6px 12px rgb(31 45 39 / 0.08);
		cursor: grab;
		touch-action: none;
		transition: transform var(--t-state) var(--spring);
	}
	.chip:not(:disabled):hover {
		transform: translateY(-2px);
	}
	.chip.picked {
		transform: translateY(-4px) scale(1.05);
		outline: 3px solid var(--berry, #e0457b);
		outline-offset: 2px;
	}
	.chip:global(.dragging) {
		z-index: 50;
		cursor: grabbing;
	}
	.chip.placed {
		background: var(--brand-soft, #e5f6ec);
	}
	.chip.ok {
		box-shadow: 0 0 0 3px var(--good);
	}
	.chip.off {
		box-shadow: 0 0 0 3px var(--almost);
	}
	.chip:disabled {
		cursor: default;
	}
	.should {
		color: var(--on-almost-soft, #a2461b);
		font-weight: 800;
		font-size: 0.85rem;
	}

	/* Tubuh Manusia: a radiology screen */
	.xray .view {
		background:
			linear-gradient(rgb(120 220 255 / 0.06) 1px, transparent 1px) 0 0 / 100% 14px,
			radial-gradient(circle at 50% 40%, #12324a, #050d16 75%);
		box-shadow:
			inset 0 0 0 3px #0b2233,
			0 10px 24px rgb(5 13 22 / 0.35);
	}
	.xray .frame img {
		filter: drop-shadow(0 0 12px rgb(120 220 255 / 0.25));
	}
	.xray .pin {
		background: #10b6d8;
		box-shadow: 0 0 0 4px rgb(16 182 216 / 0.3);
	}
	.xray .pin.filled {
		background: #f6c445;
		color: #2a1f2d;
	}
	.xray .pin.ok {
		background: var(--good);
		color: #fff;
	}
	.xray .pin.off {
		background: var(--almost);
		color: #fff;
	}
	.scan {
		position: absolute;
		inset: 0 0 auto;
		z-index: 1;
		height: 18%;
		background: linear-gradient(180deg, transparent, rgb(120 230 255 / 0.25), transparent);
		animation: scan 3.6s linear infinite;
		pointer-events: none;
	}

	/* Mikroskop: looking down the eyepiece */
	.scope .view {
		background: radial-gradient(circle, #2b2d33 0, #111215 70%);
	}
	.scope .frame {
		width: min(100%, 22rem);
		aspect-ratio: 1 / 1 !important;
		overflow: hidden;
		border: 10px solid #3a3d46;
		border-radius: 50%;
		background: radial-gradient(circle, #fefdf6, #e9efe0 70%, #c9d3bf);
		box-shadow:
			inset 0 0 30px rgb(0 0 0 / 0.45),
			0 0 0 4px #1d1f24;
	}
	.scope .stage {
		transition: filter 0.12s linear;
	}
	/* the instrument and its focus knob */
	.rig {
		display: flex;
		align-items: center;
		gap: 0.8rem;
		padding: 0.5rem 0.8rem 0.5rem 0.5rem;
		border-radius: var(--r-md);
		background: linear-gradient(180deg, #f3f5f8, #dfe4ea);
		box-shadow: inset 0 0 0 2px #c5ccd6;
	}
	.instrument {
		flex: none;
		width: 3.6rem;
	}
	.instrument :global(img) {
		width: 100%;
		filter: drop-shadow(0 3px 4px rgb(0 0 0 / 0.3));
	}
	.focus {
		display: grid;
		flex: 1;
		min-width: 0;
		gap: 0.2rem;
		color: #2c3540;
		font: 700 0.85rem var(--font-display);
	}
	.focus small {
		color: #5a6572;
		font: 600 0.78rem/1.3 var(--font-body);
	}
	.rig.sharp .focus span {
		color: #0f7a55;
	}
	/* a knurled metal knob on a slotted track */
	.focus input {
		width: 100%;
		height: 2.6rem;
		margin: 0;
		background: transparent;
		appearance: none;
		-webkit-appearance: none;
		touch-action: pan-y;
		cursor: ew-resize;
	}
	.focus input::-webkit-slider-runnable-track {
		height: 0.55rem;
		border-radius: 999px;
		background: linear-gradient(180deg, #7d8694, #aab3c0);
		box-shadow: inset 0 1px 2px rgb(0 0 0 / 0.4);
	}
	.focus input::-moz-range-track {
		height: 0.55rem;
		border-radius: 999px;
		background: linear-gradient(180deg, #7d8694, #aab3c0);
	}
	.focus input::-webkit-slider-thumb {
		width: 2.2rem;
		height: 2.2rem;
		margin-top: -0.85rem;
		border: 2px solid #23272f;
		border-radius: 50%;
		background: repeating-conic-gradient(#4a4f5a 0 9deg, #7c8492 9deg 18deg);
		box-shadow: 0 2px 5px rgb(0 0 0 / 0.4);
		appearance: none;
		-webkit-appearance: none;
	}
	.focus input::-moz-range-thumb {
		width: 2.2rem;
		height: 2.2rem;
		border: 2px solid #23272f;
		border-radius: 50%;
		background: repeating-conic-gradient(#4a4f5a 0 9deg, #7c8492 9deg 18deg);
	}

	/* Peta Nusantara: an old map */
	.parchment .view {
		background:
			radial-gradient(circle at 20% 15%, rgb(255 255 255 / 0.5), transparent 40%),
			radial-gradient(circle at 80% 90%, rgb(140 90 30 / 0.18), transparent 45%),
			#f1dfb4;
		box-shadow:
			inset 0 0 0 3px #b98a4b,
			inset 0 0 40px rgb(120 70 20 / 0.35),
			0 8px 18px rgb(80 50 20 / 0.25);
	}
	.parchment .frame img {
		filter: sepia(0.35) saturate(1.1);
		border-radius: 6px;
	}
	/* a map pin: the teardrop turns, the number on it stays upright */
	.parchment .pin {
		isolation: isolate;
		border: 0;
		background: transparent;
		box-shadow: none;
	}
	.parchment .pin::before {
		content: '';
		position: absolute;
		inset: 0;
		z-index: -1;
		border: 3px solid #fff6dd;
		border-radius: 50% 50% 50% 0;
		background: #b8322a;
		rotate: -45deg;
		box-shadow: 0 3px 8px rgb(0 0 0 / 0.3);
	}
	.parchment .pin.filled::before {
		background: #2c6e8f;
	}
	.parchment .pin.ok::before {
		background: var(--good);
	}
	.parchment .pin.off::before {
		background: var(--almost);
	}
	.rose {
		position: absolute;
		right: 0.5rem;
		bottom: 1.6rem;
		z-index: 3;
		opacity: 0.85;
	}

	@keyframes pulse {
		50% {
			box-shadow: 0 0 0 7px rgb(224 69 123 / 0.25);
		}
	}
	@keyframes scan {
		from {
			top: -18%;
		}
		to {
			top: 100%;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.scan,
		.picking .pin {
			animation: none;
		}
	}
</style>
