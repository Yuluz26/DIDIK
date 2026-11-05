<!--
	Didi's cloud trail: one stop for each question, coloured by the stars it earned, with Didi riding to
	the stop the child is at and a gift waiting at the end. A long trail (more than 15 questions) is a bar
	without stops.
-->
<script lang="ts">
	import Sticker from '$ui/Sticker.svelte';
	import DidiSoft from './DidiSoft.svelte';

	let { total, stars, done = false }: { total: number; stars: number[]; done?: boolean } = $props();

	const at = $derived(Math.min(stars.length, total));
	const shownAt = $derived(done ? total : Math.min(at + 1, total));
	// Didi stands on the stop being answered; at the end, on the gift
	const pct = $derived(total <= 1 ? (done ? 100 : 0) : done ? 100 : (at / (total - 1)) * 100);
	const stops = $derived(total <= 15);
</script>

<div class="trail" role="progressbar" aria-valuemin={0} aria-valuemax={total} aria-valuenow={at} aria-label="Soalan {shownAt} daripada {total}">
	<div class="lane">
		<div class="track"><div class="fill" style:width="{pct}%"></div></div>
		{#if stops}
			<ol class="stops">
				{#each Array.from({ length: total }, (_, i) => i) as i (i)}
					<li class="stop s{stars[i] ?? 'x'}" class:now={!done && i === at} style:left="{total <= 1 ? 0 : (i / (total - 1)) * 100}%"></li>
				{/each}
			</ol>
		{/if}
		<span class="rider" style:left="{pct}%"><DidiSoft size={34} mood={done ? 'cheer' : 'happy'} /></span>
		<span class="gift" class:open={done}><Sticker key="hadiah" size={30} alt="" eager /></span>
	</div>
</div>

<style>
	.trail {
		width: 100%;
		padding: 0 1.4rem 0 0.6rem;
	}
	.lane {
		position: relative;
		height: 2.9rem;
	}
	.track {
		position: absolute;
		left: 0;
		right: 0;
		top: 1.9rem;
		height: 0.6rem;
		border-radius: 999px;
		background: rgb(255 255 255 / 0.75);
		box-shadow: inset 0 2px 0 rgb(120 90 170 / 0.15);
	}
	.fill {
		height: 100%;
		border-radius: inherit;
		background: linear-gradient(90deg, #ff9fc3, #ffcf6e, #8fe0b0);
		transition: width 700ms cubic-bezier(0.34, 1.56, 0.64, 1);
	}
	.stops {
		position: absolute;
		left: 0;
		right: 0;
		top: 1.9rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.stop {
		position: absolute;
		top: 50%;
		width: 0.95rem;
		height: 0.95rem;
		border: 3px solid #fff;
		border-radius: 50%;
		background: #e5dcf3;
		transform: translate(-50%, -50%);
		box-shadow: 0 2px 0 rgb(120 90 170 / 0.2);
	}
	.stop.s3 {
		background: #ffc93c;
	}
	.stop.s2 {
		background: #ff9fc3;
	}
	.stop.s1 {
		background: #9fd0ff;
	}
	.stop.s0 {
		background: #cfc6dd;
	}
	.stop.now {
		width: 1.2rem;
		height: 1.2rem;
		background: #fff;
		border-color: #b98cff;
		animation: pulse-stop 1.4s ease-in-out infinite;
	}
	.rider {
		position: absolute;
		top: -0.35rem;
		transform: translateX(-50%);
		transition: left 700ms cubic-bezier(0.34, 1.56, 0.64, 1);
		filter: drop-shadow(0 2px 2px rgb(60 40 90 / 0.2));
	}
	.gift {
		position: absolute;
		right: -1.5rem;
		top: 0.95rem;
	}
	.gift.open {
		animation: pop-in 520ms var(--spring) both;
	}
	@keyframes pulse-stop {
		50% {
			box-shadow: 0 0 0 6px rgb(185 140 255 / 0.25);
		}
	}
</style>
