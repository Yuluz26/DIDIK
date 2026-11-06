<!-- Peta Nusantara: pin the names on an old, sun-browned map with a compass rose. -->
<script lang="ts">
	import LabelBoard from '../LabelBoard.svelte';
	import type { GameProps } from '../kit.svelte';

	let props: GameProps = $props();
</script>

<LabelBoard {...props} skin="parchment" />
