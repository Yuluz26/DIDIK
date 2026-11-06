<!-- Tubuh Manusia: label the body's parts on an X-ray screen, with a scan line passing over it. -->
<script lang="ts">
	import LabelBoard from '../LabelBoard.svelte';
	import type { GameProps } from '../kit.svelte';

	let props: GameProps = $props();
</script>

<LabelBoard {...props} skin="xray" />
