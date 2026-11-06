<!--
	Kurator Muzium: a gallery of glass display cases on wooden plinths under spotlights, one case for each
	era (group). Put each artefact in the case of its time.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import SortPlay, { type SortView } from '../SortPlay.svelte';
	import SortedThing from '../SortedThing.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();
</script>

<SortPlay {p} pool="Artifak baharu tiba" tip="Pamerkan setiap artifak dalam almari zaman yang betul.">
	{#snippet board(v: SortView)}
		<div class="gallery" style:--n={v.groups.length}>
			{#each v.groups as g, i (g.id)}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div class="case" data-zone={v.zone(g.id)} onclick={() => v.tapGroup(g.id)}>
					<span class="light" aria-hidden="true"></span>
					<div class="glass">
						{#each v.inside(g.id) as item (item.id)}<SortedThing {v} {item} group={g.id} size={34} />{/each}
					</div>
					<div class="plinth">
						{#if g.sticker}<Sticker key={g.sticker} size={26} alt="" />{/if}
						<span>{g.name}</span>
						<small>Galeri {String.fromCharCode(65 + i)}</small>
					</div>
				</div>
			{/each}
		</div>
	{/snippet}
</SortPlay>

<style>
	.gallery {
		display: grid;
		grid-template-columns: repeat(var(--n), minmax(0, 1fr));
		gap: 0.6rem;
		padding: 0.8rem 0.6rem;
		border-radius: var(--r-lg);
		background:
			linear-gradient(180deg, #2c2420 0%, #3d322b 55%, #6b5240 55.5%, #5a4535 100%);
		box-shadow: inset 0 0 0 3px #1d1714;
	}
	.case {
		position: relative;
		display: grid;
		grid-template-rows: 1fr auto;
		min-height: 13rem;
	}
	.light {
		position: absolute;
		left: 50%;
		top: -0.8rem;
		width: 100%;
		height: 70%;
		translate: -50% 0;
		background: radial-gradient(ellipse at 50% 0%, rgb(255 236 180 / 0.35), transparent 70%);
		pointer-events: none;
	}
	.glass {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		align-content: flex-start;
		justify-content: center;
		gap: 0.35rem;
		padding: 0.6rem 0.3rem;
		border: 2px solid rgb(220 235 245 / 0.65);
		border-bottom: 0;
		border-radius: 8px 8px 0 0;
		background: linear-gradient(120deg, rgb(255 255 255 / 0.22), rgb(200 225 240 / 0.08) 45%, rgb(255 255 255 / 0.18));
	}
	.case:global(.zone-hover) .glass {
		border-color: #ffd36b;
		box-shadow: inset 0 0 20px rgb(255 211 107 / 0.35);
	}
	.plinth {
		display: grid;
		justify-items: center;
		gap: 0.05rem;
		padding: 0.35rem 0.2rem;
		border-radius: 0 0 6px 6px;
		background: linear-gradient(180deg, #a0784f, #7b5735);
		box-shadow: inset 0 3px 0 rgb(255 255 255 / 0.15);
		color: #fff7e6;
		font: 700 0.9rem/1.1 var(--font-display);
		text-align: center;
	}
	.plinth small {
		color: #e9cfa5;
		font: 700 0.65rem var(--font-body);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}
</style>
