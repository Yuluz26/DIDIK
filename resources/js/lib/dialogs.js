/** Opens and closes native <dialog> elements from data attributes. No other behaviour. */
export function initDialogs() {
    document.addEventListener('click', (event) => {
        const opener = event.target.closest('[data-dialog-open]');

        if (opener) {
            document.getElementById(opener.dataset.dialogOpen)?.showModal();
            return;
        }

        if (event.target.closest('[data-dialog-close]')) {
            event.target.closest('dialog')?.close();
            return;
        }

        // A click on the backdrop lands on the dialog element itself.
        if (event.target instanceof HTMLDialogElement) {
            event.target.close();
        }
    });
}
