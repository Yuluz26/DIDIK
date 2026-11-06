<!--
	Label rajah's editor: choose a diagram or photo, then tap on it to put a numbered place where a label
	goes, and write each label. A diagram made for labelling offers its usual places with one tap.
	Places are kept a little apart, so a child can tell them apart on a phone.
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import { DIAGRAMS, diagramOf, diagramUrl } from '$lib/diagrams';
	import { LIMITS, make, suggestedSpots, type Question } from './model';

	type Diagram = Extract<Question, { type: 'diagram' }>;
	let { question = $bindable(), err }: { question: Diagram; err: (...path: (string | number)[]) => string | undefined } = $props();

	const d = $derived(diagramOf(question.diagram));
	const unused = $derived((d?.spots ?? []).filter((s) => !question.spots.some((q) => q.label.trim().toLowerCase() === s.label.toLowerCase())));

	function choose(key: string) {
		question.diagram = key;
		question.spots = suggestedSpots(key, 4);
		if (!question.spots.length) question.spots = [];
	}
	function addAt(event: MouseEvent) {
		if (question.spots.length >= LIMITS.spots) return;
		const box = (event.currentTarget as HTMLElement).getBoundingClientRect();
		const x = Math.round(((event.clientX - box.left) / box.width) * 1000) / 10;
		const y = Math.round(((event.clientY - box.top) / box.height) * 1000) / 10;
		question.spots = [...question.spots, make.spot(x, y)];
	}
	function addSuggested(s: { x: number; y: number; label: string }) {
		if (question.spots.length >= LIMITS.spots) return;
		question.spots = [...question.spots, make.spot(s.x, s.y, s.label)];
	}
	const remove = (id: string) => (question.spots = question.spots.filter((s) => s.id !== id));
</script>

<div class="diagram-ed">
	<fieldset class="choose">
		<legend>Rajah</legend>
		<div class="strip">
			{#each DIAGRAMS as option (option.key)}
				<button type="button" class="opt" aria-pressed={question.diagram === option.key} onclick={() => choose(option.key)} title={option.name}>
					<img src={diagramUrl(option.key)} alt="" loading="lazy" />
					<span>{option.name}</span>
				</button>
			{/each}
		</div>
		{#if err('diagram')}<span class="field-error">{err('diagram')}</span>{/if}
	</fieldset>

	{#if d}
		<div class="place">
			<p class="help">Ketik pada rajah untuk menambah tempat label ({question.spots.length}/{LIMITS.spots}).</p>
			<button type="button" class="canvas" style:aspect-ratio="{d.w} / {d.h}" onclick={addAt} aria-label="Ketik untuk menambah tempat label">
				<img src={diagramUrl(d.key)} alt={d.name} />
				{#each question.spots as s, i (s.id)}
					<span class="pin" style:left="{s.x}%" style:top="{s.y}%">{i + 1}</span>
				{/each}
			</button>
			{#if unused.length && question.spots.length < LIMITS.spots}
				<div class="ideas">
					<span>Tempat biasa:</span>
					{#each unused as s (s.label)}<button type="button" class="chip" onclick={() => addSuggested(s)}>+ {s.label}</button>{/each}
				</div>
			{/if}
		</div>
		<ol class="labels">
			{#each question.spots as s, i (s.id)}
				<li>
					<span class="n">{i + 1}</span>
					<input class="input" bind:value={s.label} maxlength="40" placeholder="Label tempat {i + 1}" aria-label="Label tempat {i + 1}" aria-invalid={!!err('spots', i, 'label')} />
					<button type="button" class="tool" onclick={() => remove(s.id)} disabled={question.spots.length <= 2} aria-label="Buang tempat {i + 1}"><Icon name="trash" size={18} /></button>
				</li>
			{/each}
		</ol>
		{#if err('spots')}<span class="field-error">{err('spots')}</span>{/if}
	{/if}
</div>

<style>
	.diagram-ed {
		display: grid;
		gap: 0.8rem;
	}
	.choose {
		margin: 0;
		padding: 0;
		border: 0;
		min-width: 0;
	}
	.choose legend {
		margin-bottom: 0.4rem;
		padding: 0;
		font-weight: 800;
		font-size: 0.95rem;
	}
	.strip {
		display: flex;
		gap: 0.4rem;
		overflow-x: auto;
		padding-bottom: 0.3rem;
	}
	.opt {
		display: grid;
		justify-items: center;
		gap: 0.2rem;
		flex: none;
		width: 6.4rem;
		padding: 0.3rem;
		border: 2px solid var(--line);
		border-radius: var(--r-md);
		background: #fff;
		color: var(--ink);
		font-size: 0.72rem;
		font-weight: 700;
		line-height: 1.15;
		text-align: center;
		cursor: pointer;
	}
	.opt img {
		width: 100%;
		height: 3.6rem;
		object-fit: contain;
	}
	.opt[aria-pressed='true'] {
		border-color: var(--brand);
		background: var(--brand-soft, #e5f6ec);
	}
	.place {
		display: grid;
		gap: 0.4rem;
		justify-items: center;
	}
	.canvas {
		position: relative;
		width: min(100%, 26rem);
		padding: 0;
		border: 2px dashed var(--line);
		border-radius: var(--r-md);
		background: #fff;
		cursor: crosshair;
	}
	.canvas img {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: contain;
		pointer-events: none;
	}
	.pin {
		position: absolute;
		display: grid;
		place-items: center;
		width: 1.8rem;
		height: 1.8rem;
		translate: -50% -50%;
		border: 3px solid #fff;
		border-radius: 50%;
		background: var(--berry, #e0457b);
		color: #fff;
		font: 700 0.85rem var(--font-display);
		box-shadow: 0 2px 6px rgb(0 0 0 / 0.3);
		pointer-events: none;
	}
	.ideas {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.3rem;
		font-size: 0.85rem;
		font-weight: 700;
	}
	.chip {
		padding: 0.2rem 0.6rem;
		border: 0;
		border-radius: 999px;
		background: #fff7d6;
		font-weight: 800;
		cursor: pointer;
	}
	.labels {
		display: grid;
		gap: 0.4rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	.labels li {
		display: flex;
		align-items: center;
		gap: 0.4rem;
	}
	.n {
		display: grid;
		place-items: center;
		flex: none;
		width: 1.8rem;
		height: 1.8rem;
		border-radius: 50%;
		background: var(--berry, #e0457b);
		color: #fff;
		font: 700 0.85rem var(--font-display);
	}
	.tool {
		display: grid;
		place-items: center;
		width: 2.6rem;
		height: 2.6rem;
		border: 0;
		border-radius: 50%;
		background: transparent;
		cursor: pointer;
	}
</style>
