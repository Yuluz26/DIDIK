<!--
	The editors of the four small hands-on games that need only a setting or two: Cantum gambar (the
	picture and 4 or 9 pieces), Bina nombor (the number), Laraskan jam (the time) and Bayar dengan wang
	(the price and what is bought). While the question still says what this editor wrote for it, it follows
	the settings; once the parent writes their own words it is left alone.
-->
<script lang="ts">
	import { ringgit } from '$lib/money';
	import { stickerOf } from '$lib/stickers';
	import Sticker from '$ui/Sticker.svelte';
	import StickerPicker from './StickerPicker.svelte';
	import type { Question } from './model';

	type Small = Extract<Question, { type: 'puzzle' | 'blocks' | 'clock' | 'money' }>;
	let { question = $bindable(), err }: { question: Small; err: (...path: (string | number)[]) => string | undefined } = $props();

	const time = (h: number, m: number) => `${h}.${String(m).padStart(2, '0')}`;

	function said(q: Small): string {
		if (q.type === 'blocks') return `Bina nombor ${q.answer} dengan blok ${q.answer >= 100 ? 'ratus, puluh dan sa' : 'puluh dan sa'}.`;
		if (q.type === 'clock') return `Laraskan jam kepada pukul ${time(q.hour, q.minute)}.`;
		if (q.type === 'money') {
			const what = stickerOf(q.sticker)?.name;
			return what ? `${what} ini berharga ${ringgit(q.amount)}. Bayar dengan tepat.` : `Bayar ${ringgit(q.amount)} dengan tepat.`;
		}
		return 'Cantumkan kepingan gambar ini.';
	}

	function change(apply: () => void) {
		const following = !question.prompt.trim() || question.prompt === said(question);
		apply();
		if (following) question.prompt = said(question);
	}

	// money is typed in ringgit ("2.50") and kept in sen
	let price = $state(question.type === 'money' ? (question.amount / 100).toFixed(2) : '');
	function setPrice(value: string) {
		price = value;
		const sen = Math.round(Number(value.replace(',', '.')) * 100);
		if (question.type === 'money' && Number.isFinite(sen) && sen > 0) change(() => question.type === 'money' && (question.amount = Math.round(sen / 5) * 5));
	}
</script>

<div class="small-ed">
	{#if question.type === 'puzzle'}
		<div class="row">
			<div class="field">
				<span>Gambar untuk dicantum</span>
				<StickerPicker bind:value={question.sticker} label="Gambar" optional />
				<small class="help">Atau kosongkan dan guna gambar soalan (Tambah gambar) di atas.</small>
			</div>
			<fieldset class="grid-choice">
				<legend>Bilangan kepingan</legend>
				<div class="seg">
					<button type="button" aria-pressed={question.grid === 2} onclick={() => question.type === 'puzzle' && (question.grid = 2)}>4 keping</button>
					<button type="button" aria-pressed={question.grid === 3} onclick={() => question.type === 'puzzle' && (question.grid = 3)}>9 keping</button>
				</div>
			</fieldset>
		</div>
		{#if question.sticker}
			<div class="cut" style:--g={question.grid} aria-hidden="true">
				<Sticker key={question.sticker} size={120} alt="" />
				<span class="lines"></span>
			</div>
		{/if}
	{:else if question.type === 'blocks'}
		<label class="field num">
			<span>Nombor untuk dibina (1 hingga 999)</span>
			<input
				class="input"
				type="number"
				min="1"
				max="999"
				value={question.answer}
				oninput={(e) => {
					const n = Math.max(1, Math.min(999, Math.round(Number((e.currentTarget as HTMLInputElement).value) || 1)));
					change(() => question.type === 'blocks' && (question.answer = n));
				}}
				aria-invalid={!!err('answer')}
			/>
			{#if err('answer')}<span class="field-error">{err('answer')}</span>{/if}
		</label>
		<p class="help">{question.answer} = {question.answer >= 100 ? `${Math.floor(question.answer / 100)} ratus + ` : ''}{Math.floor(question.answer / 10) % 10} puluh + {question.answer % 10} sa</p>
	{:else if question.type === 'clock'}
		<div class="row time">
			<label class="field">
				<span>Jam</span>
				<select class="input" value={question.hour} onchange={(e) => change(() => question.type === 'clock' && (question.hour = Number((e.currentTarget as HTMLSelectElement).value)))}>
					{#each Array.from({ length: 12 }, (_, i) => i + 1) as h (h)}<option value={h}>{h}</option>{/each}
				</select>
			</label>
			<label class="field">
				<span>Minit</span>
				<select class="input" value={question.minute} onchange={(e) => change(() => question.type === 'clock' && (question.minute = Number((e.currentTarget as HTMLSelectElement).value)))}>
					{#each Array.from({ length: 12 }, (_, i) => i * 5) as m (m)}<option value={m}>{String(m).padStart(2, '0')}</option>{/each}
				</select>
			</label>
			<p class="say">pukul <strong>{time(question.hour, question.minute)}</strong></p>
		</div>
	{:else if question.type === 'money'}
		<div class="row">
			<label class="field">
				<span>Harga (RM)</span>
				<input class="input" inputmode="decimal" value={price} oninput={(e) => setPrice((e.currentTarget as HTMLInputElement).value)} placeholder="Contoh: 2.50" aria-invalid={!!err('amount')} />
				{#if err('amount')}<span class="field-error">{err('amount')}</span>{:else}<small class="help">= {ringgit(question.amount)}, dibundarkan kepada 5 sen.</small>{/if}
			</label>
			<div class="field">
				<span>Barang yang dibeli</span>
				<StickerPicker value={question.sticker} label="Barang" optional onpick={(key) => change(() => question.type === 'money' && (question.sticker = key))} />
			</div>
		</div>
	{/if}
</div>

<style>
	.small-ed {
		display: grid;
		gap: 0.9rem;
	}
	.row {
		display: flex;
		flex-wrap: wrap;
		align-items: flex-start;
		gap: 0.9rem;
	}
	.row > :global(*) {
		flex: 1 1 12rem;
	}
	.grid-choice {
		margin: 0;
		padding: 0;
		border: 0;
	}
	.grid-choice legend {
		margin-bottom: 0.4rem;
		padding: 0;
		font-weight: 800;
		font-size: 0.95rem;
	}
	.seg {
		display: inline-flex;
		gap: 0.3rem;
		padding: 0.25rem;
		border-radius: 999px;
		background: var(--paper-2);
	}
	.seg button {
		min-height: 2.6rem;
		padding: 0 1rem;
		border: 0;
		border-radius: 999px;
		background: transparent;
		font-weight: 800;
		cursor: pointer;
	}
	.seg button[aria-pressed='true'] {
		background: var(--card);
		box-shadow: 0 2px 0 var(--line);
	}
	.cut {
		position: relative;
		width: 120px;
		height: 120px;
		border-radius: 12px;
		background: conic-gradient(from 45deg, #ffd1e3, #ffe9a8, #c9f2d8, #c8e2ff, #e3d2ff, #ffd1e3);
	}
	.lines {
		position: absolute;
		inset: 0;
		border-radius: 12px;
		background:
			repeating-linear-gradient(90deg, transparent 0 calc(100% / var(--g) - 2px), #fff calc(100% / var(--g) - 2px) calc(100% / var(--g))),
			repeating-linear-gradient(0deg, transparent 0 calc(100% / var(--g) - 2px), #fff calc(100% / var(--g) - 2px) calc(100% / var(--g)));
	}
	.cut :global(img) {
		position: absolute;
		inset: 0;
	}
	.num input {
		max-width: 10rem;
		font: 600 1.3rem var(--font-display);
	}
	.time {
		align-items: flex-end;
	}
	.time > :global(.field) {
		flex: 0 1 7rem;
	}
	.say {
		flex: 1 1 8rem;
		padding-bottom: 0.6rem;
		font-weight: 800;
	}
	.say strong {
		font: 600 1.4rem var(--font-display);
	}
</style>
