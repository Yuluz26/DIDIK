// The sign-in page: an email, then the six-digit code sent to it. Nothing here knows who the owner is.
const $ = (id) => document.getElementById(id);
const ask = $('ask');
const check = $('check');
const error = $('error');
const COOLDOWN = 60;
const BASE = document.documentElement.dataset.base;

let email = '';
let timer = 0;

function fail(message) {
	error.textContent = message;
	error.hidden = !message;
}

async function post(path, body) {
	const response = await fetch(path, {
		method: 'POST',
		headers: { 'content-type': 'application/json', 'x-didik-admin': '1' },
		body: JSON.stringify(body),
		credentials: 'same-origin'
	});
	const data = await response.json().catch(() => ({}));
	if (!response.ok) throw new Error(data.message || 'Sesuatu tidak kena. Cuba lagi.');
	return data;
}

function busy(form, on) {
	const button = form.querySelector('.go');
	button.disabled = on;
}

function countdown() {
	const resend = $('resend');
	let left = COOLDOWN;
	resend.disabled = true;
	clearInterval(timer);
	const tick = () => {
		resend.textContent = left > 0 ? `Hantar semula (${left}s)` : 'Hantar semula';
		if (left <= 0) {
			resend.disabled = false;
			clearInterval(timer);
		}
		left -= 1;
	};
	tick();
	timer = setInterval(tick, 1000);
}

function toCode() {
	ask.hidden = true;
	check.hidden = false;
	$('title').textContent = 'Semak emel anda';
	$('lead').textContent = 'Kami hantar kod 6 digit jika emel itu dibenarkan.';
	$('code').value = '';
	$('code').focus();
	countdown();
}

async function send() {
	fail('');
	busy(ask, true);
	try {
		await post(`${BASE}/api/otp`, { email });
		toCode();
	} catch (problem) {
		fail(problem.message);
	} finally {
		busy(ask, false);
	}
}

ask.addEventListener('submit', (event) => {
	event.preventDefault();
	email = $('email').value.trim();
	if (!email) return fail('Masukkan emel anda.');
	send();
});

check.addEventListener('submit', async (event) => {
	event.preventDefault();
	const code = $('code').value.replace(/\D/g, '');
	if (code.length !== 6) return fail('Kod mesti 6 digit.');
	fail('');
	busy(check, true);
	try {
		await post(`${BASE}/api/verify`, { email, code });
		location.reload();
	} catch (problem) {
		fail(problem.message);
		$('code').select();
		busy(check, false);
	}
});

$('code').addEventListener('input', (event) => {
	const digits = event.target.value.replace(/\D/g, '').slice(0, 6);
	event.target.value = digits;
	if (digits.length === 6) check.requestSubmit();
});

$('resend').addEventListener('click', async () => {
	fail('');
	try {
		await post(`${BASE}/api/otp`, { email });
		countdown();
		$('code').focus();
	} catch (problem) {
		fail(problem.message);
	}
});

$('change').addEventListener('click', () => {
	clearInterval(timer);
	fail('');
	check.hidden = true;
	ask.hidden = false;
	$('title').textContent = 'Bilik kawalan';
	$('lead').textContent = 'Masukkan emel anda. Kod 6 digit akan dihantar ke sana.';
	$('email').focus();
});

$('email').focus();
