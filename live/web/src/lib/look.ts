// Rooms playing a 3D game use darker colours that match its dusk and night worlds (app.css,
// :root[data-look='3d']), from the join screen to the podium; the 2D games keep the warm paper look.

export function applyLook(look: string | undefined): () => void {
	const root = document.documentElement;
	if (look === '3d') root.dataset.look = look;
	else delete root.dataset.look;
	return () => delete root.dataset.look;
}
