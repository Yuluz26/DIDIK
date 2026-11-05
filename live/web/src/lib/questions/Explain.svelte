<!--
	The question's explanation ("Kenapa?"), written by whoever wrote the quiz: shown with the right answer
	to a child who did not get it right, and on the host's screen at the reveal, so the class hears why.
-->
<script lang="ts">
	import { canSpeak, speak } from '$lib/speech';
	import Icon from '$ui/Icon.svelte';
	import Sticker from '$ui/Sticker.svelte';

	let { text }: { text: string } = $props();
</script>

<aside class="explain" aria-label="Penerangan">
	<span class="bulb" aria-hidden="true"><Sticker key="mentol" size={40} alt="" /></span>
	<div class="words">
		<p class="head">Kenapa begitu?</p>
		<p class="text">{text}</p>
	</div>
	{#if canSpeak()}
		<button type="button" class="hear" onclick={() => speak(text)} aria-label="Dengar penerangan"><Icon name="speak" size={18} /></button>
	{/if}
</aside>

<style>
	.explain {
		display: flex;
		align-items: flex-start;
		gap: 0.6rem;
		padding: 0.7rem 0.8rem;
		border: 2px solid #f4dc8a;
		border-radius: var(--r-md);
		background: #fffbe6;
		color: #4d3b00;
		text-align: left;
		animation: rise-in var(--t-enter) var(--ease-out) both;
	}
	.bulb {
		flex: none;
		animation: glow-bulb 2.4s ease-in-out infinite;
	}
	.words {
		flex: 1;
		min-width: 0;
	}
	.head {
		font: 600 0.95rem var(--font-display);
		color: #8a6400;
	}
	.text {
		font-weight: 700;
		line-height: 1.45;
		overflow-wrap: break-word;
	}
	.hear {
		display: grid;
		place-items: center;
		flex: none;
		width: 2.75rem;
		height: 2.75rem;
		border: 0;
		border-radius: 50%;
		background: #fff;
		color: #8a6400;
		box-shadow: 0 2px 0 #f4dc8a;
		cursor: pointer;
	}
	@keyframes glow-bulb {
		50% {
			filter: drop-shadow(0 0 8px rgb(255 214 80 / 0.9));
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.bulb {
			animation: none;
		}
	}
</style>
