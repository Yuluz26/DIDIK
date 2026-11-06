<!--
	Neraca Amal: a brass balance with a pan for each of the first two groups (pahala and dosa, wajib and
	haram...), and a box for a third. The beam tips towards the pan holding more as things are put on.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import SortPlay, { type SortView } from '../SortPlay.svelte';
	import SortedThing from '../SortedThing.svelte';
	import type { GameProps } from '../kit.svelte';

	let p: GameProps = $props();
</script>

<SortPlay {p} pool="Perbuatan" tip="Letak setiap perbuatan di piring yang betul.">
	{#snippet board(v: SortView)}
		{@const [a, b, ...rest] = v.groups}
		{@const tilt = a && b ? Math.max(-12, Math.min(12, (v.inside(b.id).length - v.inside(a.id).length) * 4)) : 0}
		<div class="stand">
			<div class="beam" style:--tilt="{tilt}deg">
				{#each [a, b] as g, side (side)}
					{#if g}
						<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
						<div class="hang {side ? 'right' : 'left'}" style:--tilt="{-tilt}deg">
							<span class="chains" aria-hidden="true"></span>
							<div class="pan" data-zone={v.zone(g.id)} onclick={() => v.tapGroup(g.id)}>
								<h4>{#if g.sticker}<Sticker key={g.sticker} size={22} alt="" />{/if}{g.name}</h4>
								<div class="load">
									{#each v.inside(g.id) as item (item.id)}<SortedThing {v} {item} group={g.id} size={22} />{/each}
								</div>
							</div>
						</div>
					{/if}
				{/each}
			</div>
			<div class="post" aria-hidden="true"><span class="cap"></span></div>
			{#each rest as g (g.id)}
				<!-- svelte-ignore a11y_click_events_have_key_events, a11y_no_static_element_interactions -->
				<div class="box" data-zone={v.zone(g.id)} onclick={() => v.tapGroup(g.id)}>
					<h4>{g.name}</h4>
					<div class="load">{#each v.inside(g.id) as item (item.id)}<SortedThing {v} {item} group={g.id} size={22} />{/each}</div>
				</div>
			{/each}
		</div>
	{/snippet}
</SortPlay>

<style>
	.stand {
		position: relative;
		display: grid;
		justify-items: center;
		gap: 0.4rem;
		padding: 1rem 0.5rem 0.8rem;
		border-radius: var(--r-lg);
		background: radial-gradient(circle at 50% 20%, #fff8e4, #f1e2bd 70%);
		box-shadow: inset 0 0 0 3px #d9bf85;
	}
	.beam {
		position: relative;
		z-index: 1;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.4rem;
		width: 100%;
		padding-top: 0.6rem;
		border-top: 8px solid #b8892c;
		border-radius: 6px;
		rotate: var(--tilt);
		transition: rotate 0.6s var(--spring, ease-out);
	}
	.hang {
		display: grid;
		justify-items: center;
		rotate: var(--tilt);
		transition: rotate 0.6s var(--spring, ease-out);
		transform-origin: 50% 0;
	}
	.chains {
		width: 70%;
		height: 1.4rem;
		margin-top: -0.6rem;
		border: 2px solid #9a7426;
		border-bottom: 0;
		clip-path: polygon(50% 0, 100% 100%, 0 100%);
		background: transparent;
	}
	.pan {
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		width: 100%;
		min-height: 7.5rem;
		padding: 0.4rem 0.3rem 0.6rem;
		border-radius: 0 0 50% 50% / 0 0 34% 34%;
		background: linear-gradient(180deg, #f7d77a, #d9a83a);
		box-shadow:
			inset 0 -6px 0 rgb(120 80 10 / 0.2),
			0 6px 10px rgb(120 80 10 / 0.25);
	}
	.pan:global(.zone-hover) {
		box-shadow: 0 0 0 4px rgb(255 255 255 / 0.8);
	}
	h4 {
		display: inline-flex;
		align-items: center;
		gap: 0.2rem;
		color: #4a3205;
		font: 700 0.95rem/1.1 var(--font-display);
		text-align: center;
	}
	.load {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 0.25rem;
	}
	.post {
		position: absolute;
		left: 50%;
		top: 0.7rem;
		bottom: 0.6rem;
		width: 10px;
		translate: -50% 0;
		border-radius: 5px;
		background: linear-gradient(90deg, #8a6418, #d9a83a, #8a6418);
	}
	.cap {
		position: absolute;
		left: 50%;
		top: -0.6rem;
		width: 1.4rem;
		height: 1.4rem;
		translate: -50% 0;
		border-radius: 50%;
		background: radial-gradient(circle at 35% 30%, #ffe9a6, #b8892c);
	}
	.box {
		position: relative;
		z-index: 1;
		display: grid;
		justify-items: center;
		gap: 0.3rem;
		width: 100%;
		min-height: 4.5rem;
		padding: 0.4rem;
		border-radius: 10px;
		background: #fffdf5;
		border: 2px dashed #d9bf85;
	}
	@media (prefers-reduced-motion: reduce) {
		.beam,
		.hang {
			transition: none;
		}
	}
</style>
