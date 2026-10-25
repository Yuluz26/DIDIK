import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, type ProxyOptions } from 'vite';

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

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		port: 5173,
		proxy: {
			'/api': asSameOrigin,
			'/uploads': server,
			'/ws': { ...asSameOrigin, target: server.replace('http', 'ws'), ws: true }
		}
	}
});
