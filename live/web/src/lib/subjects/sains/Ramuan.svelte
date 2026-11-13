<!--
	Makmal Ramuan: bottles of ingredients on a lab shelf above a big beaker. Tap a bottle to pour it in
	(tap it again to take it back out); the liquid rises and takes on its colour. For "pick all the right
	ones", pour as many as asked. Semak stirs it: once the answer is shown, a right mixture fizzes and
	sparkles, a wrong one turns murky.
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Sticker from '$ui/Sticker.svelte';
	import Checks from '../Checks.svelte';
	import GameImage from '../GameImage.svelte';
	import Mark from '../Mark.svelte';
	import { find } from '../assets';
	import { type GameProps, isLocked, stickerFor } from '../kit.svelte';

	let p: GameProps = $props();

	const choices = $derived(p.question.choices ?? []);
	const many = $derived(p.question.type === 'multiple');
	const need = $derived(many ? (p.question.pick ?? 1) : 1);
	const locked = $derived(isLocked(p));
	let poured = $state<string[]>([]);
	const given = $derived<string[]>(p.mine !== undefined ? (many ? p.mine : [p.mine]) : p.reveal ? p.reveal.correct : poured);
	const right = $derived<string[] | null>(p.reveal ? p.reveal.correct : null);
	const good = $derived(!!right && given.length === right.length && given.every((g) => right.includes(g)));
	// photographs only if every bottle has one, so none stands out
	const photos = $derived(choices.every((c) => !!find('materials', c.text)?.key));
	const COLOURS = ['#ff6b8b', '#4fc3f7', '#9be15d', '#ffd54f', '#b388ff', '#ffab40'];
	const colourOf = (id: string) => COLOURS[choices.findIndex((c) => c.id === id) % COLOURS.length];
	const mix = $derived(given.length ? given.map(colourOf) : ['#dff3ff']);

	function pour(id: string) {
		if (locked) return;
		if (poured.includes(id)) {
			poured = poured.filter((x) => x !== id);
			play('tap');
		} else {
			poured = many ? (poured.length >= need ? [...poured.slice(1), id] : [...poured, id]) : [id];
			play('water');
		}
	}
</script>

<div class="lab">
	<ul class="shelf">
		{#each choices as c, i (c.id)}
			{@const ok = right ? right.includes(c.id) : null}
			<li>
				<button type="button" class="bottle" class:in={given.includes(c.id)} style:--c={COLOURS[i % COLOURS.length]} disabled={locked} onclick={() => pour(c.id)} aria-pressed={given.includes(c.id)}>
					<span class="neck" aria-hidden="true"></span>
					<span class="body">
						<!-- a photograph of what is in the bottle, as its label -->
						<span class="label-pic">
							<GameImage name={photos ? find('materials', c.text)?.key : null} fit="cover">
								{#snippet fallback()}{#if c.sticker ?? stickerFor(c.text)}<Sticker key={c.sticker ?? stickerFor(c.text) ?? ''} size={30} alt="" />{/if}{/snippet}
							</GameImage>
						</span>
					</span>
					<span class="tag">{c.text}</span>
					{#if right && (given.includes(c.id) || ok)}<Mark ok={!!ok} />{/if}
				</button>
			</li>
		{/each}
	</ul>
	<div class="station">
		<div class="beaker" class:fizz={good} class:murk={!!right && !good}>
			<span class="liquid" style:height="{12 + (given.length / Math.max(need, given.length, 1)) * 58}%" style:background="linear-gradient(180deg, {mix.join(', ')})"></span>
			{#each [0, 1, 2, 3] as b (b)}<i class="bubble" style:--b={b}></i>{/each}
			<span class="marks" aria-hidden="true"></span>
		</div>
		<p class="count">{many ? `Dituang ${given.length} / ${need}` : given.length ? 'Sudah dituang' : 'Bikar kosong'}</p>
	</div>
</div>
{#if !locked}
	<Checks
		tip={many ? `Tuang ${need} bahan yang betul. Ketik botol untuk tuang atau keluarkan.` : 'Ketik satu botol untuk dituang ke dalam bikar.'}
		label="Kacau dan semak"
		ready={poured.length === need}
		dirty={poured.length > 0}
		onreset={() => (poured = [])}
		oncheck={() => p.onanswer?.(many ? poured : poured[0])}
	/>
{/if}

<style>
	.label-pic {
		display: grid;
		place-items: center;
		width: 2rem;
		height: 2rem;
		overflow: hidden;
		border: 2px solid #fff;
		border-radius: 0.35rem;
		box-shadow: 0 1px 3px rgb(0 0 0 / 0.3);
	}
	.label-pic :global(img.g-img) {
		width: 100%;
		height: 100%;
	}
	.lab {
		display: grid;
		gap: 0.6rem;
		padding: 0.8rem 0.6rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #e9f1f4, #d6e3e8);
		box-shadow: inset 0 0 0 3px #b8cbd3;
	}
	.shelf {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(5rem, 1fr));
		gap: 0.9rem 0;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	/* every bottle stands on a wooden shelf board */
	.shelf li {
		padding-bottom: 0.35rem;
		background: linear-gradient(180deg, transparent calc(100% - 0.45rem), #a3866a calc(100% - 0.45rem), #7d6046);
	}
	.bottle {
		position: relative;
		display: grid;
		justify-items: center;
		width: 100%;
		padding: 0;
		border: 0;
		background: transparent;
		cursor: pointer;
		transition: transform 0.35s var(--spring, ease-out);
	}
	.neck {
		width: 1.1rem;
		height: 1rem;
		border-radius: 3px 3px 0 0;
		background: linear-gradient(90deg, #c9d6dc, #f4f8fa, #c9d6dc);
		box-shadow: 0 -4px 0 #8b5a2b;
	}
	.body {
		display: grid;
		place-items: center;
		width: 3.6rem;
		height: 3.8rem;
		border-radius: 0.8rem 0.8rem 1rem 1rem;
		background: linear-gradient(90deg, rgb(255 255 255 / 0.5), transparent 40%, rgb(255 255 255 / 0.25)), linear-gradient(180deg, transparent 30%, var(--c) 30%);
		box-shadow: inset 0 0 0 2px rgb(255 255 255 / 0.7);
	}
	.tag {
		margin-top: 0.25rem;
		padding: 0.15rem 0.35rem;
		border-radius: 4px;
		background: #fffef8;
		color: var(--ink);
		font: 700 0.8rem/1.1 var(--font-body);
		text-align: center;
		box-shadow: 0 1px 0 #c9d6dc;
	}
	.bottle.in {
		transform: translateY(1.2rem) rotate(-28deg);
	}
	.bottle.in .body {
		background: linear-gradient(90deg, rgb(255 255 255 / 0.5), transparent 40%), linear-gradient(180deg, transparent 80%, var(--c) 80%);
	}
	.bottle:disabled {
		cursor: default;
	}
	.station {
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		padding-top: 0.6rem;
	}
	.beaker {
		position: relative;
		width: 8.5rem;
		height: 9.5rem;
		overflow: hidden;
		border: 4px solid rgb(170 200 215 / 0.95);
		border-top: 0;
		border-radius: 0 0 1.8rem 1.8rem;
		background: rgb(255 255 255 / 0.55);
	}
	.liquid {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		opacity: 0.85;
		transition:
			height 0.6s var(--ease-out, ease-out),
			background 0.6s;
	}
	.marks {
		position: absolute;
		left: 0.4rem;
		top: 1rem;
		bottom: 1rem;
		width: 1rem;
		background: repeating-linear-gradient(180deg, rgb(120 150 165 / 0.7) 0 2px, transparent 2px 14px);
	}
	.bubble {
		position: absolute;
		bottom: -1rem;
		left: calc(25% + var(--b) * 14%);
		width: 0.6rem;
		height: 0.6rem;
		border-radius: 50%;
		background: rgb(255 255 255 / 0.85);
		opacity: 0;
	}
	.fizz .bubble {
		opacity: 1;
		animation: up calc(0.9s + var(--b) * 0.25s) ease-in calc(var(--b) * -0.3s) infinite;
	}
	.fizz {
		box-shadow: 0 0 26px 6px rgb(120 255 160 / 0.55);
	}
	.murk .liquid {
		filter: grayscale(0.8) brightness(0.7);
	}
	.count {
		color: var(--ink-2);
		font-weight: 800;
	}
	@keyframes up {
		to {
			bottom: 85%;
			opacity: 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.fizz .bubble {
			animation: none;
		}
		.bottle {
			transition: none;
		}
	}
</style>
