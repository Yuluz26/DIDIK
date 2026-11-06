<!--
	Choose a 3D sticker: a button showing the chosen one opens a dialog of every sticker, in groups, with a
	search by name. `optional` adds "Tiada gambar"; `diagrams` adds the diagrams and photos (lib/diagrams.ts)
	as their own group, for a question's picture.
-->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';
	import Sticker from '$ui/Sticker.svelte';
	import { STICKERS, STICKER_GROUPS, stickerOf, type StickerGroup } from '$lib/stickers';
	import { DIAGRAMS, diagramOf, diagramUrl } from '$lib/diagrams';

	let {
		value = $bindable(),
		label,
		optional = false,
		compact = false,
		diagrams = false,
		onpick
	}: {
		value: string | null;
		label: string;
		optional?: boolean;
		compact?: boolean;
		diagrams?: boolean;
		onpick?: (key: string | null) => void;
	} = $props();

	let dialog = $state<HTMLDialogElement>();
	let search = $state('');
	let tab = $state<StickerGroup | 'semua' | 'rajah'>('haiwan');

	const chosen = $derived(stickerOf(value));
	const chosenDiagram = $derived(diagrams ? diagramOf(value) : undefined);
	const shownDiagrams = $derived.by(() => {
		if (!diagrams) return [];
		const q = search.trim().toLowerCase();
		if (q) return DIAGRAMS.filter((d) => d.name.toLowerCase().includes(q));
		return tab === 'rajah' ? DIAGRAMS : [];
	});
	const shown = $derived.by(() => {
		const q = search.trim().toLowerCase();
		if (q) return STICKERS.filter((s) => s.name.toLowerCase().includes(q) || s.key.includes(q));
		if (tab === 'rajah') return [];
		return tab === 'semua' ? STICKERS : STICKERS.filter((s) => s.group === tab);
	});

	function open() {
		search = '';
		if (chosen) tab = chosen.group;
		else if (chosenDiagram) tab = 'rajah';
		dialog?.showModal();
	}

	function pick(key: string | null) {
		value = key;
		onpick?.(key);
		dialog?.close();
	}
</script>

<button type="button" class="pick" class:compact class:empty={!chosen && !chosenDiagram} onclick={open} aria-label="{label}: {chosen?.name ?? chosenDiagram?.name ?? 'tiada gambar'}. Tukar">
	{#if chosen}
		<Sticker key={chosen.key} size={compact ? 34 : 44} alt="" />
	{:else if chosenDiagram}
		<img class="thumb" src={diagramUrl(chosenDiagram.key)} alt="" />
	{:else}
		<span class="plus"><Icon name="plus" size={compact ? 16 : 20} /></span>
	{/if}
	{#if !compact}<span class="what"><small>{label}</small>{chosen?.name ?? chosenDiagram?.name ?? 'Pilih gambar'}</span>{/if}
</button>

<dialog bind:this={dialog} class="picker" aria-label="Pilih gambar: {label}" onclick={(e) => e.target === dialog && dialog?.close()}>
	<div class="sheet">
		<header>
			<h2>Pilih gambar</h2>
			<button type="button" class="close" onclick={() => dialog?.close()} aria-label="Tutup"><Icon name="close" /></button>
		</header>
		<input class="input" type="search" bind:value={search} placeholder="Cari: kucing, epal, bas..." aria-label="Cari gambar" />
		{#if !search.trim()}
			<div class="tabs" role="tablist" aria-label="Kumpulan gambar">
				{#if diagrams}<button type="button" role="tab" aria-selected={tab === 'rajah'} class:on={tab === 'rajah'} onclick={() => (tab = 'rajah')}>Rajah &amp; foto</button>{/if}
				{#each STICKER_GROUPS as g (g.key)}
					<button type="button" role="tab" aria-selected={tab === g.key} class:on={tab === g.key} onclick={() => (tab = g.key)}>{g.name}</button>
				{/each}
			</div>
		{/if}
		<ul class="grid">
			{#if optional}
				<li>
					<button type="button" class="cell none" class:on={!value} onclick={() => pick(null)}>
						<Icon name="close" size={22} />
						<span>Tiada gambar</span>
					</button>
				</li>
			{/if}
			{#each shownDiagrams as d (d.key)}
				<li>
					<button type="button" class="cell rajah" class:on={value === d.key} onclick={() => pick(d.key)}>
						<img src={diagramUrl(d.key)} alt="" loading="lazy" />
						<span>{d.name}</span>
					</button>
				</li>
			{/each}
			{#each shown as s (s.key)}
				<li>
					<button type="button" class="cell" class:on={value === s.key} onclick={() => pick(s.key)}>
						<Sticker key={s.key} size={52} alt="" />
						<span>{s.name}</span>
					</button>
				</li>
			{:else}
				{#if !shownDiagrams.length}<li class="nothing">Tiada gambar bernama "{search}".</li>{/if}
			{/each}
		</ul>
	</div>
</dialog>

<style>
	.pick {
		display: inline-flex;
		align-items: center;
		gap: 0.55rem;
		min-height: 3.4rem;
		padding: 0.3rem 0.8rem 0.3rem 0.35rem;
		border: 2px solid var(--line);
		border-radius: var(--r-md);
		background: var(--card);
		color: var(--ink);
		text-align: left;
		cursor: pointer;
		transition:
			border-color var(--t-state),
			transform var(--t-state) var(--spring);
	}
	.pick:hover {
		border-color: var(--sky);
		transform: translateY(-1px);
	}
	.thumb {
		width: 3.4rem;
		height: 2.6rem;
		border-radius: 6px;
		object-fit: cover;
		background: #fff;
	}
	.cell.rajah img {
		width: 100%;
		height: 4.2rem;
		border-radius: 8px;
		object-fit: contain;
		background: #fff;
	}
	.pick.compact {
		justify-content: center;
		width: 2.9rem;
		min-height: 2.9rem;
		padding: 0.2rem;
	}
	.pick.empty {
		border-style: dashed;
	}
	.plus {
		display: grid;
		place-items: center;
		width: 2.6rem;
		height: 2.6rem;
		border-radius: 50%;
		background: var(--paper-2);
		color: var(--ink-2);
	}
	.compact .plus {
		width: 2rem;
		height: 2rem;
	}
	.what {
		display: grid;
		font-weight: 800;
		line-height: 1.2;
	}
	.what small {
		color: var(--ink-3);
		font-size: 0.75rem;
		font-weight: 800;
	}
	.picker {
		width: min(40rem, calc(100vw - 1.5rem));
		max-height: min(42rem, calc(100dvh - 2rem));
		padding: 0;
		border: 0;
		border-radius: 22px;
		background: var(--card);
		box-shadow: 0 30px 70px rgb(31 45 39 / 0.3);
	}
	.picker::backdrop {
		background: rgb(31 45 39 / 0.45);
		backdrop-filter: blur(3px);
	}
	.picker[open] {
		animation: pop-in 260ms var(--spring);
	}
	.sheet {
		display: grid;
		grid-template-rows: auto auto auto minmax(0, 1fr);
		gap: 0.7rem;
		max-height: inherit;
		padding: 1rem;
	}
	header {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	h2 {
		font: 600 1.3rem var(--font-display);
	}
	.close {
		display: grid;
		place-items: center;
		width: 2.75rem;
		height: 2.75rem;
		border: 0;
		border-radius: 50%;
		background: var(--paper-2);
		cursor: pointer;
	}
	.tabs {
		display: flex;
		gap: 0.35rem;
		overflow-x: auto;
		padding-bottom: 0.2rem;
	}
	.tabs button {
		flex: none;
		min-height: 2.5rem;
		padding: 0 0.9rem;
		border: 2px solid var(--line);
		border-radius: 999px;
		background: var(--card);
		font-weight: 800;
		cursor: pointer;
	}
	.tabs button.on {
		border-color: var(--brand);
		background: var(--brand);
		color: #fff;
	}
	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(5.4rem, 1fr));
		gap: 0.4rem;
		margin: 0;
		padding: 0.1rem;
		overflow-y: auto;
		list-style: none;
	}
	.cell {
		display: grid;
		justify-items: center;
		align-content: center;
		gap: 0.2rem;
		width: 100%;
		min-height: 5.6rem;
		padding: 0.4rem 0.2rem;
		border: 2px solid transparent;
		border-radius: 14px;
		background: var(--paper);
		font-size: 0.78rem;
		font-weight: 800;
		line-height: 1.1;
		text-align: center;
		cursor: pointer;
		transition:
			transform var(--t-state) var(--spring),
			border-color var(--t-state);
	}
	.cell:hover {
		transform: translateY(-2px) scale(1.04);
		border-color: var(--line);
	}
	.cell.on {
		border-color: var(--brand);
		background: var(--brand-soft);
	}
	.cell.none {
		color: var(--ink-2);
	}
	.nothing {
		grid-column: 1 / -1;
		padding: 1rem;
		color: var(--ink-2);
		font-weight: 800;
		text-align: center;
	}
</style>
