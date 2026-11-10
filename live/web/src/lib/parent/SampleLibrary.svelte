<script lang="ts">
	import { api } from '$lib/api';
	import './SampleLibrary.css';
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
		const islam = quizzes.filter((q) => q.title.startsWith('Pendidikan Islam') && !q.title.includes('Menengah'));
		const primary = quizzes.filter((q) => !islam.includes(q) && !/Menengah|Tingkatan/.test(q.title));
		const secondary = quizzes.filter((q) => !islam.includes(q) && !primary.includes(q));
		return [
			{ key: 'islam', title: 'Pendidikan Islam · topik KAFA', subtitle: 'Akhlak, ibadah dan sirah untuk sekolah rendah', badge: 'Buku 01', color: 'plum', books: islam },
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
		<span class="library-mark" aria-hidden="true">✦</span>
		<div><strong>Jelajah rak buku</strong><p>Pilih sebuah buku, selak soalan, kemudian main atau salin untuk kelas anda.</p></div>
		<span class="library-count">{quizzes.length} buku · {quizzes.reduce((n, q) => n + q.questionCount, 0)} soalan</span>
	</div>
	{#if !quizzes.length && parent.loading}<p class="empty">Sedang menyusun buku di rak…</p>{/if}
	{#each sections as section (section.key)}
		<section class="shelf" aria-labelledby="heading-{section.key}">
			<div class="shelf-heading"><span class="shelf-number">{section.badge}</span><div><h2 id="heading-{section.key}">{section.title}</h2><p>{section.subtitle}</p></div><span class="shelf-total">{section.books.length} koleksi</span><span class="shelf-swipe">Leret rak untuk lihat lagi →</span></div>
			<div class="book-row">
				{#each section.books as quiz (quiz.id)}
					<button class="book {section.color}" type="button" onclick={() => open(quiz)} aria-label="Buka buku {quiz.title}, {quiz.questionCount} soalan">
						<span class="book-pages" aria-hidden="true"></span>
						<span class="book-cover">
							<span class="book-spine" aria-hidden="true"></span>
							<span class="book-top"><span class="book-icon" aria-hidden="true">✿</span><span>DIDIK LIBRARY</span></span>
							<img class="cover-art" src={diagramUrl(visual(quiz))} alt="" loading="lazy" />
							<span class="book-subject">{label(quiz)}</span>
							<strong>{quiz.title}</strong>
							<span class="book-bottom"><span>{quiz.questionCount} soalan</span><span aria-hidden="true">↗</span></span>
						</span>
					</button>
				{/each}
			</div>
		</section>
	{/each}
</div>

<dialog bind:this={dialog} class="book-dialog" aria-label={selected ? `Buku ${selected.title}` : 'Buku soalan'} onclose={() => { requestId++; selected = null; opened = null; }} onclick={(event) => { if (event.target === dialog) close(); }}>
	{#if selected}
		<div class="open-book">
			<header class="book-dialog-header"><span>✿ &nbsp; PERPUSTAKAAN DIDIK</span><button type="button" class="close" onclick={close} aria-label="Tutup buku">×</button></header>
			{#if loading}<div class="loading"><span class="loading-book" aria-hidden="true">📖</span><p>Sedang membuka buku…</p></div>
			{:else if error && !opened}<div class="loading"><p role="alert">{error}</p><button type="button" onclick={() => open(selected!)}>Cuba lagi</button></div>
			{:else if opened}
				<div class="spread">
					<div class="left-page">
						<span class="eyebrow">{label(opened)} · {opened.questionCount} SOALAN</span>
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
								<figcaption>{question.diagram === key || question.picture === key ? 'Rajah soalan' : 'Gambar rujukan topik'} · {diagramOf(key)?.credit || 'Wikimedia Commons'}</figcaption>
							</figure>
							{#if question.picture && !isDiagram(question.picture) && stickerOf(question.picture)}<div class="original-picture"><Sticker key={question.picture} size={60} /><span>Ilustrasi soalan: {stickerOf(question.picture)?.name}</span></div>{/if}
							<div class="page-turn"><button type="button" disabled={active === 0} onclick={() => (active -= 1)}>← Sebelumnya</button><span>{active + 1} / {opened.questions.length}</span><button type="button" disabled={active === opened.questions.length - 1} onclick={() => (active += 1)}>Seterusnya →</button></div>
						{/if}
					</div>
				</div>
				{#if error}<p class="action-error" role="alert">{error}</p>{/if}
				<div class="book-actions"><a class="play" href={`/ibu-bapa/kuiz/${opened.id}/main`}>▷ &nbsp; Main bersama</a><button class="copy" type="button" disabled={copying} onclick={copy}>{copying ? 'Sedang menyalin…' : '✧ Salin dan ubah'}</button></div>
			{/if}
		</div>
	{/if}
</dialog>
