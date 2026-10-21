// "Bacakan soalan": the browser's own voice reads the question aloud, for children who cannot read
// fluently yet. Malay voice when the device has one, otherwise Indonesian, which is close.

export function canSpeak(): boolean {
	return typeof window !== 'undefined' && 'speechSynthesis' in window;
}

function voice(): SpeechSynthesisVoice | undefined {
	const voices = window.speechSynthesis.getVoices();
	return (
		voices.find((v) => v.lang.toLowerCase().startsWith('ms')) ??
		voices.find((v) => v.lang.toLowerCase().startsWith('id'))
	);
}

export function speak(text: string): void {
	if (!canSpeak()) return;
	window.speechSynthesis.cancel();
	const utterance = new SpeechSynthesisUtterance(text);
	const chosen = voice();
	if (chosen) utterance.voice = chosen;
	utterance.lang = chosen?.lang ?? 'ms-MY';
	utterance.rate = 0.92;
	window.speechSynthesis.speak(utterance);
}

export function stopSpeaking(): void {
	if (canSpeak()) window.speechSynthesis.cancel();
}
