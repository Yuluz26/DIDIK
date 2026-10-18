import Alpine from '@alpinejs/csp';
import questionEditor from './admin/question-editor';
import linkList from './admin/link-list';
import { initDialogs } from './lib/dialogs';

Alpine.data('conceptPicker', (initial) => ({ concept: initial }));
Alpine.data('questionEditor', questionEditor);
Alpine.data('linkList', linkList);

window.Alpine = Alpine;
Alpine.start();

initDialogs();
