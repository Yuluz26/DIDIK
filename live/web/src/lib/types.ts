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
	/** All supported modes use 2D presentation. */
	look: '2d';
	/** Which of the three kinds of game: Kuiz Interaktif, the 2D island games, or the story mode. */
	family: 'interaktif' | '2d' | 'story';
	/** What a score counts: mata, m, syiling, petak... */
	unit: string;
	needs: string;
	eligible?: number;
	/** a subject's Kuiz Interaktif (sains, sejarah, islam): every question it suits plays as one of its games */
	subject?: string;
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
	teams?: { key: string; name: string; score: number; players: number }[];
	/** What a team's score counts (petak, gol). */
	teamUnit?: string;
	winner?: string | null;
	/** Co-op games: what the room built, in words from the server. */
	headline?: string;
	note?: string | null;
	complete?: boolean;
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
	/** After a server restart: the game waits, paused, until the players are back. */
	resuming?: true;
}

// ------------------------------------------------------------ questions

export interface Choice {
	id: string;
	text: string;
	/** A 3D sticker on the option (lib/stickers.ts). */
	sticker?: string | null;
}

export interface PublicQuestion {
	id: string;
	type:
		| 'single'
		| 'multiple'
		| 'truefalse'
		| 'text'
		| 'number'
		| 'order'
		| 'match'
		| 'blank'
		| 'count'
		| 'spell'
		| 'sort'
		| 'missing'
		| 'puzzle'
		| 'blocks'
		| 'clock'
		| 'money'
		| 'diagram';
	label: string;
	prompt: string;
	image: string | null;
	/** What illustrates the question: a 3D sticker (lib/stickers.ts) or a diagram (lib/diagrams.ts). */
	picture?: string | null;
	/** A subject game to answer it in (lib/subjects/games.ts). */
	game?: string;
	timeLimit: number;
	choices?: Choice[];
	pick?: number;
	maxLength?: number;
	unit?: string;
	items?: (Choice & { sticker?: string | null })[];
	left?: Choice[];
	right?: Choice[];
	parts?: (string | { blank: number } | { ch: string })[];
	blanks?: number;
	bank?: string[];
	/** Kira dan masukkan: the object, where it goes, and how many are in the pile. */
	sticker?: string | null;
	place?: string;
	supply?: number;
	/** Susun huruf: the mixed-up letters and how many boxes. */
	tiles?: { id: string; ch: string }[];
	length?: number;
	/** Isih kumpulan: the baskets (the things to sort are `items`, each with its sticker). */
	groups?: { id: string; name: string; sticker: string | null }[];
	/** Cantum gambar: the pieces (each with the part of the picture it shows) and the grid's size. */
	pieces?: { id: string; cut: number }[];
	grid?: number;
	/** Bina nombor: the place-value columns shown (ratus, puluh, sa). */
	places?: string[];
	/** Bayar dengan wang: the amount in sen and the coins and notes to pay with. */
	amount?: number;
	money?: number[];
	/** Label rajah: the diagram, its places (percent from the top left) and the labels to put on them. */
	diagram?: string;
	spots?: { id: string; x: number; y: number }[];
	labels?: { id: string; text: string }[];
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type Answer = any;

export interface Reveal {
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	correct: any;
	accepted?: string[];
	tolerance?: number;
	unit?: string;
	/** Why the answer is what it is, for a child who got it wrong. */
	explain?: string;
	/** Susun huruf, Huruf hilang: the whole word. */
	word?: string;
	/** Bina nombor: the number. */
	number?: number;
	/** Bayar dengan wang: one way to pay it, coin or note (in sen) to how many. */
	pay?: Record<string, number>;
}
