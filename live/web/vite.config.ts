import { createHash } from 'node:crypto';
import { readdirSync, readFileSync } from 'node:fs';
import { join, relative } from 'node:path';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, type Plugin, type ProxyOptions } from 'vite';

// In development the Python server runs on :8080; Vite proxies the API, sockets and uploads to it.
const server = process.env.DIDIK_SERVER ?? 'http://127.0.0.1:8080';

// The server only accepts changes and sockets whose Origin is its own, so through the proxy the page
// is presented as coming from the server's address.
const asSameOrigin: ProxyOptions = {
	target: server,
	changeOrigin: true,
	configure: (proxy) => {
		proxy.on('proxyReq', (req) => req.setHeader('origin', server));
		proxy.on('proxyReqWs', (req) => req.setHeader('origin', server));
	}
};

/**
 * `virtual:story-hashes`: a short hash of every file in static/story/, by its path there. The story art
 * is asked for with its own hash (data.ts, storyArt), so browsers and the service worker keep a picture
 * or a video for as long as it is unchanged, across new builds of the app, and fetch it again only once
 * it really changes.
 */
function storyHashes(): Plugin {
	const id = 'virtual:story-hashes';
	const root = join(process.cwd(), 'static', 'story');
	const walk = (dir: string): string[] =>
		readdirSync(dir, { withFileTypes: true }).flatMap((entry) => (entry.isDirectory() ? walk(join(dir, entry.name)) : [join(dir, entry.name)]));
	return {
		name: 'didik-story-hashes',
		resolveId: (source) => (source === id ? `\0${id}` : undefined),
		load(source) {
			if (source !== `\0${id}`) return;
			const hashes: Record<string, string> = {};
			for (const file of walk(root)) {
				if (file.endsWith('manifest.json')) continue;
				hashes[relative(root, file).split('\\').join('/')] = createHash('sha256').update(readFileSync(file)).digest('hex').slice(0, 12);
			}
			return `export default ${JSON.stringify(hashes)};`;
		}
	};
}

export default defineConfig({
	plugins: [storyHashes(), sveltekit()],
	server: {
		port: 5173,
		proxy: {
			'/api': asSameOrigin,
			'/uploads': server,
			'/ws': { ...asSameOrigin, target: server.replace('http', 'ws'), ws: true }
		}
	}
});
