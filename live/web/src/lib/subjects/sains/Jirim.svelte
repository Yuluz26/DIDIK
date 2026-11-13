<!--
	Balang Jirim: glass jars on a lab shelf, one for each group, each showing its state inside: packed
	blocks for a solid, a rippling liquid, rising bubbles for a gas (chosen from the group's name, so
	"Pepejal", "Cecair" and "Gas" look like themselves).
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import GameImage from '../GameImage.svelte';
	import SortPlay, { type SortView } from '../SortPlay.svelte';
	import SortedThing from '../SortedThing.svelte';
	import { find, stateOfGroup } from '../assets';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	// A jar shows the state its group names. The server gives this game only to groups that are states of
	// matter; a group that is not is drawn as a plain jar, never as a state it is not.
	const stateOf = (name: string): 'pepejal' | 'cecair' | 'gas' | 'plain' => stateOfGroup(name) ?? 'plain';
	const photo = (text: string) => find('materials', text)?.key;
	const EXAMPLE = { pepejal: 'mat/ice', cecair: 'mat/water', gas: 'mat/steam', plain: null };
</script>

<SortPlay {p} pool="Bahan" tip="Masukkan setiap bahan ke dalam balang keadaan jirimnya.">
	{#snippet card(item)}
		<span class="mini"><GameImage name={photo(item.text)} fit="cover">{#snippet fallback()}{#if item.sticker}<Sticker key={item.sticker} size={38} alt="" />{/if}{/snippet}</GameImage></span>
		<span>{item.text}</span>
	{/snippet}
	{#snippet board(v: SortView)}
		<div class="shelf" style:--n={v.groups.length}>
			{#each v.groups as g, i (g.id)}
				{@const kind = stateOf(g.name)}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div class="jar {kind}" data-zone={v.zone(g.id)} onclick={() => v.tapGroup(g.id)}>
					<span class="lid" aria-hidden="true"></span>
					<span class="glass" aria-hidden="true">
						{#if kind === 'pepejal'}<i class="block b1"></i><i class="block b2"></i><i class="block b3"></i>{/if}
						{#if kind === 'cecair'}<i class="liquid"></i>{/if}
						{#if kind === 'gas'}{#each [0, 1, 2, 3, 4] as b (b)}<i class="bubble" style:--b={b}></i>{/each}{/if}
					</span>
					<div class="things">
						{#each v.inside(g.id) as item (item.id)}<SortedThing {v} {item} group={g.id} size={28} photo={photo(item.text)} />{/each}
					</div>
					<h4>
						{#if EXAMPLE[kind]}<span class="eg"><GameImage name={EXAMPLE[kind]} fit="cover" /></span>{:else if g.sticker}<Sticker key={g.sticker} size={24} alt="" />{/if}
						<span>{g.name}</span>
					</h4>
				</div>
			{/each}
		</div>
	{/snippet}
</SortPlay>

<style>
	.eg {
		display: inline-grid;
		flex: none;
		width: 1.35rem;
		height: 1.35rem;
		overflow: hidden;
		border-radius: 50%;
		box-shadow: 0 0 0 2px #fff;
	}
	.eg :global(img.g-img) {
		width: 100%;
		height: 100%;
	}
	.mini {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.6rem;
		height: 2.6rem;
		overflow: hidden;
		border-radius: 0.6rem;
		background: #fff;
		box-shadow: 0 0 0 1px #e7dccb;
	}
	.mini :global(img.g-img) {
		width: 100%;
		height: 100%;
	}
	.shelf {
		display: grid;
		grid-template-columns: repeat(var(--n), minmax(0, 1fr));
		gap: 0.5rem;
		padding: 0.8rem 0.6rem 0.4rem;
		border-radius: var(--r-lg);
		background:
			linear-gradient(180deg, transparent calc(100% - 1rem), #8b6a43 calc(100% - 1rem), #6e512f),
			linear-gradient(180deg, #f2f6f8, #e2eaee);
		box-shadow: inset 0 0 0 3px #cfdbe2;
	}
	.jar {
		position: relative;
		display: grid;
		grid-template-rows: auto 1fr auto;
		min-height: 13rem;
		padding: 1.2rem 0.3rem 0.4rem;
		border: 3px solid rgb(160 190 210 / 0.9);
		border-top: 0;
		border-radius: 0 0 1.4rem 1.4rem;
		background: linear-gradient(90deg, rgb(255 255 255 / 0.65), rgb(220 240 250 / 0.35) 40%, rgb(255 255 255 / 0.7));
		overflow: hidden;
	}
	.jar:global(.zone-hover) {
		border-color: #1f8fc0;
		box-shadow: 0 0 0 4px rgb(31 143 192 / 0.2);
	}
	.lid {
		position: absolute;
		top: 0;
		left: -3px;
		right: -3px;
		height: 0.7rem;
		border-radius: 4px;
		background: linear-gradient(180deg, #9aa7b3, #6f7c88);
	}
	.glass {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}
	.block {
		position: absolute;
		bottom: 0.5rem;
		width: 30%;
		height: 2rem;
		border-radius: 4px;
		background: linear-gradient(135deg, #c8d8e4, #8fa7ba);
		box-shadow: inset 0 0 0 2px rgb(255 255 255 / 0.4);
	}
	.b1 {
		left: 8%;
	}
	.b2 {
		left: 38%;
		height: 2.6rem;
	}
	.b3 {
		left: 66%;
		height: 1.6rem;
	}
	.liquid {
		position: absolute;
		left: 0;
		right: 0;
		bottom: 0;
		height: 42%;
		background: linear-gradient(180deg, rgb(90 180 230 / 0.55), rgb(40 120 190 / 0.6));
	}
	.liquid::before {
		content: '';
		position: absolute;
		left: -50%;
		top: -6px;
		width: 200%;
		height: 12px;
		background: radial-gradient(ellipse at 25% 100%, transparent 60%, rgb(90 180 230 / 0.55) 62%) 0 0 / 40px 12px repeat-x;
		animation: ripple 2.4s linear infinite;
	}
	.bubble {
		position: absolute;
		bottom: -1rem;
		left: calc(12% + var(--b) * 18%);
		width: 0.7rem;
		height: 0.7rem;
		border: 2px solid rgb(120 170 200 / 0.6);
		border-radius: 50%;
		animation: rise calc(2.4s + var(--b) * 0.5s) linear calc(var(--b) * -0.7s) infinite;
	}
	.things {
		position: relative;
		z-index: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.3rem;
		grid-row: 2;
		align-self: start;
	}
	h4 {
		position: relative;
		z-index: 1;
		display: inline-flex;
		justify-content: center;
		align-items: center;
		gap: 0.2rem;
		padding: 0.15rem 0.3rem;
		border-radius: 6px;
		background: #fffdf6;
		color: #2a3a48;
		font: 700 0.92rem/1.1 var(--font-display);
		text-align: center;
		box-shadow: 0 2px 0 #c9b28a;
	}
	@keyframes ripple {
		to {
			translate: 40px 0;
		}
	}
	@keyframes rise {
		to {
			bottom: 100%;
			opacity: 0;
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.liquid::before,
		.bubble {
			animation: none;
		}
	}
</style>
