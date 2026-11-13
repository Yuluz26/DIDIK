<!--
	Magnet Ajaib: a big horseshoe magnet with field lines curving off its poles. Things for the first group
	stick to the magnet; things for the other groups go in the trays below.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import GameImage from '../GameImage.svelte';
	import SortPlay, { type SortView } from '../SortPlay.svelte';
	import SortedThing from '../SortedThing.svelte';
	import { find, pulls, type Entry } from '../assets';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();

	interface Material extends Entry {
		magnetic: boolean | null;
	}
	const material = (text: string) => find<Material>('materials', text);
	// the magnet's side is the group whose name says "pulled by a magnet" (else the first)
	const pullId = $derived((p.question.groups ?? []).find((g) => pulls(g.name) === true)?.id ?? p.question.groups?.[0]?.id);
</script>

<SortPlay {p} pool="Benda" tip="Bawa setiap benda ke magnet atau ke dulang. Magnet hanya menarik bahan tertentu.">
	{#snippet card(item)}
		<span class="mini"><GameImage name={material(item.text)?.key} fit="cover">{#snippet fallback()}{#if item.sticker}<Sticker key={item.sticker} size={38} alt="" />{/if}{/snippet}</GameImage></span>
		<span>{item.text}</span>
	{/snippet}
	{#snippet board(v: SortView)}
		{@const pull = v.groups.find((g) => g.id === pullId)}
		{@const rest = v.groups.filter((g) => g.id !== pullId)}
		<div class="lab">
			{#if pull}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div class="field" data-zone={v.zone(pull.id)} onclick={() => v.tapGroup(pull.id)}>
					<span class="magnet" aria-hidden="true"><GameImage name="magnet/field" eager /></span>
					<h4>{pull.name}</h4>
					<div class="stuck">
						{#each v.inside(pull.id) as item (item.id)}
							{@const held = material(item.text)?.magnetic}
							<!-- once the answer is in, the magnet does what a magnet does: it holds iron and steel, and lets the rest fall -->
							<span class="on-magnet" class:falls={v.locked && held === false} class:holds={v.locked && held === true}>
								<SortedThing {v} {item} group={pull.id} photo={material(item.text)?.key} />
								{#if v.locked && held != null}<small>{held ? 'melekat' : 'jatuh: tidak ditarik'}</small>{/if}
							</span>
						{/each}
					</div>
				</div>
			{/if}
			<div class="trays">
				{#each rest as g (g.id)}
					<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
					<div class="tray" data-zone={v.zone(g.id)} onclick={() => v.tapGroup(g.id)}>
						<h4>{#if g.sticker}<Sticker key={g.sticker} size={26} alt="" />{/if}{g.name}</h4>
						<div class="stuck">
							{#each v.inside(g.id) as item (item.id)}<SortedThing {v} {item} group={g.id} photo={material(item.text)?.key} />{/each}
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/snippet}
</SortPlay>

<style>
	/* the real picture of a horseshoe magnet's field */
	.magnet {
		display: block;
		width: min(100%, 15rem);
		margin: 0 auto 0.3rem;
		overflow: hidden;
		border-radius: 0.8rem;
		background: #fff;
		box-shadow: 0 4px 10px rgb(0 0 0 / 0.18);
	}
	.magnet :global(img) {
		width: 100%;
	}
	.on-magnet {
		display: inline-grid;
		justify-items: center;
		gap: 0.1rem;
		transition:
			transform 0.5s cubic-bezier(0.4, 0, 0.8, 0.4),
			opacity 0.5s;
	}
	.on-magnet small {
		padding: 0 0.4rem;
		border-radius: 999px;
		background: #e7f6ec;
		color: #17613f;
		font: 800 0.66rem/1.5 var(--font-body);
	}
	.on-magnet.falls {
		transform: translateY(0.9rem) rotate(7deg);
		opacity: 0.75;
	}
	.on-magnet.falls small {
		background: #eef0f3;
		color: #55606e;
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
	@media (prefers-reduced-motion: reduce) {
		.on-magnet {
			transition: none;
		}
	}
	.lab {
		display: grid;
		gap: 0.6rem;
		padding: 0.7rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #eef3f8, #dfe7ef);
		box-shadow: inset 0 0 0 3px #c4d2df;
	}
	.field {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		min-height: 11rem;
		padding: 0.4rem;
		border: 2px dashed #9fb3c7;
		border-radius: var(--r-lg);
		background: radial-gradient(circle at 50% 30%, #ffffff, #e9f0f6 70%);
	}
	.field:global(.zone-hover) {
		border-color: #d33a2c;
		box-shadow: 0 0 0 4px rgb(211 58 44 / 0.15);
	}
	h4 {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		color: #2a3340;
		font: 700 1rem var(--font-display);
	}
	.stuck {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.35rem;
		min-height: 2.6rem;
	}
	.trays {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
		gap: 0.5rem;
	}
	.tray {
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		min-height: 6rem;
		padding: 0.5rem;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #c9b08a, #a88a5c);
		box-shadow:
			inset 0 6px 10px rgb(0 0 0 / 0.2),
			0 3px 0 #7c6236;
	}
	.tray h4 {
		color: #fff;
		text-shadow: 0 1px 2px rgb(0 0 0 / 0.35);
	}
	.tray:global(.zone-hover) {
		outline: 3px solid #f0a400;
	}
	@keyframes flow {
		to {
			stroke-dashoffset: -16;
		}
	}
	@keyframes buzz {
		50% {
			translate: 1px 0;
		}
	}
</style>
