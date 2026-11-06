<!-- A small round tick or cross on a thing once the answer is shown. -->
<script lang="ts">
	import Icon from '$ui/Icon.svelte';

	let { ok, size = 14 }: { ok: boolean; size?: number } = $props();
</script>

<span class="mark" class:off={!ok} aria-label={ok ? 'Betul' : 'Salah'}><Icon name={ok ? 'check' : 'close'} {size} /></span>

<style>
	.mark {
		position: absolute;
		top: -0.45rem;
		right: -0.45rem;
		z-index: 3;
		display: grid;
		place-items: center;
		width: 1.45rem;
		height: 1.45rem;
		border: 2px solid #fff;
		border-radius: 50%;
		background: var(--good);
		color: #fff;
		box-shadow: 0 2px 6px rgb(0 0 0 / 0.2);
	}
	.off {
		background: var(--almost);
	}
</style>
