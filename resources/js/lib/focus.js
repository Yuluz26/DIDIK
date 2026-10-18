/**
 * Moves focus to an element Alpine has just revealed. `x-show` shows an element on the next
 * animation frame, so a plain focus() straight after the state change lands on something that is
 * still display:none and does nothing: keyboard and screen reader users would be left at the top
 * of the page after every answer. This waits until the element has a box, for a few frames at most.
 */
export function focusWhenShown(element, frames = 10) {
    if (!element) {
        return;
    }

    const attempt = () => {
        if (element.getClientRects().length > 0) {
            element.focus();

            return;
        }

        if (frames-- > 0) {
            requestAnimationFrame(attempt);
        }
    };

    requestAnimationFrame(attempt);
}
