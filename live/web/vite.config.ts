import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

// In development the Python server runs on :8080; Vite proxies the API, sockets and uploads to it.
const server = process.env.DIDIK_SERVER ?? 'http://127.0.0.1:8080';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 5173,
		proxy: {
			'/api': server,
			'/uploads': server,
			'/ws': { target: server.replace('http', 'ws'), ws: true }
		}
	}
});
