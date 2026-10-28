<!--
	A dashboard stat card: a small title, one big number, a strip of mini bars and a little chip. The bars
	are real numbers (questions per quiz, players per room); what is missing is drawn as faint stubs so
	the strip keeps its shape.
-->
<script lang="ts">
	import NmIcon from './NmIcon.svelte';

	let {
		title,
		value,
		bars = [],
		tone = 'blue',
		chip
	}: {
		title: string;
		value: string;
		bars?: number[];
		tone?: 'blue' | 'purple' | 'pink';
		chip: { text: string; tone: 'blue' | 'green' | 'pink'; icon: string };
	} = $props();

	const SLOTS = 12;
	const shown = $derived(bars.slice(0, SLOTS));
	const top = $derived(Math.max(1, ...shown));
</script>

<article class="stat nm-card {tone}">
	<header>
		<h3>{title}</h3>
		<p class="value">{value}</p>
	</header>
	<footer>
		<div class="strip" aria-hidden="true">
			{#each Array(SLOTS) as _, i (i)}
				{#if i < shown.length}
					<i style:height="{28 + (shown[i] / top) * 72}%"></i>
				{:else}
					<i class="stub"></i>
				{/if}
			{/each}
		</div>
		<span class="chip-tag {chip.tone}"><NmIcon name={chip.icon} size={12} /> {chip.text}</span>
	</footer>
</article>

<style>
	.stat {
		display: flex;
		flex-direction: column;
		justify-content: space-between;
		gap: 1rem;
		min-width: 0;
		padding: 1.2rem 1.3rem 1.15rem;
	}
	header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 0.6rem;
	}
	h3 {
		font: 500 0.95rem/1.2 var(--font-display);
		color: var(--ink);
	}
	.value {
		font: 300 clamp(2rem, 1.5rem + 1.4vw, 2.7rem) / 1 var(--font-display);
		letter-spacing: -0.02em;
		color: var(--ink);
	}
	footer {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		gap: 0.8rem;
	}
	.strip {
		display: flex;
		align-items: flex-end;
		gap: 0.28rem;
		height: 1.9rem;
		min-width: 0;
		flex: 1;
	}
	.strip i {
		display: block;
		width: 0.28rem;
		border-radius: 999px;
		background: var(--c);
		box-shadow: 1px 2px 3px rgb(120 130 170 / 0.3);
	}
	.strip .stub {
		height: 22%;
		background: #d4d8e5;
		box-shadow: none;
	}
	.blue {
		--c: linear-gradient(180deg, #86adff, #4a78ee);
	}
	.purple {
		--c: linear-gradient(180deg, #b69cff, #7a55ee);
	}
	.pink {
		--c: linear-gradient(180deg, #ff9fc0, #f2487a);
	}
	.chip-tag {
		display: inline-flex;
		align-items: center;
		gap: 0.3rem;
		flex: none;
		padding: 0.22rem 0.6rem;
		border-radius: 999px;
		background: #eceef5;
		box-shadow: inset 2px 2px 4px rgb(163 172 198 / 0.4), inset -2px -2px 4px rgb(255 255 255 / 0.95);
		font: 600 0.74rem/1.2 var(--font-display);
		white-space: nowrap;
	}
	.chip-tag.blue {
		color: #2f5fd0;
	}
	.chip-tag.green {
		color: #0f8a6f;
	}
	.chip-tag.pink {
		color: #d2255f;
	}
</style>
