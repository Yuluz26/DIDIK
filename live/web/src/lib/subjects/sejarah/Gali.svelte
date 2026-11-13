<!--
	Gali Artifak: an excavation trench marked out in squares with string and pegs. Each square hides one
	answer under three layers of earth: tap to dig (the soil flies), and the find comes to light. Tap a
	find to tag it as the answer, then Semak.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Sticker from '$ui/Sticker.svelte';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked, stickerFor } from '../kit.svelte';

	let p: GameProps = $props();

	const choices = $derived(p.question.choices ?? []);
	const locked = $derived(isLocked(p));
	let chosen = $state<string | null>(null);
	let dug = $state<Record<string, number>>({});
	let puffs = $state<Record<string, number>>({});
	const pick = $derived<string | null>(p.mine !== undefined ? p.mine : p.reveal ? p.reveal.correct[0] : chosen);
	const right = $derived<string | null>(p.reveal ? p.reveal.correct[0] : null);
	const DEEP = 3;
	const FINDS = ['tempayan', 'syiling', 'keris', 'cincin', 'permata', 'tulang', 'kunci-lama', 'skrol'];
	const open = (id: string) => locked || (dug[id] ?? 0) >= DEEP;

	function dig(id: string) {
		if (locked) return;
		if (open(id)) {
			chosen = id;
			play('pop');
			return;
		}
		dug = { ...dug, [id]: (dug[id] ?? 0) + 1 };
		puffs = { ...puffs, [id]: (puffs[id] ?? 0) + 1 };
		play((dug[id] ?? 0) >= DEEP ? 'key' : 'dig');
	}
	const found = $derived(choices.filter((c) => open(c.id)).length);
	import GameImage from '../GameImage.svelte';
	import { asset, find } from '../assets';
	// real excavation soil, its layers showing, under the squares
	const SOIL = asset('hist/soil');
	// Finds are shown as photographs only if every one has its own; a single photograph among stickers
	// would make one answer stand out.
	const photos = $derived(choices.every((c) => !!find('history', c.text)));
</script>

<div class="site" style:--soil={SOIL ? `url(${SOIL.src})` : 'none'}>
	<div class="trench" style:--cols={choices.length > 4 ? 3 : 2}>
		{#each choices as c, i (c.id)}
			{@const depth = locked ? DEEP : (dug[c.id] ?? 0)}
			{@const ok = right ? c.id === right : null}
			<button
				type="button"
				class="square"
				class:open={open(c.id)}
				class:on={pick === c.id}
				style:--d={depth}
				disabled={locked}
				onclick={() => dig(c.id)}
				aria-label={open(c.id) ? `Temuan: ${c.text}` : `Petak ${String.fromCharCode(65 + i)}, gali`}
			>
				<span class="grid-ref">{String.fromCharCode(65 + i)}{i + 1}</span>
				{#if open(c.id)}
					<span class="find">
						<span class="relic">
							<GameImage name={photos ? find('history', c.text)?.key : null} fit="cover">
								{#snippet fallback()}<Sticker key={c.sticker ?? stickerFor(c.text) ?? FINDS[i % FINDS.length]} size={44} alt="" />{/snippet}
							</GameImage>
						</span>
						<span class="label">{c.text}</span>
					</span>
					{#if right && (pick === c.id || c.id === right)}<Mark ok={c.id === right} />{/if}
				{:else}
					<span class="soil" aria-hidden="true"></span>
					<span class="dig-hint">{DEEP - depth}×</span>
				{/if}
				{#key puffs[c.id]}{#if puffs[c.id]}<span class="dust" aria-hidden="true"></span>{/if}{/key}
			</button>
		{/each}
	</div>
	<p class="log"><span class="trowel" aria-hidden="true"><GameImage name="hist/trowel" eager /></span> Jumpaan: <strong>{locked ? choices.length : found}</strong> / {choices.length}</p>
	{#if !locked}
		<Checks
			tip={chosen ? 'Artifak ditanda. Semak bila pasti.' : found ? 'Ketik artifak untuk menandanya sebagai jawapan.' : 'Ketik petak untuk menggali.'}
			ready={!!chosen}
			dirty={!!chosen}
			onreset={() => (chosen = null)}
			oncheck={() => p.onanswer?.(chosen)}
		/>
	{/if}
</div>

<style>
	/* the trench is dug in real ground */
	.trench {
		background-image: linear-gradient(rgb(60 36 16 / 0.35), rgb(60 36 16 / 0.35)), var(--soil) !important;
		background-size: cover !important;
		background-position: center !important;
	}
	.relic {
		display: grid;
		place-items: center;
		width: 3.4rem;
		height: 3.4rem;
		overflow: hidden;
		border-radius: 0.6rem;
		background: #f3ead8;
		box-shadow:
			0 0 0 2px #fff8e8,
			0 3px 8px rgb(40 20 0 / 0.4);
	}
	.relic :global(img.g-img) {
		width: 100%;
		height: 100%;
	}
	.trowel {
		display: inline-block;
		width: 2rem;
		vertical-align: middle;
	}
	.trowel :global(img) {
		width: 100%;
	}
	.site {
		display: grid;
		gap: 0.6rem;
	}
	.trench {
		display: grid;
		grid-template-columns: repeat(var(--cols), minmax(0, 1fr));
		gap: 0;
		padding: 0.6rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #8c6239, #6f4b2a);
		box-shadow:
			inset 0 0 0 3px #4f341c,
			inset 0 10px 20px rgb(0 0 0 / 0.35);
	}
	.square {
		position: relative;
		display: grid;
		place-items: center;
		min-height: 7.5rem;
		padding: 0.4rem;
		border: 1px solid rgb(255 240 200 / 0.75);
		background: hsl(30 38% calc(36% + var(--d) * 9%));
		color: var(--ink);
		cursor: pointer;
		overflow: hidden;
		transition: background 0.25s;
	}
	.square::before,
	.square::after {
		content: '';
		position: absolute;
		width: 6px;
		height: 6px;
		border-radius: 50%;
		background: #d9c08a;
	}
	.square::before {
		left: -3px;
		top: -3px;
	}
	.square::after {
		right: -3px;
		bottom: -3px;
	}
	.square.open {
		background: radial-gradient(circle at 50% 45%, #f6e6c2, #d9b98a 70%);
		box-shadow: inset 0 6px 14px rgb(80 50 20 / 0.35);
	}
	.square.on {
		outline: 4px solid #ffd23f;
		outline-offset: -4px;
	}
	.square:disabled {
		cursor: default;
	}
	.soil {
		position: absolute;
		inset: 8%;
		border-radius: 40% 50% 45% 55%;
		background:
			radial-gradient(circle at 30% 30%, rgb(255 255 255 / 0.12) 0 8%, transparent 9%),
			radial-gradient(circle at 70% 60%, rgb(0 0 0 / 0.15) 0 6%, transparent 7%),
			radial-gradient(circle at 45% 75%, rgb(0 0 0 / 0.12) 0 5%, transparent 6%),
			linear-gradient(160deg, hsl(28 40% calc(40% - var(--d) * 4%)), hsl(25 45% calc(28% - var(--d) * 3%)));
		scale: calc(1 - var(--d) * 0.22);
		transition: scale 0.2s var(--spring, ease-out);
	}
	.dig-hint {
		position: relative;
		color: #fff2d6;
		font: 700 0.95rem var(--font-display);
		text-shadow: 0 1px 2px rgb(0 0 0 / 0.5);
	}
	.find {
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		animation: unearth 0.5s var(--spring, ease-out);
	}
	.label {
		padding: 0.1rem 0.4rem;
		border-radius: 6px;
		background: rgb(255 253 246 / 0.95);
		font: 700 0.85rem/1.1 var(--font-body);
		text-align: center;
		box-shadow: 0 2px 0 #c9a46a;
	}
	.grid-ref {
		position: absolute;
		left: 0.3rem;
		top: 0.2rem;
		color: rgb(255 240 210 / 0.85);
		font: 700 0.65rem var(--font-display);
	}
	.dust {
		position: absolute;
		left: 50%;
		top: 50%;
		width: 3rem;
		height: 3rem;
		translate: -50% -50%;
		border-radius: 50%;
		background: radial-gradient(circle, rgb(230 200 150 / 0.9) 0 20%, transparent 60%);
		animation: puff 0.5s ease-out forwards;
		pointer-events: none;
	}
	.log {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.4rem;
		color: var(--ink-2);
		font-weight: 800;
	}
	@keyframes puff {
		to {
			scale: 3;
			opacity: 0;
		}
	}
	@keyframes unearth {
		from {
			transform: translateY(14px) scale(0.6);
			opacity: 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.dust,
		.find {
			animation: none;
		}
	}
</style>
