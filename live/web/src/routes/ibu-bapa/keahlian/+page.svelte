<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import DashShell from '$lib/parent/DashShell.svelte';
	import { session } from '$lib/session.svelte';

	type Plan = 'free' | 'premium' | 'family';
	type Interval = 'monthly' | 'yearly';
	type Child = { id: number; name: string; schoolYear: number | null; selected: boolean };
	type Payment = { reference: string; plan: Plan; interval: Interval; amountSen: number; status: string; createdAt: string };
	type State = {
		membership: { plan: Plan; source: string; interval: Interval | null; expiresAt: string | null; childLimit: number; selectedChildId: number | null };
		children: Child[];
		payments: Payment[];
		pricesSen: { free: { monthly: number; yearly: number }; premium: { monthly: number; yearly: number }; family: { monthly: number; yearly: number } };
		billing: { qrImage: string | null; payeeName: string; instructions: string; whatsapp: string };
	};
	let data = $state<State | null>(null);
	let busy = $state(false);
	let error = $state('');
	let childName = $state('');
	let schoolYear = $state('');
	let interval = $state<Interval>('monthly');
	let checkoutPlan = $state<Plan | null>(null);
	let checkoutReference = $state('');
	const names: Record<Plan, string> = { free: 'DIDIK Free', premium: 'DIDIK Premium', family: 'DIDIK Family' };
	const money = (sen: number) => `RM${(sen / 100).toFixed(2)}`;
	const when = (value: string) => new Intl.DateTimeFormat('ms-MY', { dateStyle: 'medium' }).format(new Date(value));
	const message = (reference: string) => `Salam DIDIK, saya sudah bayar keahlian. Rujukan: ${reference}. Saya akan hantar bukti bayaran di sini.`;
	const whatsapp = (reference: string) => `https://wa.me/${data?.billing.whatsapp ?? '60139558132'}?text=${encodeURIComponent(message(reference))}`;

	async function refresh() {
		try { data = await api.get<State>('/api/membership/me'); error = ''; }
		catch (problem) { error = problem instanceof Error ? problem.message : 'Maklumat keahlian tidak dapat dimuat.'; }
	}
	onMount(() => { void refresh(); });
	async function addChild() {
		if (!childName.trim() || busy) return;
		busy = true;
		try {
			await api.post('/api/membership/children', { name: childName.trim(), school_year: schoolYear ? Number(schoolYear) : null });
			childName = ''; schoolYear = ''; await refresh();
		} catch (problem) { error = problem instanceof Error ? problem.message : 'Profil tidak dapat disimpan.'; }
		finally { busy = false; }
	}
	async function selectChild(id: number) {
		try { await api.post(`/api/membership/children/${id}/select`); await refresh(); }
		catch (problem) { error = problem instanceof Error ? problem.message : 'Profil tidak dapat dipilih.'; }
	}
	async function checkout(plan: 'premium' | 'family') {
		if (busy) return;
		busy = true; error = '';
		try {
			const payment = await api.post<Payment>('/api/membership/checkout', { plan, interval });
			checkoutPlan = plan; checkoutReference = payment.reference; await refresh();
		} catch (problem) { error = problem instanceof Error ? problem.message : 'Permintaan bayaran tidak dapat dibuat.'; }
		finally { busy = false; }
	}
</script>

<svelte:head><title>Keahlian · DIDIK</title></svelte:head>
<DashShell>
	<div class="member">
		<header class="intro"><div><h1>Keahlian DIDIK</h1><p>Pilih ruang belajar yang sesuai untuk keluarga anda.</p></div><a href="/ibu-bapa/akaun">Akaun saya</a></header>
		{#if error}<p class="alert" role="alert">{error}</p>{/if}
		{#if !data}<p aria-busy="true">Memuatkan keahlian…</p>{:else}
			<section class="current" aria-label="Keahlian semasa">
				<div><span>Pelan semasa</span><h2>{names[data.membership.plan]}</h2><p>{data.membership.source === 'complimentary' ? 'Akses percuma daripada admin' : data.membership.source === 'paid' ? 'Keahlian berbayar' : 'Percuma selamanya'}{data.membership.expiresAt ? ` · Tamat ${when(data.membership.expiresAt)}` : ''}</p></div>
				<span class="capacity">{data.children.length} / {data.membership.childLimit} profil anak</span>
			</section>
			<section class="profiles"><div class="section-head"><h2>Profil anak</h2><p>Setiap anak menyimpan ruang pembelajarannya sendiri.</p></div>
				{#if data.children.length}<ul>{#each data.children as child}<li><div><strong>{child.name}</strong><small>{child.schoolYear ? `Tahun ${child.schoolYear}` : 'Tahun belum ditetapkan'}</small></div>{#if child.selected}<span class="selected">Sedang digunakan</span>{:else}<button type="button" onclick={() => selectChild(child.id)}>Pilih profil</button>{/if}</li>{/each}</ul>{:else}<p>Belum ada profil anak. Tambah satu untuk mula belajar.</p>{/if}
				{#if data.children.length < data.membership.childLimit}<form onsubmit={(event) => { event.preventDefault(); void addChild(); }}><label>Nama panggilan anak<input bind:value={childName} maxlength="60" required /></label><label>Tahun sekolah<select bind:value={schoolYear}><option value="">Pilih jika mahu</option>{#each [1,2,3,4,5,6] as year}<option value={year}>Tahun {year}</option>{/each}</select></label><button disabled={busy}>Tambah profil</button></form>{/if}
				{#if data.children.length > data.membership.childLimit}<p class="notice">Pelan semasa membenarkan satu profil aktif. Pilih profil yang hendak digunakan; profil dan sejarah lain disimpan.</p>{/if}
			</section>
			<section class="plans"><div class="section-head"><h2>Pelan untuk keluarga</h2><p>Harga rasmi dalam Ringgit Malaysia. Bayaran sekali bagi setiap tempoh; pembaharuan dibuat secara manual.</p></div><div class="toggle" role="group" aria-label="Tempoh bayaran"><button class:active={interval === 'monthly'} onclick={() => interval = 'monthly'}>Bulanan</button><button class:active={interval === 'yearly'} onclick={() => interval = 'yearly'}>Tahunan</button></div><div class="plan-grid">
				<article><h3>DIDIK Free</h3><p class="price">{money(data.pricesSen.free.monthly)} <small>selamanya</small></p><ul><li>1 profil anak</li><li>Kuiz contoh asas</li><li>Kuiz Interaktif asas</li><li>Keputusan kuiz asas</li></ul><span class="tag">Tersedia tanpa bayaran</span></article>
				<article class="featured"><h3>DIDIK Premium</h3><p class="price">{money(data.pricesSen.premium[interval])} <small>/{interval === 'monthly' ? 'bulan' : 'tahun'}</small></p><ul><li>1 profil anak</li><li>Semua kuiz interaktif</li><li>14 permainan 2D dan Hikayat Lima Alam</li><li>Hos bilik multiplayer</li></ul><button disabled={!data.billing.qrImage || busy} onclick={() => checkout('premium')}>Pilih Premium</button></article>
				<article><h3>DIDIK Family</h3><p class="price">{money(data.pricesSen.family[interval])} <small>/{interval === 'monthly' ? 'bulan' : 'tahun'}</small></p><ul><li>Sehingga 3 profil anak</li><li>Semua ciri Premium</li><li>Ruang belajar setiap anak</li><li>Story Mode Solo dan Party</li></ul><button disabled={!data.billing.qrImage || busy} onclick={() => checkout('family')}>Pilih Family</button></article>
			</div>{#if !data.billing.qrImage}<p class="notice">Pembayaran QR belum dibuka. Admin sedang menyediakan kod QR.</p>{/if}</section>
			{#if checkoutReference}<section class="checkout" aria-live="polite"><h2>Bayar {names[checkoutPlan ?? 'premium']}</h2><p>Rujukan anda: <strong>{checkoutReference}</strong>. Bayar jumlah tepat {money(data.payments.find((p) => p.reference === checkoutReference)?.amountSen ?? 0)}, kemudian hantar bukti melalui WhatsApp. Keahlian aktif selepas admin menyemak bayaran.</p>{#if data.billing.qrImage}<img src={data.billing.qrImage} alt="Kod QR bayaran DIDIK" />{/if}<p>{data.billing.payeeName}</p><p>{data.billing.instructions}</p><a class="wa" href={whatsapp(checkoutReference)} target="_blank" rel="noopener noreferrer">Hantar bukti di WhatsApp</a></section>{/if}
			<section class="history"><h2>Sejarah bayaran</h2>{#if data.payments.length}<ul>{#each data.payments as payment}<li><span><strong>{payment.reference}</strong><small>{names[payment.plan]} · {payment.interval === 'monthly' ? 'Bulanan' : 'Tahunan'} · {when(payment.createdAt)}</small></span><span>{money(payment.amountSen)} · {payment.status === 'paid' ? 'Disahkan' : payment.status === 'rejected' ? 'Ditolak' : 'Menunggu semakan'}</span>{#if payment.status === 'pending'}<a href={whatsapp(payment.reference)} target="_blank" rel="noopener noreferrer">Hantar bukti</a>{/if}</li>{/each}</ul>{:else}<p>Belum ada permintaan bayaran.</p>{/if}</section>
		{/if}
	</div>
</DashShell>

<style>
	.member{display:grid;gap:2rem;max-width:76rem;margin:auto;padding-bottom:4rem;color:var(--nm-ink,#2b2f45)}
	.intro,.current,.section-head{display:flex;align-items:start;justify-content:space-between;gap:1rem}.intro h1{font:700 clamp(2rem,4vw,3rem)/1.1 var(--font-display);margin:0}.intro p,.section-head p,.current p{color:var(--nm-ink-2,#606780)}
	.member h2{font:700 1.5rem var(--font-display);margin:.1rem 0}.member h3{font:700 1.4rem var(--font-display);margin:0}.member button,.wa{border:0;border-radius:12px;background:#7054d8;color:white;padding:.8rem 1.1rem;font:700 1rem var(--font-body);cursor:pointer;text-decoration:none;display:inline-block}.member button:disabled{opacity:.5;cursor:not-allowed}.member button:focus-visible,.member a:focus-visible,.member input:focus-visible,.member select:focus-visible{outline:3px solid #de568b;outline-offset:3px}.intro a{color:#5840bd}
	.current,.profiles,.plans,.checkout,.history{border-radius:16px;background:#f7f8fc;padding:clamp(1.25rem,3vw,2rem);box-shadow:7px 7px 20px #a3acc654,-7px -7px 20px #ffffff}.current{background:#e8e2ff}.current span:first-child{font-size:.85rem;font-weight:800;color:#5840bd}.capacity,.selected,.tag{border-radius:99px;background:#fff;padding:.4rem .75rem;font-size:.85rem;font-weight:800;white-space:nowrap}.section-head{margin-bottom:1rem}.section-head p{margin:.2rem 0}
	.profiles ul,.history ul{list-style:none;padding:0;margin:1rem 0;display:grid;gap:.7rem}.profiles li,.history li{display:flex;align-items:center;justify-content:space-between;gap:1rem;background:#fff;border-radius:12px;padding:.8rem 1rem}.profiles li div,.history li span:first-child{display:grid}.member small{color:#626985}.profiles form{display:flex;flex-wrap:wrap;align-items:end;gap:.8rem}.profiles label{display:grid;gap:.3rem;font-weight:700}.profiles input,.profiles select{min-height:2.7rem;border:1px solid #aaa9bd;border-radius:9px;padding:.45rem .6rem;background:white;color:inherit}.profiles li button{background:#ebe6ff;color:#4e35ad}
	.toggle{display:flex;gap:.35rem;margin:1rem 0}.toggle button{background:#e6e0f5;color:#4e35ad}.toggle button.active{background:#7054d8;color:white}.plan-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1rem}.plan-grid article{display:flex;flex-direction:column;gap:1rem;background:white;padding:1.5rem;border-radius:14px}.plan-grid article.featured{background:#eee9ff}.price{font:700 2rem var(--font-display);margin:0}.price small{font:600 .9rem var(--font-body)}.plan-grid ul{padding-left:1.25rem;line-height:1.8;flex:1}.plan-grid .tag{align-self:start;background:#eee9ff}.notice,.alert{border-radius:10px;background:#fff1d8;padding:.8rem 1rem}.alert{background:#ffe0e5;color:#7a1733}.checkout img{display:block;width:min(100%,240px);height:auto;margin:1rem 0;border-radius:10px}.checkout p{max-width:65ch}.wa{background:#167a53}.history li{flex-wrap:wrap}.history a{color:#5840bd}
	@media(max-width:800px){.plan-grid{grid-template-columns:1fr}.intro,.current,.section-head{flex-direction:column}.member{gap:1.25rem}.profiles li,.history li{align-items:start;flex-wrap:wrap}}
</style>
