import { api, query } from './core.js';
import { h, toast } from './ui.js';

const names = { free: 'Free', premium: 'Premium', family: 'Family' };
const money = (sen) => `RM${(sen / 100).toFixed(2)}`;
const date = (value) => value ? new Date(value).toLocaleDateString('ms-MY') : 'Tiada had';
const localValue = () => { const now = new Date(); return new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16); };
const option = (value, label) => h('option', { value }, label);
const field = (label, control) => h('label', { class: 'member-field' }, h('span', null, label), control);
const info = (text) => h('p', { class: 'member-info' }, text);

export default {
	title: 'Pengurusan keahlian',
	subtitle: 'Grant percuma, bayaran QR dan akses setiap ibu bapa.',
	search: 'Cari nama atau emel ibu bapa…',
	async mount(root, ctx) {
		const state = { q: ctx.params.get('q') || '', plan: '', page: 1, tab: 'parents' };
		const tabs = h('div', { class: 'member-tabs' });
		const content = h('div', { class: 'member-content' });
		root.append(tabs, content);
		function showTab(tab) { state.tab = tab; render(); }
		function drawTabs() {
			tabs.replaceChildren(...[['parents', 'Ibu bapa'], ['payments', 'Bayaran QR'], ['billing', 'Tetapan QR']].map(([key, label]) =>
				h('button', { type: 'button', class: key === state.tab ? 'btn primary' : 'btn', onClick: () => showTab(key) }, label)));
		}
		async function render() {
			drawTabs(); content.replaceChildren(info('Memuatkan…'));
			try {
				if (state.tab === 'parents') await parents();
				else if (state.tab === 'payments') await payments();
				else await billing();
			} catch (error) { content.replaceChildren(info(error.message)); }
		}
		async function parents() {
			const [overview, result] = await Promise.all([
				api('/membership/overview'), api(`/membership/parents${query({ q: state.q, plan: state.plan, page: state.page })}`)
			]);
			const stats = h('div', { class: 'member-stats' }, ...[
				['Ibu bapa', overview.totalParents], ['Free', overview.free], ['Premium', overview.premium],
				['Family', overview.family], ['Berbayar aktif', overview.activePaid], ['Grant aktif', overview.activeGrants],
				['Bayaran menunggu', overview.pendingPayments], ['Nilai bulanan setara', money(overview.mrrSen)]
			].map(([label, value]) => h('div', null, h('small', null, label), h('strong', null, value))));
			const filter = h('select', { class: 'input', 'aria-label': 'Tapis pelan', onChange: (event) => { state.plan = event.target.value; state.page = 1; render(); } },
				option('', 'Semua pelan'), option('free', 'Free'), option('premium', 'Premium'), option('family', 'Family'));
			filter.value = state.plan;
			const table = h('table', { class: 'member-table' },
				h('thead', null, h('tr', null, ...['Ibu bapa', 'Pelan', 'Sumber', 'Tamat', 'Profil anak', ''].map((name) => h('th', null, name)))),
				h('tbody', null, ...result.items.map((item) => h('tr', null,
					h('td', null, h('strong', null, item.name), h('small', null, item.email)),
					h('td', null, names[item.membership.plan]), h('td', null, item.membership.source),
					h('td', null, date(item.membership.expiresAt)), h('td', null, `${item.membership.childCount}/${item.membership.childLimit}`),
					h('td', null, h('button', { class: 'btn sm', type: 'button', onClick: () => detail(item.id) }, 'Urus keahlian'))))));
			const pages = h('div', { class: 'member-pagination' },
				h('button', { class: 'btn', type: 'button', disabled: state.page <= 1, onClick: () => { state.page--; render(); } }, 'Sebelum'),
				h('span', null, `Halaman ${state.page} · ${result.total} akaun`),
				h('button', { class: 'btn', type: 'button', disabled: state.page * result.per >= result.total, onClick: () => { state.page++; render(); } }, 'Seterusnya'));
			content.replaceChildren(stats, h('div', { class: 'member-toolbar' }, filter), result.items.length ? table : info('Tiada ibu bapa yang sepadan.'), pages);
		}
		async function detail(id) {
			const user = await api(`/membership/parents/${id}`);
			const back = h('button', { class: 'btn', type: 'button', onClick: render }, '← Senarai ibu bapa');
			const head = h('div', { class: 'member-detail-head' }, h('div', null, h('h2', null, user.name), h('p', null, user.email)),
				h('strong', null, `${names[user.membership.plan]} · ${user.membership.source}`));
			const paidWarning = user.paid.some((row) => row.status === 'active' && new Date(row.expiresAt) > new Date())
				? info('Akaun ini mempunyai tempoh berbayar yang sah. Grant percuma tidak akan memadam tempoh tersebut.') : null;
			const plan = h('select', { class: 'input' }, option('premium', 'Premium'), option('family', 'Family'), option('free', 'Free'));
			const start = h('input', { class: 'input', type: 'datetime-local', required: true, value: localValue() });
			const end = h('input', { class: 'input', type: 'datetime-local' });
			const note = h('textarea', { class: 'input', rows: 2, maxlength: 500, required: true, placeholder: 'Sebab perubahan' });
			const child = h('select', { class: 'input' }, option('', 'Pilih jika perlu'), ...user.children.map((c) => option(String(c.id), c.name)));
			const form = h('form', { class: 'member-form', onSubmit: async (event) => {
				event.preventDefault();
				if (!confirm(`Grant ${names[plan.value]} kepada ${user.name}? Semak tarikh dan sebab sebelum teruskan.`)) return;
				try {
					await api(`/membership/parents/${id}/grants`, { method: 'POST', body: { plan: plan.value,
						starts_at: new Date(start.value).toISOString(), expires_at: end.value ? new Date(end.value).toISOString() : null,
						note: note.value.trim(), selected_child_id: child.value ? Number(child.value) : null } });
					toast('Grant keahlian disimpan.'); detail(id);
				} catch (error) { toast(error.message, 'bad'); }
			} }, h('h3', null, 'Grant keahlian tanpa bayaran'), info('Kosongkan tarikh tamat hanya untuk akses percuma kekal.'),
				field('Pelan', plan), field('Mula', start), field('Tamat', end), field('Profil aktif jika turun ke Free/Premium', child),
				field('Sebab', note), h('button', { class: 'btn primary', type: 'submit' }, 'Simpan grant'));
			const feature = h('select', { class: 'input' }, ...['story', 'games', 'premium_quizzes', 'premium_levels', 'host', 'history', 'solo', 'party', 'max_children'].map((name) => option(name, name)));
			const enabled = h('select', { class: 'input' }, option('true', 'Benarkan'), option('false', 'Sekat'));
			const valueInt = h('input', { class: 'input', type: 'number', min: 1, max: 3, placeholder: 'Untuk max_children: 1–3' });
			const overrideEnd = h('input', { class: 'input', type: 'datetime-local' });
			const overrideNote = h('input', { class: 'input', maxlength: 500, required: true, placeholder: 'Sebab akses khas' });
			const overrideForm = h('form', { class: 'member-form', onSubmit: async (event) => {
				event.preventDefault();
				try { await api(`/membership/parents/${id}/overrides`, { method: 'POST', body: {
					feature: feature.value, enabled: enabled.value === 'true', value_int: valueInt.value ? Number(valueInt.value) : null, starts_at: new Date().toISOString(),
					expires_at: overrideEnd.value ? new Date(overrideEnd.value).toISOString() : null, note: overrideNote.value.trim()
				} }); toast('Akses khas disimpan.'); detail(id); }
				catch (error) { toast(error.message, 'bad'); }
			} }, h('h3', null, 'Akses khas'), field('Ciri', feature), field('Tindakan', enabled), field('Had profil jika dipilih', valueInt), field('Tamat', overrideEnd), field('Sebab', overrideNote), h('button', { class: 'btn', type: 'submit' }, 'Simpan akses'));
			const rows = (title, items, renderRow) => h('section', { class: 'member-records' }, h('h3', null, title), items.length ? h('ul', null, ...items.map(renderRow)) : info('Tiada rekod.'));
			content.replaceChildren(back, head, paidWarning, h('div', { class: 'member-detail-grid' }, form, overrideForm),
				rows('Grant', user.grants, (g) => h('li', null, `${names[g.plan]} · ${g.status} · ${date(g.startsAt)} – ${date(g.expiresAt)} · ${g.note}`,
					g.status === 'active' && h('button', { class: 'btn sm', type: 'button', onClick: async () => { if (!confirm('Batalkan grant ini?')) return; await api(`/membership/parents/${id}/grants/${g.id}/cancel`, { method: 'POST' }); detail(id); } }, 'Batalkan'))),
				rows('Langganan berbayar', user.paid, (p) => h('li', null, `${names[p.plan]} · ${p.interval} · ${money(p.priceSen)} · ${date(p.startsAt)} – ${date(p.expiresAt)} · ${p.status}`)),
				rows('Akses khas', user.overrides, (o) => h('li', null, `${o.feature} · ${o.enabled ? 'Benar' : 'Sekat'} · tamat ${date(o.expiresAt)}`,
					h('button', { class: 'btn sm', type: 'button', onClick: async () => { await api(`/membership/parents/${id}/overrides/${o.id}/cancel`, { method: 'POST' }); detail(id); } }, 'Batalkan'))),
				rows('Audit', user.history, (a) => h('li', null, `${date(a.at)} · ${a.actor} · ${a.action} · ${a.note}`)));
		}
		async function payments() {
			const result = await api('/membership/payments?status=pending');
			const list = result.items.length ? h('div', { class: 'member-payments' }, ...result.items.map((p) => {
				const note = h('input', { class: 'input', placeholder: 'Catatan semakan / rujukan bukti', maxlength: 500, required: true });
				const review = async (action) => {
					if (!note.value.trim()) return toast('Masukkan catatan semakan.', 'bad');
					if (!confirm(`${action === 'approve' ? 'Sahkan' : 'Tolak'} bayaran ${p.reference}? Pastikan bukti WhatsApp dan amaun sepadan.`)) return;
					try { await api(`/membership/payments/${p.id}/review`, { method: 'POST', body: { action, note: note.value.trim() } }); toast('Semakan disimpan.'); payments(); }
					catch (error) { toast(error.message, 'bad'); }
				};
				return h('section', { class: 'member-payment' }, h('h3', null, p.reference), h('p', null, `${p.parentName} · ${p.email}`),
					h('p', null, `${names[p.plan]} ${p.interval} · ${money(p.amountSen)} · ${date(p.createdAt)}`), note,
					h('div', null, h('button', { class: 'btn primary', type: 'button', onClick: () => review('approve') }, 'Sahkan bayaran'),
						h('button', { class: 'btn', type: 'button', onClick: () => review('reject') }, 'Tolak')));
			})) : info('Tiada bayaran menunggu semakan.');
			content.replaceChildren(info('Semak bukti bayaran di WhatsApp sebelum mengesahkan. Permintaan QR tidak mengaktifkan pelan secara automatik.'), list);
		}
		async function billing() {
			const data = await api('/membership/billing');
			const payee = h('input', { class: 'input', value: data.payeeName, maxlength: 120 });
			const instructions = h('textarea', { class: 'input', rows: 3, maxlength: 500 }, data.instructions);
			const file = h('input', { class: 'input', type: 'file', accept: 'image/png' });
			const form = h('form', { class: 'member-form', onSubmit: async (event) => {
				event.preventDefault();
				try {
					let qr_png_base64;
					if (file.files[0]) { if (file.files[0].size > 2_000_000) throw new Error('Gambar QR maksimum 2 MB.');
						const bytes = new Uint8Array(await file.files[0].arrayBuffer()); let binary = ''; for (const byte of bytes) binary += String.fromCharCode(byte);
						qr_png_base64 = btoa(binary); }
					await api('/membership/billing', { method: 'PUT', body: { payee_name: payee.value.trim(), instructions: instructions.value.trim(), ...(qr_png_base64 ? { qr_png_base64 } : {}) } });
					toast('Tetapan QR disimpan.'); billing();
				} catch (error) { toast(error.message, 'bad'); }
			} }, field('Nama penerima bayaran', payee), field('Arahan bayaran', instructions), field('Kod QR PNG (maksimum 2 MB)', file),
				h('button', { class: 'btn primary', type: 'submit' }, 'Simpan tetapan'));
			content.replaceChildren(info('Muat naik QR rasmi di sini. Ibu bapa akan hantar bukti bayaran ke WhatsApp +60139558132.'),
				data.qrImage && h('img', { class: 'member-qr', src: data.qrImage, alt: 'Kod QR semasa' }), form);
		}
		this.onSearch = (value) => { state.q = value; state.page = 1; if (state.tab === 'parents') render(); };
		await render();
		return () => { delete this.onSearch; };
	}
};
