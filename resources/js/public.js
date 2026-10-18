import Alpine from 'alpinejs';
import liveQuestion from './live-question';
import quizPlayer from './player/quiz-player';
import { initDialogs } from './lib/dialogs';
import { initDisclosures } from './lib/disclosure';

// Component logic lives in Alpine.data() methods and getters, with templates calling those by
// name. That keeps every expression simple enough for Alpine's CSP build, should a strict
// Content-Security-Policy be turned on in production.
Alpine.data('liveQuestion', liveQuestion);
Alpine.data('quizPlayer', quizPlayer);

window.Alpine = Alpine;
Alpine.start();

initDialogs();
initDisclosures();
