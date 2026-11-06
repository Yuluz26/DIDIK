<!-- Label rajah, played the plain way: a diagram with numbered pins and the labels to put on them. -->
<script lang="ts">
	import LabelBoard from '$lib/subjects/LabelBoard.svelte';
	import type { GameProps } from '$lib/subjects/kit.svelte';

	let props: GameProps = $props();
</script>

<LabelBoard {...props} />
