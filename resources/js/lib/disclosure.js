/**
 * The filter panel is a <details> so it can collapse on phones. On wide screens it is always
 * open; the summary is hidden there by CSS, so it is opened here once on load.
 */
export function initDisclosures() {
    const wide = window.matchMedia('(min-width: 64rem)');

    document.querySelectorAll('details[data-open-on-desktop]').forEach((details) => {
        if (wide.matches) {
            details.open = true;
        }
    });
}
