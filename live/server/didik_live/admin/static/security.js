// Keselamatan: who is signed in to this control room, what happened at the door, and how the door is kept.

import { api } from './core.js';
import { eventRow, refreshTimes } from './feed.js';
import { ago, confirmBox, empty, h, icon, pill, skeletons, stamp, tile, toast } from './ui.js';

function device(agent) {
	const browser = /Edg\//.test(agent) ? 'Edge' : /Chrome\//.test(agent) ? 'Chrome' : /Firefox\//.test(agent) ? 'Firefox' : /Safari\//.test(agent) ? 'Safari' : 'Pelayar';
	const system = /iPhone|iPad/.test(agent) ? 'iOS' : /Android/.test(agent) ? 'Android' : /Windows/.test(agent) ? 'Windows' : /Mac OS/.test(agent) ? 'macOS' : /Linux/.test(agent) ? 'Linux' : '';
	return system ? `${browser} di ${system}` : browser;
}

export default {
	title: 'Keselamatan',
	subtitle: 'Sesi yang sedang masuk dan catatan di pintu.',
	search: 'Cari…',

	async mount(root, ctx) {
		const sessions = h('ul', { class: 'list' });
		const log = h('ul', { class: 'list feed tall' });
		const sessionsCard = h('section', { class: 'card s6' }, h('div', { class: 'card-head' }, h('h2', null, 'Sesi yang sedang masuk')), skeletons(2));
		const logCard = h('section', { class: 'card s6' }, h('div', { class: 'card-head' }, h('h2', null, 'Catatan pintu')), log);
		const facts = h('section', { class: 'card s12' }, h('div', { class: 'card-head' }, h('h2', null, 'Cara pintu ini dijaga')));
		root.append(h('div', { class: 'grid' }, sessionsCard, logCard, facts));

		const me = ctx.state.me;
		facts.append(h('ul', { class: 'list' },
			...[
				['lock', 'Alamat rahsia', 'Halaman log masuk hanya wujud pada alamat rahsia. Alamat lain menunjukkan laman biasa, seolah-olah tiada bilik kawalan.'],
				['mail', 'Kod melalui emel', `Hanya ${me.email} boleh meminta kod. Kod 6 digit sah 10 minit, 5 percubaan, sekali guna.${me.mail ? '' : ' SMTP belum ditetapkan, jadi kod hanya ditulis dalam log pelayan.'}`],
				['shield', 'Sesi', `Sesi tamat selepas 12 jam, atau 4 jam tanpa aktiviti. Sesi ini tamat ${stamp(me.expiresAt)}.`],
				['alert', 'Amaran', 'Setiap log masuk dihantar ke emel anda. Jika anda tidak mengenalinya, tukar DIDIK_ADMIN_PATH pada pelayan dan mulakan semula perkhidmatan.']
			].map(([name, title, text]) => h('li', null, tile(name), h('span', { class: 'grow' }, h('b', null, title), h('small', { class: 'wrap' }, text))))
		));

		async function load() {
			try {
				const data = await api('/security');
				sessions.replaceChildren(...data.sessions.map((s) => h('li', null,
					tile('device', s.current ? 'mint' : ''),
					h('span', { class: 'grow' }, h('b', null, device(s.agent), s.current && ' ', s.current && pill('Sesi ini', 'ok')), h('small', null, `${s.ip} · masuk ${stamp(s.createdAt)} · aktif ${ago(s.lastSeenAt)}`)),
					!s.current && h('button', { class: 'btn sm danger', type: 'button', onClick: async () => {
						await api(`/sessions/${s.id}`, { method: 'DELETE' });
						toast('Sesi ditamatkan.');
						load();
					} }, 'Tamatkan')
				)));
				const others = data.sessions.filter((s) => !s.current).length;
				sessionsCard.replaceChildren(
					h('div', { class: 'card-head' }, h('h2', null, 'Sesi yang sedang masuk'), others > 0 && h('button', { class: 'btn sm danger', type: 'button', onClick: async () => {
						if (!(await confirmBox({ title: 'Tamatkan semua sesi lain?', body: 'Peranti lain akan diminta kod baharu. Sesi ini kekal.', ok: 'Tamatkan semua', danger: true }))) return;
						await api('/sessions/revoke-others', { method: 'POST' });
						toast('Sesi lain ditamatkan.');
						load();
					} }, 'Tamatkan semua yang lain')),
					sessions
				);
				log.replaceChildren(...(data.log.length ? data.log.map((e) => eventRow(e, { detail: true })) : [h('li', null, empty('shield', 'Belum ada catatan.'))]));
			} catch (error) {
				sessionsCard.replaceChildren(h('p', { class: 'error-line' }, error.message));
			}
		}
		await load();
		const stops = [ctx.on('tick', () => refreshTimes(log)), ctx.on('event', (event) => event.kind.startsWith('admin.') && load())];
		return () => stops.forEach((stop) => stop());
	}
};
