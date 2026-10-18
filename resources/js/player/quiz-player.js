import { postJson } from '../lib/http';

/**
 * The quiz player. One engine for every game concept: the concepts only differ in the Blade
 * views that read this state (dots, star slots, river path), never in how answers are handled.
 *
 * The browser is never told which option is correct before it has answered. Every answer goes
 * to the server, which checks it. Templates call the getters and methods below by name, so every
 * expression stays simple enough for Alpine's CSP build.
 */
export default function quizPlayer(config) {
    return {
        // Fixed for the page
        strings: config.strings,
        settings: config.settings,
        conceptKey: config.concept,
        lang: config.lang,
        quizUrl: config.quizUrl,
        startUrl: config.startUrl,

        // Loaded from the server
        feedbackMode: 'instant',
        questions: [],
        answers: {}, // question id -> { option_id, correct?, correct_option_id?, explanation? }
        answerUrl: '',
        resultUrl: '',

        // Where the child is
        phase: 'loading', // loading | question | feedback | checkpoint | error
        errorKind: '', // load | exhausted | unavailable
        answerFailed: false,
        index: 0,
        selectedId: null,
        busy: false,
        streak: 0,
        finished: false,

        // ---------------------------------------------------------------- loading

        async start(restart = false) {
            this.phase = 'loading';
            this.errorKind = '';

            try {
                const state = await postJson(this.startUrl, { restart });

                if (state.finished) {
                    window.location.assign(state.urls.result);
                    return;
                }

                this.feedbackMode = state.feedback_mode;
                this.questions = state.questions;
                this.answers = Array.isArray(state.answers) ? {} : state.answers;
                this.answerUrl = state.urls.answer;
                this.resultUrl = state.urls.result;

                // Resume at the first question that has no answer yet.
                const next = this.questions.findIndex((question) => !(question.id in this.answers));
                this.index = next === -1 ? this.questions.length - 1 : next;
                this.streak = this.countStreak();
                this.phase = 'question';
                this.focusQuestion();
            } catch (error) {
                this.errorKind = { 403: 'exhausted', 404: 'unavailable' }[error.status] ?? 'load';
                this.phase = 'error';
            }
        },

        retry() {
            this.start();
        },

        // ---------------------------------------------------------------- reading state

        get isLoading() {
            return this.phase === 'loading';
        },

        get hasError() {
            return this.phase === 'error';
        },

        get showQuestion() {
            return this.phase === 'question' || this.phase === 'feedback';
        },

        get showFeedback() {
            return this.phase === 'feedback';
        },

        get isCheckpoint() {
            return this.phase === 'checkpoint';
        },

        get isInstant() {
            return this.feedbackMode === 'instant';
        },

        get total() {
            return this.questions.length;
        },

        get current() {
            return this.questions[this.index] ?? { id: 0, body: '', options: [] };
        },

        get currentAnswer() {
            return this.answers[this.current.id] ?? null;
        },

        get answeredCount() {
            return Object.keys(this.answers).length;
        },

        get isLastQuestion() {
            return this.index >= this.total - 1;
        },

        get positionText() {
            return this.fill(this.strings.questionOf, { current: this.index + 1, total: this.total });
        },

        get progressStyle() {
            return `--progress: ${this.total ? this.answeredCount / this.total : 0}`;
        },

        get nextLabel() {
            return this.isLastQuestion ? this.strings.finish : this.strings.next;
        },

        get errorTitle() {
            return { exhausted: this.strings.exhaustedTitle, unavailable: this.strings.unavailableTitle }[this.errorKind] ?? this.strings.errorTitle;
        },

        get errorText() {
            return this.errorKind === 'load' ? this.strings.errorText : '';
        },

        get canRetry() {
            return this.errorKind === 'load';
        },

        // ---------------------------------------------------------------- answering

        letter(index) {
            return String.fromCharCode(65 + index);
        },

        isLocked() {
            return this.busy || this.phase !== 'question';
        },

        optionState(option) {
            const answer = this.currentAnswer;

            if (answer === null) {
                return this.busy && option.id === this.selectedId ? 'selected' : 'idle';
            }

            if (!this.isInstant) {
                return option.id === answer.option_id ? 'selected' : 'idle';
            }

            if (option.id === answer.correct_option_id) {
                return answer.correct ? 'correct' : 'reveal';
            }

            return option.id === answer.option_id ? 'wrong' : 'idle';
        },

        isChosen(option) {
            return this.currentAnswer !== null && this.currentAnswer.option_id === option.id;
        },

        showBadgeRight(option) {
            return this.isInstant && this.currentAnswer !== null && option.id === this.currentAnswer.correct_option_id && this.currentAnswer.correct;
        },

        showBadgeAnswer(option) {
            return this.isInstant && this.currentAnswer !== null && option.id === this.currentAnswer.correct_option_id && !this.currentAnswer.correct;
        },

        showBadgeMine(option) {
            return this.isChosen(option) && (!this.isInstant || !this.currentAnswer.correct);
        },

        async choose(option) {
            if (this.isLocked()) {
                return;
            }

            const question = this.current;
            this.busy = true;
            this.answerFailed = false;
            this.selectedId = option.id;

            try {
                const result = await postJson(this.answerUrl, { question_id: question.id, option_id: option.id });

                // Replace the whole object rather than adding a key, so everything reading it updates.
                this.answers = {
                    ...this.answers,
                    [question.id]: this.isInstant
                        ? {
                              option_id: option.id,
                              correct: result.correct,
                              correct_option_id: result.correct_option_id,
                              explanation: result.explanation,
                          }
                        : { option_id: option.id },
                };

                this.streak = this.isInstant && result.correct ? this.streak + 1 : 0;

                if (result.finished) {
                    this.finished = true;
                    this.resultUrl = result.result_url ?? this.resultUrl;
                }

                this.phase = 'feedback';
                this.focusNext();
            } catch (error) {
                this.handleAnswerError(error);
            } finally {
                this.busy = false;
            }
        },

        handleAnswerError(error) {
            this.selectedId = null;

            if (error.status === 409 && error.body?.code === 'closed') {
                window.location.assign(error.body.result_url);
            } else if (error.status === 409 || error.status === 422) {
                // The server and this page disagree about the attempt: load it again.
                this.start();
            } else {
                // Offline or a server hiccup. Nothing was recorded, so the child can simply try again.
                this.answerFailed = true;
            }
        },

        // ---------------------------------------------------------------- feedback

        get feedbackKind() {
            if (!this.isInstant) {
                return 'recorded';
            }

            return this.currentAnswer?.correct ? 'ok' : 'hint';
        },

        get isOk() {
            return this.feedbackKind === 'ok';
        },

        get isHint() {
            return this.feedbackKind === 'hint';
        },

        get isRecorded() {
            return this.feedbackKind === 'recorded';
        },

        get feedbackTitle() {
            return { ok: this.strings.correct, hint: this.strings.hint, recorded: this.strings.recorded }[this.feedbackKind];
        },

        get rightAnswerText() {
            const answer = this.currentAnswer;

            if (!answer || !this.isInstant || answer.correct) {
                return '';
            }

            const option = this.current.options.find((candidate) => candidate.id === answer.correct_option_id);

            return option ? this.fill(this.strings.rightAnswer, { answer: option.body }) : '';
        },

        get explanationText() {
            return this.currentAnswer?.explanation ?? '';
        },

        get hasExplanation() {
            return this.explanationText !== '';
        },

        get hasRightAnswer() {
            return this.rightAnswerText !== '';
        },

        get announcement() {
            if (this.phase !== 'feedback') {
                return '';
            }

            return [this.feedbackTitle, this.rightAnswerText, this.explanationText].filter(Boolean).join(' ');
        },

        get streakText() {
            return this.fill(this.strings.streak, { count: this.streak });
        },

        get showStreak() {
            return this.settings.show_streak === true && this.isInstant && this.streak >= 2;
        },

        // ---------------------------------------------------------------- moving on

        next() {
            if (this.finished) {
                window.location.assign(this.resultUrl);
                return;
            }

            if (this.endsLevel()) {
                this.phase = 'checkpoint';
                this.focusCheckpoint();
                return;
            }

            this.advance();
        },

        advance() {
            this.index += 1;
            this.selectedId = null;
            this.answerFailed = false;
            this.phase = 'question';
            this.focusQuestion();
        },

        continueLevel() {
            this.advance();
        },

        // ---------------------------------------------------------------- progress strips

        dotClass(i) {
            if (this.questions[i] && this.questions[i].id in this.answers) {
                return 'is-done';
            }

            return i === this.index ? 'is-current' : '';
        },

        // Star slots (Kutip Bintang)
        slotClass(i) {
            const question = this.questions[i];
            const answer = question ? this.answers[question.id] : undefined;

            if (answer === undefined) {
                return i === this.index ? 'is-current' : '';
            }

            if (!this.isInstant) {
                return 'is-answered';
            }

            return answer.correct ? 'is-lit' : 'is-missed';
        },

        starClass(i) {
            const question = this.questions[i];
            const answer = question ? this.answers[question.id] : undefined;

            return this.isInstant && answer && answer.correct ? 'star star--on' : 'star';
        },

        get starsLit() {
            return Object.values(this.answers).filter((answer) => answer.correct === true).length;
        },

        get starsText() {
            return this.isInstant
                ? this.fill(this.strings.starsCollected, { count: this.starsLit })
                : this.fill(this.strings.starsAnswered, { count: this.answeredCount });
        },

        // River path (Misi Berlevel): questions are grouped into levels of `level_size`
        get levelSize() {
            return this.settings.level_size ?? 5;
        },

        get levelNumber() {
            return Math.floor(this.index / this.levelSize) + 1;
        },

        get levelStart() {
            return (this.levelNumber - 1) * this.levelSize;
        },

        get levelStones() {
            return Math.min(this.levelSize, this.total - this.levelStart);
        },

        get stones() {
            return Array.from({ length: this.levelStones }, (_, i) => i);
        },

        get answeredInLevel() {
            return this.stones.filter((i) => this.questions[this.levelStart + i].id in this.answers).length;
        },

        get correctInLevel() {
            return this.stones.filter((i) => this.answers[this.questions[this.levelStart + i].id]?.correct === true).length;
        },

        get pathStyle() {
            const step = this.isCheckpoint ? this.levelStones + 1 : this.answeredInLevel;

            return `--count: ${this.levelStones + 2}; --step: ${step}`;
        },

        get levelText() {
            return this.fill(this.strings.level, { level: this.levelNumber });
        },

        get levelPositionText() {
            // While a question is open the child is about to land on the next stone; during
            // feedback or a checkpoint she is standing on the one she just reached.
            const done = this.answeredInLevel;
            const current = this.phase === 'question' ? Math.min(done + 1, this.levelStones) : Math.max(done, 1);

            return this.fill(this.strings.stonePosition, { current, total: this.levelStones });
        },

        get checkpointTitle() {
            return this.fill(this.strings.checkpoint, { level: this.levelNumber });
        },

        get checkpointText() {
            return this.isInstant
                ? this.fill(this.strings.checkpointText, { count: this.correctInLevel, total: this.levelStones })
                : '';
        },

        stoneClass(i) {
            const question = this.questions[this.levelStart + i];
            const answer = question ? this.answers[question.id] : undefined;

            if (answer === undefined) {
                return !this.isCheckpoint && this.levelStart + i === this.index ? 'is-current' : '';
            }

            if (!this.isInstant) {
                return 'is-done';
            }

            return answer.correct ? 'is-right' : 'is-wrong';
        },

        stoneIsRight(i) {
            return this.stoneClass(i) === 'is-right';
        },

        stoneIsWrong(i) {
            return this.stoneClass(i) === 'is-wrong';
        },

        endsLevel() {
            // Only the quest concept pauses between levels, and never after the last question.
            return this.conceptKey === 'quest' && !this.isLastQuestion && (this.index + 1) % this.levelSize === 0;
        },

        // ---------------------------------------------------------------- helpers

        countStreak() {
            let streak = 0;

            for (const question of this.questions) {
                const answer = this.answers[question.id];

                if (answer === undefined) {
                    break;
                }

                streak = answer.correct === true ? streak + 1 : 0;
            }

            return streak;
        },

        fill(template, values) {
            return Object.entries(values).reduce((text, [key, value]) => text.replace(`:${key}`, value), template);
        },

        focusQuestion() {
            this.$nextTick(() => this.$refs.question?.focus({ preventScroll: false }));
        },

        focusNext() {
            this.$nextTick(() => this.$refs.next?.focus());
        },

        focusCheckpoint() {
            this.$nextTick(() => this.$refs.continue?.focus());
        },
    };
}
