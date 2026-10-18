/**
 * The question editor. All questions of a quiz live on one page and are saved together.
 * The page is an ordinary form: every field below renders real inputs named
 * questions[i][...], so saving needs no extra script, and server-side validation errors
 * come back through the same names.
 *
 * Reordering uses buttons, not dragging, so it works by keyboard and with a single pointer.
 */
export default function questionEditor(config) {
    let nextKey = 1;

    const option = (data = {}) => ({ key: nextKey++, id: data.id ?? null, body: data.body ?? '' });

    const question = (data = {}) => ({
        key: nextKey++,
        id: data.id ?? null,
        type: data.type ?? 'single',
        body: data.body ?? '',
        explanation: data.explanation ?? '',
        points: Number(data.points ?? 1) || 1,
        correct: Number(data.correct ?? 0) || 0,
        options: (data.options ?? []).map(option),
    });

    return {
        questions: (config.questions ?? []).map(question),
        errors: config.errors ?? {},
        max: config.max,
        dirty: false,
        submitting: false,
        removing: null,

        init() {
            window.addEventListener('beforeunload', (event) => {
                if (this.dirty && !this.submitting) {
                    event.preventDefault();
                    event.returnValue = '';
                }
            });
        },

        // ------------------------------------------------------------ reading

        get total() {
            return this.questions.length;
        },

        get canAdd() {
            return this.total < this.max;
        },

        get isEmpty() {
            return this.total === 0;
        },

        get stateText() {
            return this.dirty ? config.strings.dirty : config.strings.clean;
        },

        get dirtyFlag() {
            return this.dirty ? 'true' : 'false';
        },

        get removeTitle() {
            return config.strings.removeTitle.replace(':number', (this.removing ?? 0) + 1);
        },

        isTrueFalse(q) {
            return q.type === 'truefalse';
        },

        isSingle(q) {
            return q.type === 'single';
        },

        canAddOption(q) {
            return q.options.length < 5;
        },

        canRemoveOption(q) {
            return q.options.length > 2;
        },

        isFirst(i) {
            return i === 0;
        },

        isLast(i) {
            return i === this.questions.length - 1;
        },

        letter(j) {
            return String.fromCharCode(65 + j);
        },

        // ------------------------------------------------------------ form names, ids and errors

        name(i, ...path) {
            return `questions[${i}]` + path.map((part) => `[${part}]`).join('');
        },

        fieldId(i, field) {
            return `q-${i}-${field}`;
        },

        errorFor(i, field) {
            return (this.errors[`questions.${i}.${field}`] ?? [])[0] ?? '';
        },

        hasError(i, field) {
            return this.errorFor(i, field) !== '';
        },

        optionError(i, j) {
            return this.errorFor(i, `options.${j}.body`);
        },

        // ------------------------------------------------------------ editing

        markDirty() {
            this.dirty = true;
        },

        addQuestion(type = 'single') {
            if (!this.canAdd) {
                return;
            }

            const fresh = question({ type, options: type === 'single' ? [{}, {}, {}] : [] });
            this.questions.push(fresh);
            this.markDirty();
            this.focusQuestion(this.questions.length - 1);
        },

        addTrueFalse() {
            this.addQuestion('truefalse');
        },

        duplicate(i) {
            if (!this.canAdd) {
                return;
            }

            const source = this.questions[i];
            const copy = question({
                ...source,
                id: null,
                options: source.options.map((o) => ({ body: o.body })),
            });

            this.questions.splice(i + 1, 0, copy);
            this.markDirty();
            this.focusQuestion(i + 1);
        },

        move(i, step) {
            const target = i + step;

            if (target < 0 || target >= this.questions.length) {
                return;
            }

            const [moved] = this.questions.splice(i, 1);
            this.questions.splice(target, 0, moved);
            this.markDirty();
            this.focusQuestion(target);
        },

        askRemove(i) {
            this.removing = i;
            this.$refs.removeDialog.showModal();
        },

        confirmRemove() {
            if (this.removing !== null) {
                this.questions.splice(this.removing, 1);
                this.markDirty();
            }

            this.removing = null;
            this.$refs.removeDialog.close();
        },

        setType(q, type) {
            q.type = type;
            q.correct = 0;

            // Back to multiple choice from true/false: there are no options to show yet.
            if (type === 'single' && q.options.length < 2) {
                q.options = [option(), option(), option()];
            }

            this.markDirty();
        },

        addOption(q) {
            if (this.canAddOption(q)) {
                q.options.push(option());
                this.markDirty();
            }
        },

        removeOption(q, j) {
            if (!this.canRemoveOption(q)) {
                return;
            }

            q.options.splice(j, 1);

            // Keep "correct" pointing at the same answer, or at the first one if it was removed.
            if (j === q.correct) {
                q.correct = 0;
            } else if (j < q.correct) {
                q.correct -= 1;
            }

            this.markDirty();
        },

        optionLabel(j) {
            return config.strings.option.replace(':letter', this.letter(j));
        },

        correctLabel(j) {
            return config.strings.correctFor.replace(':letter', this.letter(j));
        },

        removeOptionLabel(j) {
            return config.strings.removeOption.replace(':letter', this.letter(j));
        },

        questionLabel(i) {
            return config.strings.questionN.replace(':number', i + 1);
        },

        focusQuestion(i) {
            this.$nextTick(() => document.getElementById(this.fieldId(i, 'body'))?.focus());
        },

        submit() {
            this.submitting = true;
        },
    };
}
