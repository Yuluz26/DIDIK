import { postJson } from './lib/http';

/**
 * The homepage's "try one question". Answers are checked on the server; Didi hops down the
 * gutter to the stone that was right, or wobbles and lets the child try another.
 */
export default function liveQuestion(config) {
    return {
        question: config.question,
        strings: config.strings,
        state: 'idle', // idle | busy | correct | hint | error
        outcomes: {}, // option id -> 'wrong' | 'right'
        didiY: 0,
        explanation: '',

        get isThinking() {
            return this.state === 'idle' || this.state === 'busy';
        },

        get isCheering() {
            return this.state === 'correct';
        },

        get isHinting() {
            return this.state === 'hint' || this.state === 'error';
        },

        get showExplanation() {
            return this.done && this.explanation !== '';
        },

        get done() {
            return this.state === 'correct';
        },

        get message() {
            return { correct: this.strings.correct, hint: this.strings.hint, error: this.strings.error }[this.state] ?? this.strings.help;
        },

        get didiStyle() {
            return `transform: translateY(${this.didiY}px)`;
        },

        letter(index) {
            return String.fromCharCode(65 + index);
        },

        outcome(option) {
            return this.outcomes[option.id] ?? 'none';
        },

        isRight(option) {
            return this.outcome(option) === 'right';
        },

        isWrong(option) {
            return this.outcome(option) === 'wrong';
        },

        stateOf(option) {
            return { none: 'idle', wrong: 'wrong', right: 'correct' }[this.outcome(option)];
        },

        isLocked(option) {
            return this.done || this.state === 'busy' || this.outcome(option) !== 'none';
        },

        async choose(option, event) {
            if (this.isLocked(option)) {
                return;
            }

            const row = event.currentTarget.closest('li');
            this.state = 'busy';

            try {
                const result = await postJson(this.question.url, {
                    question_id: this.question.id,
                    option_id: option.id,
                });

                this.explanation = result.explanation ?? '';

                if (result.correct) {
                    this.outcomes[option.id] = 'right';
                    this.state = 'correct';
                    this.didiY = row.offsetTop + row.offsetHeight / 2 - this.$refs.didi.offsetHeight / 2;
                } else {
                    this.outcomes[option.id] = 'wrong';
                    this.state = 'hint';
                }
            } catch {
                this.state = 'error';
            }
        },
    };
}
