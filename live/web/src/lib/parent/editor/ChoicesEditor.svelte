<!--
	Options for Pilihan tunggal and Pilih semua: each with its text and whether it is right. One
	question allows one right option (round marks); the other allows several (square marks).
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import { LIMITS, make, type Choice } from './model';

	let {
		choices = $bindable(),
		multiple = false,
		name,
		err
	}: { choices: Choice[]; multiple?: boolean; name: string; err: (...path: (string | number)[]) => string | undefined } = $props();

	const min = $derived(multiple ? 3 : 2);

	function mark(index: number, value: boolean) {
		if (multiple) choices[index].correct = value;
		else choices.forEach((c, i) => (c.correct = i === index));
	}
</script>

<fieldset class="choices">
	<legend>{multiple ? 'Pilihan jawapan: tandakan semua yang betul' : 'Pilihan jawapan: tandakan yang betul'}</legend>
	<ol>
		{#each choices as choice, i (choice.id)}
			<li class:right={choice.correct}>
				<label class="mark" title={choice.correct ? 'Jawapan betul' : 'Tandakan sebagai betul'}>
					<input
						type={multiple ? 'checkbox' : 'radio'}
						{name}
						checked={choice.correct}
						onchange={(e) => mark(i, (e.currentTarget as HTMLInputElement).checked)}
						aria-label="Pilihan {i + 1} betul"
					/>
					<span class="box" class:square={multiple}><Icon name="check" size={16} /></span>
				</label>
				<input
					class="input"
					bind:value={choice.text}
					maxlength="120"
					placeholder="Pilihan {i + 1}"
					aria-label="Teks pilihan {i + 1}"
					aria-invalid={!!err('choices', i, 'text')}
				/>
				<button type="button" class="tool" onclick={() => choices.splice(i, 1)} disabled={choices.length <= min} aria-label="Buang pilihan {i + 1}">
					<Icon name="close" size={18} />
				</button>
				{#if err('choices', i, 'text')}<p class="field-error">{err('choices', i, 'text')}</p>{/if}
			</li>
		{/each}
	</ol>
	{#if choices.length < LIMITS.choices}
		<button type="button" class="add-row" onclick={() => choices.push(make.choice())}><Icon name="plus" size={18} /> Tambah pilihan</button>
	{/if}
	{#if err('choices')}<p class="field-error">{err('choices')}</p>{/if}
</fieldset>

<style>
	fieldset {
		display: grid;
		gap: 0.6rem;
		margin: 0;
		padding: 0;
		border: 0;
		min-width: 0;
	}
	legend {
		padding: 0;
		margin-bottom: 0.6rem;
		font-weight: 800;
		font-size: 0.95rem;
	}
	ol {
		display: grid;
		gap: 0.5rem;
		margin: 0;
		padding: 0;
		list-style: none;
	}
	li {
		display: grid;
		grid-template-columns: auto minmax(0, 1fr) auto;
		align-items: center;
		gap: 0.5rem;
	}
	li .field-error {
		grid-column: 2 / -1;
	}
	.right .input {
		border-color: var(--good);
		background: var(--good-soft);
	}
	.mark {
		position: relative;
		display: grid;
		place-items: center;
		width: 2.6rem;
		height: 2.6rem;
		cursor: pointer;
	}
	.mark input {
		position: absolute;
		inset: 0;
		margin: 0;
		opacity: 0;
		cursor: pointer;
	}
	.box {
		display: grid;
		place-items: center;
		width: 1.7rem;
		height: 1.7rem;
		border: 2px solid #cdbf9f;
		border-radius: 50%;
		background: var(--card);
		color: transparent;
		transition:
			background var(--t-state),
			border-color var(--t-state);
	}
	.box.square {
		border-radius: 7px;
	}
	.mark:hover .box {
		border-color: var(--good);
	}
	.mark input:checked + .box {
		border-color: var(--good);
		background: var(--good);
		color: #fff;
	}
	.mark input:focus-visible + .box {
		outline: 3px solid var(--sky);
		outline-offset: 2px;
	}
</style>
