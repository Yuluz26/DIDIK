// Rooms playing a game made for Tingkatan 1-5 use the darker "arena" colours (app.css,
// :root[data-level='menengah']) from the join screen to the podium; the primary-school games keep the
// warm paper look.

export function applyLevel(level: string | undefined): () => void {
	const root = document.documentElement;
	if (level === 'menengah') root.dataset.level = level;
	else delete root.dataset.level;
	return () => delete root.dataset.level;
}
