// One live connection to a room, for a host screen or a child's device. Reconnects on its own;
// a child's device keeps a token per room so a dropped connection or a reload keeps their place.

import type { Person, View } from './types';

export interface Fx {
	t: 'fx';
	kind: string;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	[key: string]: any;
}

type Status = 'idle' | 'connecting' | 'open' | 'reconnecting' | 'ended';

/** What a child picks on the join screen: a nickname, an animal hood, a colour and a skin tone. */
export interface JoinData {
	name: string;
	avatar: string;
	colour: string;
	skin: string;
}

const TOKEN_PREFIX = 'didik-live:token:';

function storage(): Storage | null {
	try {
		return window.localStorage;
	} catch {
		return null;
	}
}

export function savedToken(key: string): string | null {
	return storage()?.getItem(TOKEN_PREFIX + key.toLowerCase()) ?? null;
}

export class RoomClient {
	view = $state<View | null>(null);
	roster = $state<Person[]>([]);
	status = $state<Status>('idle');
	/** A final message: the room closed, the child was removed, the link is wrong. */
	notice = $state<string | null>(null);
	/** A passing message, e.g. a refused action. Clears itself. */
	error = $state<string | null>(null);
	youId = $state<string | null>(null);
	/** True when a child must pick an avatar and name before joining. */
	needsJoin = $state(false);
	joining = $state(false);

	/** Server time minus local time, for countdowns that agree on every device. */
	offset = 0;
	/** Hutan Misteri positions, kept outside reactivity and drawn every frame. */
	positions = new Map<string, { x: number; y: number; f: number }>();

	private ws: WebSocket | null = null;
	private fxListeners = new Set<(fx: Fx) => void>();
	private posListeners = new Set<() => void>();
	private attempts = 0;
	private stopped = false;
	private joinData: JoinData | null = null;
	private errorTimer: ReturnType<typeof setTimeout> | null = null;
	private pingTimer: ReturnType<typeof setInterval> | null = null;

	constructor(
		public key: string,
		public role: 'host' | 'player'
	) {}

	get people(): Map<string, Person> {
		return new Map(this.roster.map((p) => [p.id, p]));
	}

	now(): number {
		return Date.now() + this.offset;
	}

	connect(): void {
		this.stopped = false;
		this.status = this.attempts ? 'reconnecting' : 'connecting';
		const scheme = location.protocol === 'https:' ? 'wss' : 'ws';
		const ws = new WebSocket(`${scheme}://${location.host}/ws/${encodeURIComponent(this.key)}`);
		this.ws = ws;
		ws.onopen = () => {
			this.attempts = 0;
			this.status = 'open';
			if (this.role === 'host') {
				this.raw({ t: 'host' });
			} else {
				const token = savedToken(this.key);
				if (token) this.raw({ t: 'hello', token });
				else if (this.joinData) this.raw({ t: 'join', ...this.joinData });
				else this.needsJoin = true;
			}
			this.pingTimer = setInterval(() => this.raw({ t: 'ping' }), 25000);
		};
		ws.onmessage = (event) => this.receive(event.data);
		ws.onclose = () => {
			if (this.pingTimer) clearInterval(this.pingTimer);
			if (this.ws !== ws) return;
			this.ws = null;
			if (this.stopped) {
				this.status = 'ended';
				return;
			}
			this.status = 'reconnecting';
			// Doubling waits, each with some randomness, so a classroom that lost its connection at the same
			// moment does not come back in one burst.
			const wait = Math.min(5000, 400 * 2 ** this.attempts++) * (0.6 + Math.random() * 0.8);
			setTimeout(() => !this.stopped && this.connect(), wait);
		};
	}

	/** A child chooses avatar and name, then joins (connecting first if needed). */
	join(data: JoinData): void {
		this.joinData = data;
		this.joining = true;
		if (this.ws?.readyState === WebSocket.OPEN) this.raw({ t: 'join', ...data });
		else if (!this.ws) this.connect();
	}

	send(message: Record<string, unknown>): void {
		this.raw(message);
	}

	close(): void {
		this.stopped = true;
		this.ws?.close();
	}

	onFx(fn: (fx: Fx) => void): () => void {
		this.fxListeners.add(fn);
		return () => this.fxListeners.delete(fn);
	}

	onPositions(fn: () => void): () => void {
		this.posListeners.add(fn);
		return () => this.posListeners.delete(fn);
	}

	private raw(message: Record<string, unknown>): void {
		if (this.ws?.readyState === WebSocket.OPEN) this.ws.send(JSON.stringify(message));
	}

	private flash(message: string): void {
		this.error = message;
		if (this.errorTimer) clearTimeout(this.errorTimer);
		this.errorTimer = setTimeout(() => (this.error = null), 4000);
	}

	private receive(text: string): void {
		let msg: { t: string; [key: string]: unknown };
		try {
			msg = JSON.parse(text);
		} catch {
			return;
		}
		switch (msg.t) {
			case 'view': {
				this.offset = (msg.now as number) - Date.now();
				const view = msg.view as View;
				this.view = view;
				if (view.room?.code) this.remember(view);
				break;
			}
			case 'roster':
				this.roster = msg.players as Person[];
				break;
			case 'fx':
				this.fxListeners.forEach((fn) => fn(msg as Fx));
				break;
			case 'pos':
				for (const [id, x, y, f] of msg.p as [string, number, number, number][]) {
					this.positions.set(id, { x, y, f });
				}
				this.posListeners.forEach((fn) => fn());
				break;
			case 'welcome':
				this.joining = false;
				this.needsJoin = false;
				if (msg.role === 'player') {
					this.youId = msg.id as string;
					storage()?.setItem(TOKEN_PREFIX + this.key.toLowerCase(), msg.token as string);
				}
				break;
			case 'rejoin-failed':
				storage()?.removeItem(TOKEN_PREFIX + this.key.toLowerCase());
				if (this.joinData) this.raw({ t: 'join', ...this.joinData });
				else this.needsJoin = true;
				break;
			case 'error':
				this.joining = false;
				if (msg.code === 'no-room' || msg.code === 'not-host') {
					this.notice = msg.message as string;
					this.stopped = true;
				} else {
					this.flash(msg.message as string);
				}
				break;
			case 'kicked':
			case 'closed':
				this.notice = msg.message as string;
				this.stopped = true;
				storage()?.removeItem(TOKEN_PREFIX + this.key.toLowerCase());
				break;
		}
	}

	private remember(view: View): void {
		// A token saved under the word link also works under the code, and the other way round.
		const token = savedToken(this.key);
		if (!token || this.role !== 'player') return;
		for (const alias of [view.room.code, view.room.slug]) {
			storage()?.setItem(TOKEN_PREFIX + alias.toLowerCase(), token);
		}
	}
}
