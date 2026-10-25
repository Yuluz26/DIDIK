<!--
	Where a 3D world is drawn. Fills its parent; the parent decides the size. Frames are drawn only
	while something moves (the world says so from `tick`), when the size changes, or when the world
	asks to be woken, and never while the stage is off screen or the tab is hidden.

	The stage owns its world: `create` builds it (usually after a dynamic import, so three.js loads
	only here), the stage disposes it when it goes, and `bind:world` hands it to the game to update.

	`children` is an overlay above the canvas (name tags, chest buttons); `fallback` replaces the
	canvas on a device without WebGL, or when the world could not be loaded, so the game stays
	playable as a quiz.
-->
<script lang="ts" generics="W extends World3D">
	import { untrack, type Snippet } from 'svelte';
	import type { World3D } from './stage';

	let {
		create,
		world = $bindable(null),
		label,
		fallback,
		children
	}: { create: () => Promise<W>; world?: W | null; label: string; fallback?: Snippet; children?: Snippet } = $props();

	let host = $state<HTMLDivElement>();
	let canvas = $state<HTMLCanvasElement | null>(null);
	let built = $state<W | null>(null);
	let failed = $state(false);

	// The picture is described on the canvas itself, so buttons in the overlay stay buttons.
	$effect(() => canvas?.setAttribute('aria-label', label));

	// Build the world once per mount; a world that arrives after the stage has gone is thrown away.
	$effect(() => {
		let made: W | null = null;
		let cancelled = false;
		untrack(() => create())
			.then((next) => {
				if (cancelled) return next.dispose();
				made = built = world = next;
			})
			.catch(() => (failed = true));
		return () => {
			cancelled = true;
			made?.dispose();
			built = world = null;
		};
	});

	$effect(() => {
		const el = host;
		const current = built;
		if (!el || !current) return;
		let stop = () => {};
		let cancelled = false;
		import('./stage')
			.then(({ PixelPass, pixelSize, renderer }) => {
				if (cancelled) return;
				const gl = renderer();
				const pass = new PixelPass(gl);
				const end = run(el, current, gl, pass, pixelSize);
				stop = () => {
					end();
					pass.dispose();
				};
			})
			.catch(() => (failed = true));
		return () => {
			cancelled = true;
			stop();
		};
	});

	function run(el: HTMLDivElement, current: W, gl: import('three').WebGLRenderer, pass: import('./stage').PixelPass, pixel: (width: number) => number): () => void {
		const surface = gl.domElement;
		surface.classList.add('gl');
		surface.setAttribute('role', 'img');
		el.prepend(surface);
		canvas = surface;

		let width = 0;
		let height = 0;
		let frame = 0;
		let last = 0;
		let dirty = true;
		let onScreen = true;

		const resize = () => {
			const box = el.getBoundingClientRect();
			width = Math.max(1, Math.round(box.width));
			height = Math.max(1, Math.round(box.height));
			// The picture is drawn small and magnified without smoothing, so every pixel is a block.
			const p = pixel(width);
			const w = Math.max(1, Math.ceil(width / p));
			const h = Math.max(1, Math.ceil(height / p));
			gl.setPixelRatio(1);
			gl.setSize(w, h, false);
			pass.setSize(w, h);
			current.resize(width, height);
			dirty = true;
			wake();
		};

		const step = (now: number) => {
			frame = 0;
			const dt = last ? Math.min(0.1, (now - last) / 1000) : 1 / 60;
			last = now;
			const moving = current.tick(dt, now / 1000);
			if (moving || dirty) {
				pass.render(current.scene, current.camera);
				current.afterRender?.(width, height);
				dirty = false;
			}
			if (moving && onScreen && !document.hidden) frame = requestAnimationFrame(step);
			else last = 0;
		};

		function wake() {
			dirty = true;
			if (!frame && onScreen && !document.hidden) frame = requestAnimationFrame(step);
		}

		current.wake = wake;
		const sizes = new ResizeObserver(resize);
		sizes.observe(el);
		const sight = new IntersectionObserver(([entry]) => {
			onScreen = entry.isIntersecting;
			if (onScreen) wake();
		});
		sight.observe(el);
		const visibility = () => !document.hidden && wake();
		document.addEventListener('visibilitychange', visibility);
		resize();

		return () => {
			if (frame) cancelAnimationFrame(frame);
			current.wake = undefined;
			sizes.disconnect();
			sight.disconnect();
			document.removeEventListener('visibilitychange', visibility);
			if (surface.parentElement === el) surface.remove();
			canvas = null;
		};
	}
</script>

{#if failed}
	{@render fallback?.()}
{:else}
	<div class="stage3d" bind:this={host}>
		{#if children}<div class="overlay">{@render children()}</div>{/if}
	</div>
{/if}

<style>
	.stage3d {
		position: relative;
		width: 100%;
		height: 100%;
		overflow: hidden;
		border-radius: inherit;
		background: var(--stage-bg, #13303d);
		touch-action: manipulation;
	}
	.stage3d :global(canvas.gl) {
		position: absolute;
		inset: 0;
		display: block;
		width: 100%;
		height: 100%;
		image-rendering: pixelated;
	}
	.overlay {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}
	.overlay :global(:is(button, a, [data-interactive])) {
		pointer-events: auto;
	}
</style>
