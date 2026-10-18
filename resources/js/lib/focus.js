/**
 * Moves focus to an element Alpine has just revealed or rendered. `x-show` shows an element on the
 * next animation frame, so a plain focus() straight after the state change lands on something that
 * is still display:none and does nothing: keyboard and screen reader users would be left at the top
 * of the page. This waits until the element exists and has a box, for a few frames at most.
 *
 * `target` is an element, or a function returning one for something that is not in the page yet.
 */
export function focusWhenShown(target, frames = 10) {
    const attempt = () => {
        const element = typeof target === 'function' ? target() : target;

        if (element && element.getClientRects().length > 0) {
            element.focus();

            return;
        }

        if (frames-- > 0) {
            requestAnimationFrame(attempt);
        }
    };

    requestAnimationFrame(attempt);
}
