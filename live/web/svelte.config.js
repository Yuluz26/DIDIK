import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** A single-page app: FastAPI serves build/ and falls back to 200.html for every page route. */
export default {
	preprocess: vitePreprocess(),
	kit: {
		// precompress: .br and .gz beside every text file, which the server sends to browsers that take them
		adapter: adapter({ fallback: '200.html', precompress: true }),
		alias: { $ui: 'src/lib/ui', $games: 'src/lib/games' }
	}
};
