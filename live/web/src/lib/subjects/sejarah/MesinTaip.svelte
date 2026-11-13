<!--
	Mesin Taip Merdeka: an old typewriter with a sheet of paper in its roller. Type the answer (the keyboard
	clacks); it appears on the paper in typewriter letters. Semak "sends the telegram".
-->
<script lang="ts">
	import { play } from '$lib/sound';
	import Checks from '../Checks.svelte';
	import Mark from '../Mark.svelte';
	import { type GameProps, isLocked } from '../kit.svelte';

	let p: GameProps = $props();

	const locked = $derived(isLocked(p));
	let typed = $state('');
	const shown = $derived<string>(p.mine !== undefined ? String(p.mine) : p.reveal ? String(p.reveal.correct) : typed);
	const right = $derived<string | null>(p.reveal ? String(p.reveal.correct) : null);
	const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9À-ɏ]+/g, ' ').trim();
	const ok = $derived(right !== null ? [right, ...(p.reveal?.accepted ?? [])].some((a) => norm(a) === norm(shown)) : null);
	const max = $derived(p.question.maxLength ?? 60);
	import GameImage from '../GameImage.svelte';
</script>

<div class="typewriter">
	<div class="paper">
		<p class="head">TELEGRAM · {new Date().getFullYear()}</p>
		<p class="line">{shown}<span class="caret" class:hide={locked}>▌</span></p>
		{#if ok !== null}<span class="mark"><Mark {ok} size={16} /></span>{/if}
	</div>
	<div class="roller" aria-hidden="true"></div>
	<!-- a real Underwood typewriter; a key bar jumps as each letter is typed -->
	<span class="machine" class:strike={!!typed && !locked} aria-hidden="true">
		{#key typed.length}<GameImage name="hist/typewriter" eager>
			{#snippet fallback()}
				<span class="body">
					{#each ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM'] as row (row)}
						<span class="keys">{#each row.split('') as k (k)}<span class="key">{k}</span>{/each}</span>
					{/each}
				</span>
			{/snippet}
		</GameImage>{/key}
	</span>
</div>
{#if ok === false && right}<p class="should">Jawapan: <strong>{right}</strong></p>{/if}
{#if !locked}
	<label class="field">
		<span>Taip jawapan kamu</span>
		<input
			class="input"
			type="text"
			maxlength={max}
			value={typed}
			autocomplete="off"
			autocapitalize="off"
			spellcheck="false"
			oninput={(e) => {
				typed = (e.currentTarget as HTMLInputElement).value;
				play('tap');
			}}
			onkeydown={(e) => e.key === 'Enter' && typed.trim() && p.onanswer?.(typed.trim())}
		/>
	</label>
	<Checks tip="" label="Hantar telegram" ready={!!typed.trim()} dirty={!!typed} onreset={() => (typed = '')} oncheck={() => p.onanswer?.(typed.trim())} />
{/if}

<style>
	.machine {
		display: block;
		width: min(100%, 22rem);
		margin: -0.9rem auto 0;
	}
	.machine :global(img) {
		width: 100%;
		filter: drop-shadow(0 8px 10px rgb(0 0 0 / 0.35));
	}
	.machine.strike :global(img) {
		animation: clack 0.12s ease-out;
	}
	@keyframes clack {
		50% {
			transform: translateY(2px);
		}
	}
	@media (prefers-reduced-motion: reduce) {
		.machine.strike :global(img) {
			animation: none;
		}
	}
	.typewriter {
		display: grid;
		justify-items: center;
		padding: 0.8rem 0.6rem 0;
		border-radius: var(--r-lg);
		background: linear-gradient(180deg, #e9e2d2, #d6ccb5);
		box-shadow: inset 0 0 0 3px #bfb196;
	}
	.paper {
		position: relative;
		width: min(90%, 24rem);
		min-height: 6rem;
		padding: 0.6rem 0.8rem;
		background: #fffdf6;
		box-shadow: 0 -2px 8px rgb(0 0 0 / 0.1);
	}
	.head {
		color: #8a2a2a;
		font: 700 0.7rem 'Courier New', monospace;
		letter-spacing: 0.12em;
	}
	.line {
		margin-top: 0.5rem;
		min-height: 1.6em;
		color: #1b1b1b;
		font: 700 1.35rem/1.4 'Courier New', 'Courier', monospace;
		overflow-wrap: anywhere;
	}
	.caret {
		animation: blink 1s steps(2) infinite;
	}
	.caret.hide {
		display: none;
	}
	.mark {
		position: absolute;
		right: 0.4rem;
		top: 0.4rem;
		width: 1.4rem;
		height: 1.4rem;
	}
	.roller {
		width: min(98%, 27rem);
		height: 1.1rem;
		border-radius: 0.6rem;
		background: linear-gradient(180deg, #2a2a2a, #555, #2a2a2a);
	}
	/* the keys are sized from the machine, ten across the top row */
	.body {
		container-type: inline-size;
		display: grid;
		gap: 0.3rem;
		justify-items: center;
		width: 100%;
		padding: 0.6rem 0.4rem 0.8rem;
		border-radius: 0 0 var(--r-lg) var(--r-lg);
		background: linear-gradient(180deg, #2f3b33, #1f2822);
	}
	.keys {
		display: flex;
		gap: min(0.25rem, 1.2cqi);
	}
	.key {
		display: grid;
		place-items: center;
		width: min(1.55rem, calc((100cqi - 9 * min(0.25rem, 1.2cqi)) / 10 - 1px));
		height: auto;
		aspect-ratio: 1;
		border-radius: 50%;
		background: radial-gradient(circle at 40% 35%, #fff, #d9d4c6);
		color: #222;
		font: 700 0.7rem 'Courier New', monospace;
		box-shadow:
			0 0 0 2px #8f8a7a,
			0 3px 0 #111;
	}
	.should {
		padding: 0.4rem 0.8rem;
		border-radius: var(--r-md);
		background: #fff1e6;
		color: #8a3b12;
		font-weight: 700;
	}
	.field {
		display: grid;
		gap: 0.3rem;
		font-weight: 800;
	}
	.input {
		font: 700 1.2rem 'Courier New', monospace;
	}
	@keyframes blink {
		50% {
			opacity: 0;
		}
	}
</style>
