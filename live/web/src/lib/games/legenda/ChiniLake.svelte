<script lang="ts">
	// Geometry only: the official painting and boss remain the sole character artwork.
	let { cue = 'idle', x, y, still = false, paused = false }: {
		cue?: string; x: number; y: number; still?: boolean; paused?: boolean;
	} = $props();
</script>

<div class="lake {cue}" class:still class:paused style:left={`${x * 100}%`} style:top={`${y * 100}%`} aria-hidden="true">
	{#key cue}
		<span class="mist"></span>
		{#each [0, 1, 2] as i}<span class="ripple" style:--i={i}></span>{/each}
	{/key}
</div>

<style>
	.lake { position: absolute; width: 27%; height: 9%; transform: translate(-50%, -50%); z-index: 3; pointer-events: none; color: #a8f4e4; }
	.ripple { position: absolute; inset: 0; border: 0.16cqw solid currentColor; border-radius: 50%; opacity: 0; animation: ripple 4.8s ease-out infinite; animation-delay: calc(var(--i) * 1.6s); }
	.mist { position: absolute; inset: -100% -12% -20%; background: radial-gradient(ellipse at 50% 75%, rgb(105 226 209 / 0.22), transparent 65%); opacity: 0.5; }
	.reveal .ripple, .defeat .ripple { animation-duration: 1.6s; animation-iteration-count: 1; animation-delay: calc(var(--i) * 0.24s); }
	.reveal .mist { animation: mist 1.5s ease-out both; }
	.charge .ripple { animation: gather 0.65s ease-in both; animation-delay: calc(var(--i) * 0.12s); }
	.strike .ripple, .hit .ripple, .weak .ripple { animation: ripple 0.85s ease-out both; animation-delay: calc(var(--i) * 0.08s); }
	.weak { color: #ffe69b; }
	.defeat { color: #f5e5ae; }
	.defeat .mist { animation: mist 1.8s ease-out reverse both; }
	@keyframes ripple { 0% { transform: scale(0.38); opacity: 0; } 18% { opacity: 0.65; } 100% { transform: scale(1.3); opacity: 0; } }
	@keyframes gather { from { transform: scale(1.4); opacity: 0; } to { transform: scale(0.45); opacity: 0.85; } }
	@keyframes mist { from { transform: translateY(12%); opacity: 0; } 45% { opacity: 0.9; } to { transform: translateY(-10%); opacity: 0.3; } }
	.paused span { animation-play-state: paused; }
	.still .ripple { animation: none; opacity: 0.25; transform: scale(0.85); }
	.still .ripple:nth-of-type(3), .still .ripple:nth-of-type(4) { display: none; }
	.still .mist { animation: none; }
	@media (prefers-reduced-motion: reduce) { .lake span { animation: none; } .ripple { opacity: 0.25; } }
</style>
