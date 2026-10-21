<!--
	A thumb stick for phones and tablets: drag from the centre, the animal walks that way. Arrow keys
	and WASD do the same on a keyboard (handled by the parent).
-->
<script lang="ts">
	let { onmove }: { onmove: (dx: number, dy: number) => void } = $props();

	let pad = $state<HTMLElement>();
	let knob = $state({ x: 0, y: 0 });
	let active = false;
	let last = 0;

	function update(event: PointerEvent) {
		if (!pad) return;
		const box = pad.getBoundingClientRect();
		const radius = box.width / 2;
		let x = (event.clientX - (box.left + radius)) / radius;
		let y = (event.clientY - (box.top + radius)) / radius;
		const length = Math.hypot(x, y);
		if (length > 1) {
			x /= length;
			y /= length;
		}
		knob = { x, y };
		const now = performance.now();
		if (now - last > 70) {
			last = now;
			onmove(Math.hypot(x, y) < 0.22 ? 0 : x, Math.hypot(x, y) < 0.22 ? 0 : y);
		}
	}

	function start(event: PointerEvent) {
		active = true;
		(event.currentTarget as HTMLElement).setPointerCapture(event.pointerId);
		update(event);
	}

	function stop() {
		if (!active) return;
		active = false;
		knob = { x: 0, y: 0 };
		onmove(0, 0);
	}
</script>

<div
	class="stick"
	bind:this={pad}
	role="application"
	aria-label="Kayu bedik: seret untuk berjalan"
	onpointerdown={start}
	onpointermove={(e) => active && update(e)}
	onpointerup={stop}
	onpointercancel={stop}
>
	<span class="knob" style:transform="translate({knob.x * 2.2}rem, {knob.y * 2.2}rem)"></span>
</div>

<style>
	.stick {
		position: relative;
		display: grid;
		place-items: center;
		width: 7.5rem;
		height: 7.5rem;
		border-radius: 50%;
		background: rgb(255 255 255 / 0.55);
		border: 3px solid rgb(255 255 255 / 0.9);
		box-shadow: 0 6px 0 rgb(0 0 0 / 0.15);
		touch-action: none;
		user-select: none;
	}
	.knob {
		width: 3rem;
		height: 3rem;
		border-radius: 50%;
		background: var(--sun);
		box-shadow: 0 4px 0 var(--sun-deep);
		transition: transform 60ms linear;
	}
</style>
