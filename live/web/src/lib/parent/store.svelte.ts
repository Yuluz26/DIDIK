// What the signed-in parent's pages share: their quizzes, the sample quizzes and the rooms still open.
// Loaded once per sign-in, so moving between the dashboard's pages does not refetch everything.

import { goto } from '$app/navigation';
import { api } from '$lib/api';
import { session } from '$lib/session.svelte';

export interface QuizSummary {
	id: number;
	title: string;
	description: string;
	questionCount: number;
	types: Record<string, number>;
	isSample: boolean;
	updatedAt: string | null;
}

export interface ActiveRoom {
	code: string;
	slug: string;
	quizTitle: string;
	mode: { title: string; world: string };
	phase: string;
	players: number;
}

export const TYPE_NAMES: Record<string, string> = {
	single: 'Pilihan',
	multiple: 'Pilih semua',
	truefalse: 'Betul/Salah',
	text: 'Taip',
	number: 'Nombor',
	order: 'Susun',
	match: 'Padan',
	blank: 'Isi kosong'
};

class ParentData {
	mine = $state<QuizSummary[]>([]);
	samples = $state<QuizSummary[]>([]);
	rooms = $state<ActiveRoom[]>([]);
	loading = $state(true);
	problem = $state<string | null>(null);
	private loadedFor: number | null = null;

	/** Loads for the signed-in parent, once per sign-in (or again when `force` is set). */
	async ensure(force = false): Promise<void> {
		const user = session.user;
		if (!user) return;
		if (!force && this.loadedFor === user.id) return;
		this.loadedFor = user.id;
		this.loading = true;
		this.problem = null;
		try {
			const data = await api.get<{ mine: QuizSummary[]; samples: QuizSummary[] }>('/api/quizzes');
			this.mine = data.mine;
			this.samples = data.samples;
			this.rooms = (await api.get<{ rooms: ActiveRoom[] }>('/api/rooms/mine')).rooms;
		} catch (error) {
			this.problem = (error as Error).message;
		}
		this.loading = false;
	}

	/** Quizzes newest first (by last edit), for "terkini" lists. */
	get recent(): QuizSummary[] {
		return [...this.mine].sort((a, b) => (b.updatedAt ?? '').localeCompare(a.updatedAt ?? ''));
	}

	get totalQuestions(): number {
		return this.mine.reduce((sum, q) => sum + q.questionCount, 0);
	}

	get totalPlayers(): number {
		return this.rooms.reduce((sum, r) => sum + r.players, 0);
	}

	async copy(quiz: QuizSummary): Promise<void> {
		const copied = await api.post<{ id: number }>(`/api/quizzes/${quiz.id}/copy`);
		await this.ensure(true);
		await goto(`/ibu-bapa/kuiz/${copied.id}`);
	}

	async remove(quiz: QuizSummary): Promise<void> {
		await api.del(`/api/quizzes/${quiz.id}`);
		this.mine = this.mine.filter((q) => q.id !== quiz.id);
	}

	reset(): void {
		this.mine = [];
		this.samples = [];
		this.rooms = [];
		this.loadedFor = null;
		this.loading = true;
	}
}

export const parent = new ParentData();
