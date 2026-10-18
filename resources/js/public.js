import Alpine from '@alpinejs/csp';
import liveQuestion from './live-question';
import quizPlayer from './player/quiz-player';
import { initDialogs } from './lib/dialogs';
import { initDisclosures } from './lib/disclosure';

// Alpine's CSP build: no eval, so the Content-Security-Policy needs no 'unsafe-eval'. Component logic
// lives in Alpine.data() methods and getters and templates call them by name; the CSP build only
// understands simple expressions (no arrow functions, no template literals, no globals like JSON),
// so data reaches a component as a plain object literal (see the @literal Blade directive).
Alpine.data('liveQuestion', liveQuestion);
Alpine.data('quizPlayer', quizPlayer);

window.Alpine = Alpine;
Alpine.start();

initDialogs();
initDisclosures();
