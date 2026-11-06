<!-- Mikroskop: the cell comes into focus down the eyepiece; label its parts. -->
<script lang="ts">
	import LabelBoard from '../LabelBoard.svelte';
	import type { GameProps } from '../kit.svelte';

	let props: GameProps = $props();
</script>

<LabelBoard {...props} skin="scope" />
