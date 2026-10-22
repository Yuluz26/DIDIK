<!--
	A child's way in: a paper ticket with the room code written on it and a stub to tear off (Masuk).
	Didi peeks over the top, watches the pointer, waves while you are at the ticket and cheers when six
	digits are in. A code that cannot be right shakes the ticket and says what a code looks like.
-->
<script lang="ts">
	import { goto } from '$app/navigation';
	import { play } from '$lib/sound';
	import Didi from '$ui/Didi.svelte';
	import Icon from '$ui/Icon.svelte';

	let code = $state('');
	let problem = $state('');
	let shaking = $state(false);
	let near = $state(false);
	let look = $state<{ x: number; y: number } | null>(null);
	let didiEl = $state<HTMLElement>();
	let input = $state<HTMLInputElement>();

	const digits = $derived(code.replace(/\D/g, '').length);
	const mood = $derived(problem ? 'hint' : digits === 6 ? 'cheer' : near ? 'wave' : 'happy');

	/** Puts the cursor in the code box, e.g. from the small ticket that follows the page down. */
	export function focus() {
		input?.focus({ preventScroll: true });
	}

	function enter(event: Event) {
		event.preventDefault();
		const key = code.trim().toLowerCase().replace(/\s+/g, '');
		const fromLink = key.match(/\/m\/([a-z0-9-]+)/)?.[1];
		const target = fromLink ?? key;
		if (!/^(\d{6}|[a-z]+-[a-z]+-\d{2})$/.test(target)) {
			problem = 'Kod bilik ada 6 digit, contohnya 482 913.';
			shaking = true;
			setTimeout(() => (shaking = false), 500);
			input?.focus();
			return;
		}
		play('pop');
		void goto(`/m/${target}`);
	}

	// Didi's eyes follow the pointer wherever it is on the page.
	function watch(event: PointerEvent) {
		if (!didiEl || event.pointerType === 'touch') return;
		const box = didiEl.getBoundingClientRect();
		const dx = event.clientX - (box.left + box.width / 2);
		const dy = event.clientY - (box.top + box.height * 0.4);
		const distance = Math.hypot(dx, dy) || 1;
		const reach = Math.min(1, distance / 240);
		look = { x: (dx / distance) * reach, y: (dy / distance) * reach };
	}
</script>

<svelte:window onpointermove={watch} />

<div class="ticket-wrap" class:shaking>
	<span class="didi" bind:this={didiEl} aria-hidden="true"><Didi {mood} size={92} {look} /></span>
	<form
		id="tiket"
		class="ticket"
		onsubmit={enter}
		novalidate
		onpointerenter={() => (near = true)}
		onpointerleave={() => (near = false)}
		onfocusin={() => (near = true)}
		onfocusout={() => (near = false)}
	>
		<div class="write">
			<label for="code">Kod bilik</label>
			<input
				bind:this={input}
				id="code"
				bind:value={code}
				inputmode="numeric"
				autocomplete="off"
				maxlength="40"
				placeholder="000 000"
				aria-describedby={problem ? 'code-problem' : 'code-help'}
				aria-invalid={!!problem}
				oninput={() => (problem = '')}
			/>
		</div>
		<div class="stub">
			<button class="btn btn--sun btn--big go">Masuk <span class="arrow"><Icon name="next" /></span></button>
		</div>
	</form>
</div>
{#if problem}
	<p id="code-problem" class="field-error problem">{problem}</p>
{:else}
	<p id="code-help" class="help-line">Kod ada pada skrin ibu bapa atau cikgu. Pautan bilik pun boleh ditampal di sini.</p>
{/if}

<style>
	.ticket-wrap {
		position: relative;
		max-width: 31rem;
		margin-top: 4.2rem;
		transition: transform 420ms var(--spring);
	}
	.ticket-wrap:hover,
	.ticket-wrap:focus-within {
		transform: rotate(-1.2deg) translateY(-2px);
	}
	.shaking {
		animation: shake 420ms ease-in-out;
	}
	/* Didi stands behind the ticket, so only the head and a waving paw show over its edge. */
	.didi {
		position: absolute;
		z-index: 0;
		right: 7.5rem;
		bottom: calc(100% - 2.6rem);
		line-height: 0;
		transition: transform 420ms var(--spring);
	}
	.ticket-wrap:hover .didi,
	.ticket-wrap:focus-within .didi {
		transform: translateY(-6px);
	}
	.ticket {
		--notch: 13px;
		--stub: 9.6rem;
		position: relative;
		z-index: 1;
		display: grid;
		grid-template-columns: minmax(0, 1fr) var(--stub);
		align-items: center;
		min-height: 6.4rem;
		border-radius: var(--r-md);
		background: var(--paper);
		/* Two half-moons bitten out where the stub tears off. */
		mask:
			radial-gradient(circle var(--notch) at calc(100% - var(--stub)) 0, #0000 97%, #000) top / 100% 51% no-repeat, /* taste-skill-ignore: mask */
			radial-gradient(circle var(--notch) at calc(100% - var(--stub)) 100%, #0000 97%, #000) bottom / 100% 51% no-repeat; /* taste-skill-ignore: mask */
	}
	.write {
		display: grid;
		gap: 0.1rem;
		padding: 0.8rem 1.1rem 0.9rem 1.3rem;
	}
	label {
		font-weight: 800;
		color: var(--ink-2);
	}
	input {
		width: 100%;
		min-width: 0;
		padding: 0.1rem 0 0.2rem;
		border: 0;
		border-bottom: 3px solid var(--line);
		background: transparent;
		color: var(--ink);
		font: 600 clamp(1.6rem, 1.2rem + 1.2vw, 2.1rem) / 1.2 var(--font-display);
		letter-spacing: 0.08em;
		font-variant-numeric: tabular-nums;
		transition: border-color var(--t-state);
	}
	input::placeholder {
		color: #cbbd9f;
	}
	input:focus {
		outline: none;
		border-bottom-color: var(--sea);
	}
	input[aria-invalid='true'] {
		border-bottom-color: var(--almost);
	}
	/* The perforation: a column of round holes between the ticket and its stub. */
	.stub {
		display: grid;
		place-items: center;
		align-self: stretch;
		padding: 0 0.8rem;
		border-left: 4px dotted #d9cbb0;
	}
	.go {
		width: 100%;
		gap: 0.3em;
		padding-inline: 0.6em;
	}
	.arrow {
		display: inline-flex;
		transition: transform var(--t-state) var(--spring);
	}
	.go:hover .arrow {
		transform: translateX(4px);
	}
	.help-line,
	.problem {
		margin-top: 0.7rem;
		max-width: 31rem;
	}
	.help-line {
		color: var(--on-sea);
		font-weight: 700;
	}
	.problem {
		display: inline-block;
		padding: 0.25rem 0.7rem;
		border-radius: var(--r-sm);
		background: var(--paper);
	}
	@media (max-width: 420px) {
		.ticket {
			--stub: 8.2rem;
		}
		.go {
			font-size: 1.15rem;
		}
		.didi {
			right: 5.8rem;
		}
		.didi :global(svg) {
			--didi-w: 80px;
		}
	}
</style>
