// A very small Chrome DevTools Protocol driver: headless Chrome emulating a phone, for screenshots and
// scripted play-testing. No dependencies (Node's own fetch and WebSocket).
import { spawn } from 'node:child_process';
import { mkdirSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';

const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export async function launch({ port = 9333, width = 390, height = 844, scale = 2 } = {}) {
	const profile = join(tmpdir(), `didik-cdp-${port}`);
	const chrome = spawn(CHROME, ['--headless=new', `--remote-debugging-port=${port}`, '--disable-gpu', '--hide-scrollbars', '--mute-audio', `--user-data-dir=${profile}`, 'about:blank'], { stdio: 'ignore' });
	let target;
	for (let i = 0; i < 60 && !target; i++) {
		await sleep(250);
		try {
			target = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((t) => t.type === 'page');
		} catch {
			/* not up yet */
		}
	}
	if (!target) throw new Error('Chrome did not start');
	const ws = new WebSocket(target.webSocketDebuggerUrl);
	await new Promise((resolve, reject) => {
		ws.addEventListener('open', resolve);
		ws.addEventListener('error', reject);
	});
	let seq = 0;
	const pending = new Map();
	const logs = [];
	ws.addEventListener('message', (event) => {
		const m = JSON.parse(event.data);
		if (m.id) {
			const p = pending.get(m.id);
			pending.delete(m.id);
			if (m.error) p.reject(new Error(m.error.message));
			else p.resolve(m.result);
		} else if (m.method === 'Runtime.exceptionThrown') {
			logs.push('EXC ' + (m.params.exceptionDetails.exception?.description ?? m.params.exceptionDetails.text).split('\n')[0]);
		} else if (m.method === 'Runtime.consoleAPICalled' && (m.params.type === 'error' || m.params.type === 'warning')) {
			logs.push(m.params.type.toUpperCase() + ' ' + m.params.args.map((a) => a.value ?? a.description ?? '').join(' ').slice(0, 300));
		}
	});
	const send = (method, params = {}) =>
		new Promise((resolve, reject) => {
			const id = ++seq;
			pending.set(id, { resolve, reject });
			ws.send(JSON.stringify({ id, method, params }));
		});
	await send('Page.enable');
	await send('Runtime.enable');
	const size = async (w, h, dpr = scale) => {
		await send('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: dpr, mobile: true });
		await send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 5 });
	};
	await size(width, height);

	const page = {
		logs,
		send,
		size,
		async goto(url, { wait = 600 } = {}) {
			await send('Page.navigate', { url });
			for (let i = 0; i < 80; i++) {
				await sleep(150);
				const ready = await page.eval('document.readyState === "complete"').catch(() => false);
				if (ready) break;
			}
			await sleep(wait);
		},
		/** Evaluates an expression (may be async) in the page and returns its value. */
		async eval(expression) {
			const r = await send('Runtime.evaluate', { expression: `(async () => (${expression}))()`, awaitPromise: true, returnByValue: true });
			if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
			return r.result.value;
		},
		/** Waits until an expression is truthy. */
		async until(expression, { timeout = 15000, every = 150 } = {}) {
			const end = Date.now() + timeout;
			while (Date.now() < end) {
				const v = await page.eval(expression).catch(() => false);
				if (v) return v;
				await sleep(every);
			}
			throw new Error('timeout waiting for: ' + expression.slice(0, 80));
		},
		sleep,
		/** A PNG of the page, or of the element a selector names (with a margin). */
		async shot(file, { selector, margin = 8, full = false } = {}) {
			let clip;
			if (selector) {
				const box = await page.eval(`(() => { const e = document.querySelector(${JSON.stringify(selector)}); if (!e) return null; const r = e.getBoundingClientRect(); return { x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: r.height }; })()`);
				if (!box) throw new Error('no element: ' + selector);
				clip = { x: Math.max(0, box.x - margin), y: Math.max(0, box.y - margin), width: box.width + margin * 2, height: box.height + margin * 2, scale: 1 };
			} else if (full) {
				const m = await send('Page.getLayoutMetrics');
				clip = { x: 0, y: 0, width: m.cssContentSize.width, height: m.cssContentSize.height, scale: 1 };
			}
			const r = await send('Page.captureScreenshot', { format: 'png', clip, captureBeyondViewport: !!clip });
			mkdirSync(dirname(file), { recursive: true });
			writeFileSync(file, Buffer.from(r.data, 'base64'));
		},
		/** A finger tap at a point of the viewport (CSS pixels). */
		async tap(x, y) {
			await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
			await sleep(40);
			await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
			await sleep(120);
		},
		/** Taps the middle of the element a selector names (scrolling it into view first). */
		async tapOn(selector, nth = 0) {
			const at = await page.eval(`(() => { const e = document.querySelectorAll(${JSON.stringify(selector)})[${nth}]; if (!e) return null; e.scrollIntoView({ block: 'center' }); const r = e.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()`);
			if (!at) throw new Error('no element to tap: ' + selector);
			await sleep(120);
			const again = await page.eval(`(() => { const r = document.querySelectorAll(${JSON.stringify(selector)})[${nth}].getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()`);
			await page.tap(again[0], again[1]);
		},
		/** A finger drag from one point to another, in steps. */
		async drag(x1, y1, x2, y2, { steps = 12, hold = 60 } = {}) {
			await send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: x1, y: y1 }] });
			await sleep(hold);
			for (let i = 1; i <= steps; i++) {
				await send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: x1 + ((x2 - x1) * i) / steps, y: y1 + ((y2 - y1) * i) / steps }] });
				await sleep(16);
			}
			await sleep(hold);
			await send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
			await sleep(200);
		},
		async close() {
			try {
				await send('Browser.close');
			} catch {
				/* already gone */
			}
			chrome.kill();
		}
	};
	return page;
}
