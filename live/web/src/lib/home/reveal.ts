import type { Attachment } from 'svelte/attachments';

/**
 * Lifts an element into place the first time it scrolls into view, `delay` ms after the others in its
 * group. Without motion, or without IntersectionObserver, the element is simply there; nothing is
 * hidden before the script runs.
 */
export function reveal(delay = 0): Attachment<HTMLElement> {
	return (node) => {
		if (matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
		node.classList.add('reveal');
		node.style.setProperty('--delay', `${delay}ms`);
		const seen = new IntersectionObserver(
			(entries) => {
				if (entries.some((e) => e.isIntersecting)) {
					node.classList.add('in');
					seen.disconnect();
				}
			},
			{ rootMargin: '0px 0px -8% 0px' }
		);
		seen.observe(node);
		return () => seen.disconnect();
	};
}
