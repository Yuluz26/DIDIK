// The signed-in parent, shared by every page in the parent area.

import { api } from './api';

export interface Parent {
	id: number;
	name: string;
	email: string;
}

class Session {
	user = $state<Parent | null>(null);
	demo = $state(false);
	/** Whether this server emails reset links (otherwise they go to its log). */
	mail = $state(true);
	/** The email typed on the sign-in form, carried to the forgotten-password page. */
	emailHint = '';
	loaded = $state(false);

	async load(): Promise<Parent | null> {
		try {
			const data = await api.get<{ user: Parent | null; demo: boolean; mail: boolean }>('/api/auth/me');
			this.user = data.user;
			this.demo = data.demo;
			this.mail = data.mail;
		} catch {
			this.user = null;
		}
		this.loaded = true;
		return this.user;
	}

	async login(email: string, password: string): Promise<void> {
		const data = await api.post<{ user: Parent }>('/api/auth/login', { email, password });
		this.user = data.user;
	}

	async register(name: string, email: string, password: string): Promise<void> {
		const data = await api.post<{ user: Parent }>('/api/auth/register', { name, email, password });
		this.user = data.user;
	}

	async logout(): Promise<void> {
		await api.post('/api/auth/logout');
		this.user = null;
	}
}

export const session = new Session();
