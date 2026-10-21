<!--
	A question's picture: upload one (it is re-encoded on the server), see it, change or remove it.
-->
<script lang="ts">
	import { api, ApiError } from '$lib/api';
	import Icon from '$ui/Icon.svelte';

	let { image = $bindable(null), id }: { image: string | null; id: string } = $props();

	let busy = $state(false);
	let problem = $state('');

	async function choose(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		input.value = '';
		if (!file) return;
		if (file.size > 5 * 1024 * 1024) {
			problem = 'Gambar terlalu besar. Had 5 MB.';
			return;
		}
		busy = true;
		problem = '';
		try {
			image = (await api.upload<{ url: string }>('/api/uploads', file)).url;
		} catch (error) {
			problem = error instanceof ApiError ? error.message : 'Gambar tidak dapat dimuat naik. Cuba lagi.';
		}
		busy = false;
	}
</script>

<div class="image-field">
	{#if image}
		<img src={image} alt="Gambar soalan" />
	{/if}
	<div class="actions">
		<label class="btn btn--plain" class:busy aria-busy={busy}>
			<input id="image-{id}" type="file" accept="image/png,image/jpeg,image/webp,image/gif" onchange={choose} disabled={busy} />
			<Icon name="image" size={18} />
			{busy ? 'Memuat naik…' : image ? 'Tukar gambar' : 'Tambah gambar'}
		</label>
		{#if image && !busy}
			<button type="button" class="btn btn--ghost" onclick={() => (image = null)}>Buang</button>
		{/if}
	</div>
	{#if problem}<p class="field-error" role="alert">{problem}</p>{/if}
</div>

<style>
	.image-field {
		display: grid;
		gap: 0.5rem;
		justify-items: start;
	}
	img {
		max-width: min(100%, 16rem);
		max-height: 10rem;
		border-radius: var(--r-sm);
		object-fit: contain;
		background: var(--paper-2);
	}
	.actions {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}
	label {
		position: relative;
		cursor: pointer;
	}
	label:focus-within {
		outline: 3px solid var(--sky);
		outline-offset: 3px;
	}
	input {
		position: absolute;
		inset: 0;
		opacity: 0;
		cursor: pointer;
	}
	.busy {
		opacity: 0.7;
	}
</style>
