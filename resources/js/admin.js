import Alpine from 'alpinejs';
import questionEditor from './admin/question-editor';
import linkList from './admin/link-list';
import { initDialogs } from './lib/dialogs';

Alpine.data('questionEditor', questionEditor);
Alpine.data('linkList', linkList);

window.Alpine = Alpine;
Alpine.start();

initDialogs();
