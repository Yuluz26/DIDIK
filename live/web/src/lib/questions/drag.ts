// Tap or drag, for the hands-on question types (Kira dan masukkan, Susun huruf, Isih kumpulan).
//
// Every movable thing is a button: a tap (or Enter and Space on a keyboard) does the simple thing, such as
// "put this in the basket". Dragging is the same move by hand: the piece follows the finger, the drop zone
// under it lights up, and letting go over a zone calls `drop` with that zone's `data-zone`. Let go anywhere
// else and the piece springs back. The piece keeps its dragged position when it is dropped, so the
// question's own animation can carry it from there to its new place.

export interface DragOptions {
	/** Nothing moves while this says no (the answer is sent, or the game is paused). */
	enabled: () => boolean;
	/** The zone this piece is in now: letting go over it again is no move at all. */
	home?: () => string | null;
	/** A tap, a click or Enter. */
	tap: () => void;
	/** Let go over the zone with this `data-zone`. */
	drop: (zone: string) => void;
}

const LIFT = 8;

function zoneAt(x: number, y: number, self: HTMLElement): HTMLElement | null {
	// the piece itself is under the finger: look past it
	const before = self.style.pointerEvents;
	self.style.pointerEvents = 'none';
	const under = document.elementFromPoint(x, y);
	self.style.pointerEvents = before;
	return (under?.closest('[data-zone]') as HTMLElement | null) ?? null;
}

export function dragTap(options: DragOptions) {
	return (node: HTMLElement) => {
		let start: { x: number; y: number; id: number } | null = null;
		let dragging = false;
		let dragged = false;
		let lit: HTMLElement | null = null;

		const light = (zone: HTMLElement | null) => {
			if (zone === lit) return;
			lit?.classList.remove('zone-hover');
			lit = zone;
			lit?.classList.add('zone-hover');
		};

		// Once pressed, the moves are followed on the whole window: a quick mouse leaves the piece before
		// its first move is seen (a finger's moves stay with the piece anyway).
		const follow = (on: boolean) => {
			if (on) {
				window.addEventListener('pointermove', move);
				window.addEventListener('pointerup', up);
				window.addEventListener('pointercancel', cancel);
			} else {
				window.removeEventListener('pointermove', move);
				window.removeEventListener('pointerup', up);
				window.removeEventListener('pointercancel', cancel);
			}
		};

		const down = (event: PointerEvent) => {
			if (!options.enabled() || event.button > 0) return;
			start = { x: event.clientX, y: event.clientY, id: event.pointerId };
			dragging = false;
			dragged = false;
			follow(true);
		};

		const move = (event: PointerEvent) => {
			if (!start || event.pointerId !== start.id) return;
			const dx = event.clientX - start.x;
			const dy = event.clientY - start.y;
			if (!dragging) {
				if (Math.hypot(dx, dy) < LIFT) return;
				dragging = true;
				try {
					node.setPointerCapture(event.pointerId);
				} catch {
					// a pointer the browser no longer tracks: the piece still follows the moves it gets
				}
				node.classList.add('dragging');
				node.style.transition = 'none';
			}
			event.preventDefault();
			node.style.transform = `translate(${dx}px, ${dy}px) scale(1.12) rotate(-4deg)`;
			const zone = zoneAt(event.clientX, event.clientY, node);
			light(zone && zone.dataset.zone !== options.home?.() ? zone : null);
		};

		const back = () => {
			node.style.transition = 'transform 280ms cubic-bezier(0.34, 1.56, 0.64, 1)';
			node.style.transform = '';
		};

		const up = (event: PointerEvent) => {
			if (!start || event.pointerId !== start.id) return;
			start = null;
			follow(false);
			if (!dragging) return;
			dragging = false;
			dragged = true;
			node.classList.remove('dragging');
			const zone = lit?.dataset.zone ?? null;
			light(null);
			if (zone && options.enabled()) {
				// keep where it was let go; the question's own animation takes it from here
				node.style.transform = node.style.transform.replace(/ scale\([^)]*\) rotate\([^)]*\)/, '');
				options.drop(zone);
				// a piece that stays (a letter dropped on its own slot) settles back
				requestAnimationFrame(() => node.isConnected && back());
			} else {
				back();
			}
		};

		const cancel = () => {
			follow(false);
			if (!dragging) {
				start = null;
				return;
			}
			start = null;
			dragging = false;
			node.classList.remove('dragging');
			light(null);
			back();
		};

		const click = (event: MouseEvent) => {
			// the click that ends a drag is not a tap
			if (dragged) {
				dragged = false;
				event.preventDefault();
				return;
			}
			if (options.enabled()) options.tap();
		};

		node.addEventListener('pointerdown', down);
		node.addEventListener('click', click);
		return () => {
			light(null);
			follow(false);
			node.removeEventListener('pointerdown', down);
			node.removeEventListener('click', click);
		};
	};
}

/** Whether moving things should glide, or just appear (prefers-reduced-motion). */
export function still(): boolean {
	return typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}
