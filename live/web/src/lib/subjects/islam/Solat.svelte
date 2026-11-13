<!--
	Gerakan Solat: a prayer mat with its mihrab arch at the head, and a place for each step down its length.
	A step put in place shows its position (berdiri, takbir, rukuk, iktidal, sujud, duduk, salam) as a plain
	figure with no face.
-->
<script lang="ts">
	import Mark from '../Mark.svelte';
	import OrderPlay, { type OrderView } from '../OrderPlay.svelte';
	import type { GameProps } from '../kit.svelte';
	import Pose, { poseOf } from './Pose.svelte';

	let p: GameProps = $props();
	import GameImage from '../GameImage.svelte';
	import { asset } from '../assets';
	const RUG = asset('isl/rug');
</script>

<OrderPlay {p} pic={() => undefined} pool="Gerakan" tip="Mula dari kepala sejadah. Ketik atau seret ke tempatnya.">
	{#snippet board(v: OrderView)}
		<div class="mat" style:--rug={RUG ? `url(${RUG.src})` : 'none'}>
			<span class="mihrab" aria-hidden="true"><GameImage name="isl/mihrab" eager fit="cover">{#snippet fallback()}<span class="arch"><span></span></span>{/snippet}</GameImage></span>
			<ol class="steps">
				{#each v.slots as id, i (i)}
					{@const ok = v.ok(i)}
					<li class="step" class:filled={!!id} data-zone={v.zone(i)}>
						<span class="n">{i + 1}</span>
						{#if id}
							<button type="button" class="move" disabled={v.locked} {@attach v.grab(i)} aria-label="{v.text(id)}, gerakan {i + 1}">
								<Pose kind={poseOf(v.text(id))} size={46} />
								<span>{v.text(id)}</span>
								{#if ok !== null}<Mark {ok} />{/if}
							</button>
							{#if v.should(i)}<span class="should">→ {v.should(i)}</span>{/if}
						{:else}
							<span class="empty">Gerakan {i + 1}</span>
						{/if}
					</li>
				{/each}
			</ol>
			<div class="fringe" aria-hidden="true"></div>
		</div>
	{/snippet}
</OrderPlay>

<style>
	.mat {
		background-image: linear-gradient(rgb(120 20 30 / 0.55), rgb(90 14 24 / 0.65)), var(--rug) !important;
		background-size: cover !important;
		background-position: center !important;
	}
	.mihrab {
		display: block;
		width: 5rem;
		height: 6rem;
		margin: 0 auto 0.5rem;
		overflow: hidden;
		border: 3px solid #e8c25a;
		border-radius: 2.5rem 2.5rem 0.4rem 0.4rem;
		box-shadow: 0 4px 10px rgb(0 0 0 / 0.4);
	}
	.mihrab :global(img.g-img) {
		width: 100%;
		height: 100%;
	}
	.mat {
		position: relative;
		width: min(100%, 26rem);
		margin-inline: auto;
		padding: 0.8rem 0.9rem 1.4rem;
		border-radius: 0.8rem 0.8rem 0.3rem 0.3rem;
		background:
			repeating-linear-gradient(45deg, rgb(255 255 255 / 0.04) 0 6px, transparent 6px 12px),
			linear-gradient(180deg, #7a1f2b, #5c1520);
		box-shadow:
			inset 0 0 0 4px #c9a13b,
			inset 0 0 0 8px #7a1f2b,
			inset 0 0 0 10px #e6c46a,
			0 10px 20px rgb(60 10 20 / 0.3);
	}
	.arch {
		display: grid;
		place-items: center;
		height: 4.2rem;
		margin: 0.3rem auto 0.6rem;
		width: 60%;
	}
	.arch span {
		width: 100%;
		height: 100%;
		border: 4px solid #e6c46a;
		border-bottom: 0;
		border-radius: 50% 50% 0 0 / 70% 70% 0 0;
		background: radial-gradient(circle at 50% 80%, #2d5d4f, #173a31);
		box-shadow: inset 0 0 0 4px #7a1f2b;
	}
	.steps {
		display: grid;
		gap: 0.45rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.step {
		position: relative;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.4rem;
		min-height: 3.6rem;
		padding: 0.3rem 0.5rem 0.3rem 2.2rem;
		border: 2px dashed rgb(230 196 106 / 0.6);
		border-radius: 10px;
	}
	.step.filled {
		border-style: solid;
		border-color: #e6c46a;
		background: #fbf3df;
	}
	.step:global(.zone-hover) {
		background: rgb(230 196 106 / 0.3);
	}
	.n {
		position: absolute;
		left: 0.5rem;
		top: 50%;
		translate: 0 -50%;
		display: grid;
		place-items: center;
		width: 1.4rem;
		height: 1.4rem;
		border-radius: 50%;
		background: #e6c46a;
		color: #5c1520;
		font: 700 0.78rem var(--font-display);
	}
	.move {
		position: relative;
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0;
		border: 0;
		background: transparent;
		color: #3a1606;
		font: 700 0.98rem/1.15 var(--font-body);
		text-align: left;
		cursor: grab;
		touch-action: none;
	}
	.move:disabled {
		cursor: default;
	}
	.empty {
		color: rgb(250 225 160 / 0.8);
		font-weight: 700;
		font-size: 0.88rem;
	}
	.should {
		color: #8a2a00;
		font-weight: 800;
		font-size: 0.82rem;
	}
	.fringe {
		position: absolute;
		left: 6%;
		right: 6%;
		bottom: -0.5rem;
		height: 0.7rem;
		background: repeating-linear-gradient(90deg, #e6c46a 0 2px, transparent 2px 6px);
	}
</style>
