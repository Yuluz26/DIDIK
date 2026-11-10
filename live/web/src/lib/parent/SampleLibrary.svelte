<script lang="ts">
	import { api } from '$lib/api';
	import { diagramOf, diagramUrl, isDiagram } from '$lib/diagrams';
	import { stickerOf } from '$lib/stickers';
	import Sticker from '$lib/ui/Sticker.svelte';
	import { parent, TYPE_NAMES, type QuizSummary } from './store.svelte';

	let { quizzes }: { quizzes: QuizSummary[] } = $props();

	type Question = { id: string; type: string; prompt?: string; picture?: string; diagram?: string; sticker?: string; image?: string };
	type FullQuiz = QuizSummary & { questions: Question[] };
	type Section = { key: string; title: string; subtitle: string; badge: string; color: string; books: QuizSummary[] };

	let dialog: HTMLDialogElement;
	let selected = $state<QuizSummary | null>(null);
	let opened = $state<FullQuiz | null>(null);
	let active = $state(0);
	let loading = $state(false);
	let error = $state('');
	let copying = $state(false);
	let requestId = 0;

	const sections = $derived.by((): Section[] => {
		const islam = quizzes.filter((q) => q.title.startsWith('Pendidikan Islam'));
		const primary = quizzes.filter((q) => !islam.includes(q) && !/Menengah|Tingkatan/.test(q.title));
		const secondary = quizzes.filter((q) => !islam.includes(q) && !primary.includes(q));
		return [
			{ key: 'islam', title: 'Pendidikan Islam & KAFA', subtitle: 'Akhlak, ibadah, sirah dan tajwid', badge: 'Buku 01', color: 'plum', books: islam },
			{ key: 'primary', title: 'KSSR & asas pembelajaran', subtitle: 'Bahasa, nombor, sains dan negaraku', badge: 'Buku 02', color: 'teal', books: primary },
			{ key: 'secondary', title: 'Menengah', subtitle: 'Topik lebih mendalam untuk remaja', badge: 'Buku 03', color: 'coral', books: secondary }
		].filter((section) => section.books.length);
	});

	function visual(quiz: QuizSummary, question?: Question): string {
		if (question?.diagram && isDiagram(question.diagram)) return question.diagram;
		if (question?.picture && isDiagram(question.picture)) return question.picture;
		const text = `${question?.prompt ?? ''} ${quiz.title}`.toLowerCase();
		if (/suria|planet|angkasa|matahari/.test(text)) return 'rajah-suria';
		if (/air|hujan|sejatan|wap/.test(text) && /sains|kitaran/.test(text)) return 'rajah-kitaran-air';
		if (/sel tumbuhan|pokok|daun/.test(text)) return 'rajah-sel-pokok';
		if (/sel|haiwan|paru|jantung|rangka|organ/.test(text) && /sains/.test(quiz.title)) return 'rajah-sel-haiwan';
		if (/haiwan|gajah|harimau|penyu|burung|rama-rama/.test(text)) return 'rajah-gajah-asia';
		if (/merdeka|melaka|kesultanan|famosa/.test(text)) return 'rajah-afamosa';
		if (/bujang|sejarah/.test(text)) return 'rajah-lembah-bujang';
		if (/malaysia|negeri|sabah|sarawak|semenanjung/.test(text)) return 'rajah-malaysia';
		if (/matematik|nombor|kira|algebra|wang/.test(text)) return 'rajah-number-line';
		if (/bahasa|eja|huruf|kata|ayat/.test(text)) return 'rajah-letters';
		if (/islam|sirah|ibadah|fiqh|tajwid|solat/.test(text)) return 'rajah-kaabah';
		return 'rajah-malaysia';
	}

	function label(quiz: QuizSummary): string {
		if (quiz.title.includes('Pendidikan Islam')) return 'PENDIDIKAN ISLAM';
		if (quiz.title.includes('Sains')) return 'SAINS';
		if (quiz.title.includes('Sejarah') || quiz.title.includes('Malaysiaku')) return 'SEJARAH';
		if (quiz.title.includes('Matematik') || quiz.title.includes('Kira')) return 'MATEMATIK';
		if (quiz.title.includes('Bahasa') || quiz.title.includes('Eja')) return 'BAHASA';
		return 'KUIZ INTERAKTIF';
	}

	async function open(quiz: QuizSummary) {
		selected = quiz;
		opened = null;
		active = 0;
		error = '';
		loading = true;
		if (!dialog.open) dialog.showModal();
		const current = ++requestId;
		try {
			const full = await api.get<FullQuiz>(`/api/quizzes/${quiz.id}`);
			if (current === requestId) opened = full;
		} catch (cause) {
			if (current === requestId) error = (cause as Error).message;
		} finally {
			if (current === requestId) loading = false;
		}
	}

	function close() {
		requestId++;
		dialog.close();
		selected = null;
		opened = null;
	}

	async function copy() {
		if (!selected || copying) return;
		copying = true;
		try {
			await parent.copy(selected);
			close();
		} catch (cause) {
			error = (cause as Error).message;
		} finally {
			copying = false;
		}
	}
</script>

<div class="library">
	<div class="library-intro">
		<span class="library-mark" aria-hidden="true">âœ¦</span>
		<div><strong>Jelajah rak buku</strong><p>Pilih sebuah buku, selak soalan, kemudian main atau salin untuk kelas anda.</p></div>
		<span class="library-count">{quizzes.length} buku Â· {quizzes.reduce((n, q) => n + q.questionCount, 0)} soalan</span>
	</div>
	{#if !quizzes.length && parent.loading}<p class="empty">Sedang menyusun buku di rakâ€¦</p>{/if}
	{#each sections as section (section.key)}
		<section class="shelf" aria-labelledby="heading-{section.key}">
			<div class="shelf-heading"><span class="shelf-number">{section.badge}</span><div><h2 id="heading-{section.key}">{section.title}</h2><p>{section.subtitle}</p></div><span class="shelf-total">{section.books.length} koleksi</span></div>
			<div class="book-row">
				{#each section.books as quiz, index (quiz.id)}
					<button class="book {section.color}" type="button" onclick={() => open(quiz)} aria-label="Buka buku {quiz.title}, {quiz.questionCount} soalan" style={`--book-index:${index}`}>
						<span class="book-pages" aria-hidden="true"></span>
						<span class="book-cover">
							<span class="book-spine" aria-hidden="true"></span>
							<span class="book-top"><span class="book-icon" aria-hidden="true">âœ¿</span><span>DIDIK LIBRARY</span></span>
							<img class="cover-art" src={diagramUrl(visual(quiz))} alt="" loading="lazy" />
							<span class="book-subject">{label(quiz)}</span>
							<strong>{quiz.title}</strong>
							<span class="book-bottom"><span>{quiz.questionCount} soalan</span><span aria-hidden="true">â†—</span></span>
						</span>
					</button>
				{/each}
			</div>
			<div class="shelf-edge" aria-hidden="true"></div>
		</section>
	{/each}
</div>

<dialog bind:this={dialog} class="book-dialog" aria-label={selected ? `Buku ${selected.title}` : 'Buku soalan'} onclose={() => { requestId++; selected = null; opened = null; }} onclick={(event) => { if (event.target === dialog) close(); }}>
	{#if selected}
		<div class="open-book">
			<header class="book-dialog-header"><span>âœ¿ &nbsp; PERPUSTAKAAN DIDIK</span><button type="button" class="close" onclick={close} aria-label="Tutup buku">Ã—</button></header>
			{#if loading}<div class="loading"><span class="loading-book" aria-hidden="true">ðŸ“–</span><p>Sedang membuka bukuâ€¦</p></div>
			{:else if error && !opened}<div class="loading"><p role="alert">{error}</p><button type="button" onclick={() => open(selected!)}>Cuba lagi</button></div>
			{:else if opened}
				<div class="spread">
					<div class="left-page">
						<span class="eyebrow">{label(opened)} Â· {opened.questionCount} SOALAN</span>
						<h2>{opened.title}</h2>
						{#if opened.description}<p class="book-description">{opened.description}</p>{/if}
						<div class="contents-title">Isi kandungan <span>pilih soalan</span></div>
						<nav class="question-list" aria-label="Pilih soalan dalam buku">
							{#each opened.questions as question, index (question.id)}
								<button type="button" class:current={active === index} aria-current={active === index ? 'step' : undefined} onclick={() => (active = index)}><span>{String(index + 1).padStart(2, '0')}</span><span>{question.prompt || TYPE_NAMES[question.type] || 'Soalan'}</span></button>
							{/each}
						</nav>
					</div>
					<div class="right-page">
						{#if opened.questions[active]}
							{@const question = opened.questions[active]}
							{@const key = visual(opened, question)}
							<div class="page-meta"><span>SOALAN {active + 1} / {opened.questions.length}</span><span>{TYPE_NAMES[question.type] || question.type}</span></div>
							<h3>{question.prompt || 'Lihat gambar dan jawab soalan.'}</h3>
							<figure class="diagram">
								<img src={diagramUrl(key)} alt={diagramOf(key)?.name || 'Gambar rujukan topik'} />
								<figcaption>{question.diagram === key || question.picture === key ? 'Rajah soalan' : 'Gambar rujukan topik'} Â· {diagramOf(key)?.credit || 'Wikimedia Commons'}</figcaption>
							</figure>
							{#if question.picture && !isDiagram(question.picture) && stickerOf(question.picture)}<div class="original-picture"><Sticker key={question.picture} size={60} /><span>Ilustrasi soalan: {stickerOf(question.picture)?.name}</span></div>{/if}
							<div class="page-turn"><button type="button" disabled={active === 0} onclick={() => (active -= 1)}>â† Sebelumnya</button><span>{active + 1} / {opened.questions.length}</span><button type="button" disabled={active === opened.questions.length - 1} onclick={() => (active += 1)}>Seterusnya â†’</button></div>
						{/if}
					</div>
				</div>
				{#if error}<p class="action-error" role="alert">{error}</p>{/if}
				<div class="book-actions"><a class="play" href={`/ibu-bapa/kuiz/${opened.id}/main`}>â–· &nbsp; Main bersama</a><button class="copy" type="button" disabled={copying} onclick={copy}>{copying ? 'Sedang menyalinâ€¦' : 'âœ§ &nbsp; Salin dan ubah'}</button></div>
			{/if}
		</div>
	{/if}
</dialog>

<style>
	.library { --ink:#25223a; --muted:#686176; color:var(--ink); display:grid; gap:2.2rem; padding-bottom:2rem; }
	.library-intro { display:flex; align-items:center; gap:1rem; padding:1rem 1.25rem; border:1px solid #e9dfd1; border-radius:20px; background:#fffaf0; }
	.library-mark { display:grid; place-items:center; width:44px; height:44px; border-radius:14px; color:#7652c8; background:#eee5ff; font-size:1.5rem; flex:none; }
	.library-intro strong { font:600 1.08rem/1.2 var(--font-display); }.library-intro p { margin:.18rem 0 0; font-size:.88rem; color:var(--muted); }.library-count { margin-left:auto; white-space:nowrap; font-size:.78rem; font-weight:800; color:#7652c8; }
	.shelf-heading { display:flex; align-items:center; gap:.9rem; margin-bottom:1.1rem; }.shelf-number { display:grid; place-items:center; min-width:58px; height:29px; border-radius:8px; background:#e9dbf9; color:#6244a1; font-size:.72rem; font-weight:900; }.shelf-heading h2 { margin:0; font:600 1.35rem/1.15 var(--font-display); }.shelf-heading p { margin:.15rem 0 0; color:var(--muted); font-size:.83rem; }.shelf-total { margin-left:auto; color:#8b8291; font-size:.76rem; font-weight:800; white-space:nowrap; }
	.book-row { display:grid; grid-template-columns:repeat(auto-fill,minmax(145px,1fr)); gap:1.1rem .9rem; align-items:end; padding:.25rem .8rem 0; }.book { --cover:#7455b8; --cover-dark:#4d317f; --cover-light:#ad91e5; position:relative; isolation:isolate; width:100%; height:240px; padding:0; border:0; background:none; text-align:left; cursor:pointer; perspective:700px; }.book.teal { --cover:#237f83; --cover-dark:#13555a; --cover-light:#8cd5ca; }.book.coral { --cover:#b4586b; --cover-dark:#823747; --cover-light:#f5a5aa; }.book:nth-child(3n+2) { height:228px; }.book:nth-child(4n+3) { height:250px; }.book-pages { position:absolute; inset:6px 0 2px 13px; border-radius:3px 12px 12px 3px; background:repeating-linear-gradient(90deg,#f5edda 0 2px,#e1d5bf 2px 3px); box-shadow:3px 4px 3px #634a4660; }.book-cover { position:absolute; inset:0 8px 0 0; display:flex; flex-direction:column; overflow:hidden; padding:12px 12px 11px 20px; border-radius:4px 12px 12px 4px; border:2px solid var(--cover-dark); color:#fffdf7; background:linear-gradient(125deg,var(--cover-dark),var(--cover) 19%,var(--cover) 78%,var(--cover-light)); box-shadow:4px 6px 8px #473a4e38,inset -5px 0 7px #382a493b,inset 0 0 0 5px #ffffff24; transform-origin:left center; transition:transform 260ms cubic-bezier(.23,1,.32,1),box-shadow 260ms cubic-bezier(.23,1,.32,1); }.book-cover:after { content:''; position:absolute; inset:8px; border:1px solid #ffffff75; border-radius:3px 8px 8px 3px; pointer-events:none; }.book-spine { position:absolute; inset:0 auto 0 0; width:12px; border-right:1px solid #ffffff69; background:#1f143233; box-shadow:2px 0 4px #140d2940; }.book-top,.book-bottom { display:flex; justify-content:space-between; align-items:center; font-size:.6rem; font-weight:900; letter-spacing:.09em; }.book-icon { font-size:1rem; line-height:1; }.cover-art { width:85px; height:72px; margin:.5rem auto .35rem; padding:5px; border:2px solid #ffffffa8; border-radius:8px; background:#fffaf0; object-fit:contain; box-shadow:0 3px 7px #1b122933; }.book-subject { font-size:.59rem; font-weight:900; letter-spacing:.1em; opacity:.86; }.book strong { display:-webkit-box; overflow:hidden; -webkit-line-clamp:3; line-clamp:3; -webkit-box-orient:vertical; margin:.17rem 0 auto; font:600 .88rem/1.15 var(--font-display); text-wrap:balance; }.book-bottom { margin-top:.5rem; padding-top:.5rem; border-top:1px solid #ffffff75; letter-spacing:0; }.book-bottom span:last-child { font-size:1rem; }.shelf-edge { position:relative; height:16px; border-radius:3px 3px 9px 9px; background:linear-gradient(#e8bd91 0 32%,#ad7655 33% 72%,#86553c 73%); box-shadow:0 8px 13px #51392c2b; }.shelf-edge:after { content:''; position:absolute; inset:auto 7% -6px; height:6px; border-radius:50%; background:#49372a24; filter:blur(4px); }.empty { padding:2rem; text-align:center; }
	@media (hover:hover) and (pointer:fine) { .book:hover .book-cover { transform:rotateY(-13deg) translateX(2px); box-shadow:8px 9px 14px #473a4e48; } }.book:focus-visible { outline:3px solid #6647d9; outline-offset:5px; border-radius:8px; }
	.book-dialog { width:min(960px,calc(100vw - 24px)); max-height:min(88vh,850px); padding:0; border:0; border-radius:18px; color:#2c2a3b; background:#fffaf1; box-shadow:0 30px 85px #21192f6b; animation:book-open 260ms cubic-bezier(.23,1,.32,1) both; }.book-dialog::backdrop { background:#171221aa; backdrop-filter:blur(4px); }.open-book { min-height:440px; }.book-dialog-header { display:flex; justify-content:space-between; align-items:center; height:52px; padding:0 1.25rem; color:#fff; background:#62479c; font-size:.73rem; font-weight:900; letter-spacing:.12em; }.close { width:34px; height:34px; border:0; border-radius:50%; color:#fff; background:#ffffff30; font-size:1.55rem; line-height:1; cursor:pointer; }.spread { display:grid; grid-template-columns:1fr 1fr; max-height:calc(88vh - 126px); min-height:355px; }.left-page,.right-page { min-width:0; padding:1.5rem 1.6rem; overflow:auto; }.left-page { background:#f6eddb; box-shadow:inset -10px 0 12px -12px #72584666; }.right-page { background:#fffdf8; box-shadow:inset 10px 0 12px -12px #72584666; }.eyebrow,.page-meta { color:#8a6282; font-size:.7rem; font-weight:900; letter-spacing:.09em; }.left-page h2 { margin:.65rem 0 .4rem; font:600 clamp(1.35rem,3vw,1.8rem)/1.12 var(--font-display); }.book-description { margin:.5rem 0 1.2rem; color:#675d68; font-size:.86rem; line-height:1.5; }.contents-title { display:flex; justify-content:space-between; padding-bottom:.5rem; border-bottom:1px solid #b9a98d; font-weight:900; }.contents-title span { color:#83776d; font-size:.74rem; font-weight:700; }.question-list { display:grid; gap:.25rem; margin-top:.4rem; }.question-list button { display:flex; gap:.6rem; align-items:start; width:100%; padding:.55rem .65rem; border:0; border-radius:9px; color:#403644; background:transparent; text-align:left; font:700 .83rem/1.3 var(--font-body); cursor:pointer; }.question-list button span:first-child { color:#9a7192; font-weight:900; }.question-list button.current { background:#e9d7ef; color:#51296d; }.question-list button:hover { background:#eee1df; }.page-meta { display:flex; justify-content:space-between; gap:.5rem; }.right-page h3 { margin:1.1rem 0; font:600 clamp(1.2rem,2.6vw,1.55rem)/1.25 var(--font-display); }.diagram { display:grid; place-items:center; gap:.45rem; min-height:190px; margin:0; padding:1rem; border:1px solid #eadbc4; border-radius:14px; background:#fff9ec; }.diagram img { display:block; width:100%; max-width:340px; height:min(25vh,225px); object-fit:contain; border-radius:6px; }.diagram figcaption { color:#766c69; font-size:.67rem; text-align:center; }.original-picture { display:flex; align-items:center; gap:.5rem; margin-top:.5rem; font-size:.73rem; color:#675d68; }.page-turn { display:flex; align-items:center; justify-content:space-between; gap:.5rem; margin-top:1rem; font-size:.75rem; color:#83776d; }.page-turn button { padding:.4rem .5rem; border:0; border-radius:7px; color:#62479c; background:#eee6f5; font-weight:800; cursor:pointer; }.page-turn button:disabled { opacity:.35; cursor:default; }.book-actions { display:flex; justify-content:flex-end; gap:.6rem; padding:.75rem 1.2rem; border-top:1px solid #e7d9c8; background:#fffaf1; }.book-actions a,.book-actions button { display:inline-flex; align-items:center; justify-content:center; padding:.65rem 1rem; border:0; border-radius:10px; font:800 .85rem/1 var(--font-body); text-decoration:none; cursor:pointer; }.play { color:#fff; background:#f23b78; }.copy { color:#574080; background:#ece4fa; }.copy:disabled { opacity:.55; }.loading { display:grid; place-content:center; min-height:360px; text-align:center; }.loading-book { font-size:3rem; }.action-error { margin:.5rem 1rem 0; color:#b02444; font-size:.8rem; }.book-dialog button:focus-visible,.book-dialog a:focus-visible { outline:3px solid #6e45cb; outline-offset:2px; }
	@keyframes book-open { from { opacity:0; transform:perspective(1000px) rotateY(-8deg) scale(.97); } to { opacity:1; transform:perspective(1000px) rotateY(0) scale(1); } }
	@media (max-width:650px) { .library-intro { flex-wrap:wrap; }.library-count { width:100%; margin-left:58px; }.book-row { grid-template-columns:repeat(auto-fill,minmax(125px,1fr)); gap:.8rem; padding-inline:.35rem; }.book { height:210px; }.book:nth-child(3n+2) { height:205px; }.book:nth-child(4n+3) { height:218px; }.book-cover { padding:10px 9px 9px 17px; }.cover-art { width:70px; height:59px; }.book strong { font-size:.8rem; }.shelf-total { display:none; }.spread { grid-template-columns:1fr; max-height:calc(88vh - 126px); }.left-page { max-height:185px; padding:1rem; box-shadow:inset 0 -9px 10px -11px #72584666; }.left-page h2 { margin:.3rem 0; }.book-description { display:none; }.contents-title { display:none; }.question-list { display:flex; gap:.35rem; overflow-x:auto; }.question-list button { flex:none; width:auto; max-width:170px; }.question-list button span:last-child { overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }.right-page { padding:1rem; }.book-actions { justify-content:stretch; }.book-actions a,.book-actions button { flex:1; padding:.65rem .45rem; font-size:.76rem; } }
	@media (prefers-reduced-motion:reduce) { .book-cover { transition:none; }.book-dialog { animation:none; } }
</style>

