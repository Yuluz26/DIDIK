// Shapes of what the server sends. Game-specific parts are typed in each game's component.

export type Pace = 'sync' | 'self' | 'roam';

export interface ModeInfo {
	key: string;
	title: string;
	tagline: string;
	how: string;
	style: string;
	pace: Pace;
	world: string;
	needs: string;
	eligible?: number;
	reason?: string | null;
}

export interface RoomInfo {
	code: string;
	slug: string;
	quizTitle: string;
	mode: ModeInfo;
	phase: 'lobby' | 'playing' | 'ended';
	locked: boolean;
	customNames: boolean;
	waitingRoom: boolean;
	accepting: boolean;
	reason: string | null;
	link?: string;
}

export interface Person {
	id: string;
	name: string;
	avatar: string;
	colour: string;
	skin?: string;
	team: string | null;
	online: boolean;
	bot: boolean;
	approved: boolean;
}

export interface FeedItem {
	id: number;
	text: string;
	kind: string;
	player: string | null;
}

export interface Clock {
	paused: boolean;
	deadline?: number;
	left?: number;
}

export interface Me extends Person {
	score: number;
}

export interface RoomSettings {
	timing: 'normal' | 'longer' | 'relaxed';
	minutes: number;
	question_limit: number | null;
	shuffle: boolean;
	custom_names: boolean;
	waiting_room: boolean;
	late_join: boolean;
	max_players: number;
	naughty: boolean;
}

export interface ResultRow {
	id: string;
	score: number;
	rank: number;
	team?: string | null;
	hearts?: number;
}

export interface Results {
	kind: 'solo' | 'teams' | 'coop';
	players: ResultRow[];
	teams?: { key: string; name: string; cells: number; players: number }[];
	winner?: string | null;
	built?: number;
	total?: number;
	complete?: boolean;
	decorations?: number;
}

export interface View {
	room: RoomInfo;
	phase: 'lobby' | 'playing' | 'ended' | 'waiting';
	round: number;
	feed: FeedItem[];
	me?: Me;
	host?: true;
	settings?: RoomSettings;
	botsAllowed?: boolean;
	modes?: ModeInfo[];
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	game?: any;
	results?: Results;
	/** In the lobby: where everyone stands in the waiting room's square, as [id, x, y, facing]. */
	plaza?: [string, number, number, number][];
}

// ------------------------------------------------------------ questions

export interface Choice {
	id: string;
	text: string;
}

export interface PublicQuestion {
	id: string;
	type: 'single' | 'multiple' | 'truefalse' | 'text' | 'number' | 'order' | 'match' | 'blank';
	label: string;
	prompt: string;
	image: string | null;
	timeLimit: number;
	choices?: Choice[];
	pick?: number;
	maxLength?: number;
	unit?: string;
	items?: Choice[];
	left?: Choice[];
	right?: Choice[];
	parts?: (string | { blank: number })[];
	blanks?: number;
	bank?: string[];
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Answer = any;

export interface Reveal {
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	correct: any;
	accepted?: string[];
	tolerance?: number;
	unit?: string;
}
