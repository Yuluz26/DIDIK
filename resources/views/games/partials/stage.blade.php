{{--
    The part of the player every concept shares: loading, errors, the question, the answers and the
    feedback after an answer. A concept view adds its own progress strip around this.
--}}
<section class="stage container" aria-label="{{ $quiz->title }}">
    {{-- Loading is the default state, so a slow connection shows something kind straight away. --}}
    <div class="stage__panel" x-show="isLoading" role="status">
        <x-mascot mood="think" size="lg" />
        <p class="stage__note">{{ __('public.player.loading') }}</p>
    </div>

    <div class="stage__panel" x-show="hasError" x-cloak role="alert">
        <x-mascot mood="hint" size="lg" />
        <h2 class="stage__title" x-text="errorTitle"></h2>
        <p x-show="canRetry" x-text="errorText"></p>
        <div class="stage__actions">
            <button type="button" class="btn btn--primary" x-show="canRetry" @click="retry()">
                <x-icon name="rotate-ccw" /> {{ __('public.player.retry') }}
            </button>
            <a class="btn" :href="quizUrl">{{ __('public.quiz.back') }}</a>
        </div>
    </div>

    <div class="stage__question" x-show="showQuestion" x-cloak :lang="lang">
        <h2 class="question" tabindex="-1" x-ref="question" x-text="current.body"></h2>

        <div class="answers" role="group" aria-label="{{ __('public.player.group') }}" :data-count="current.options.length">
            {{-- The loop variable is `n`, not `index`: inside this scope `index` would shadow the component's own. --}}
            <template x-for="(option, n) in current.options" :key="option.id">
                <button
                    type="button"
                    class="answer"
                    :data-state="optionState(option)"
                    :aria-disabled="isLocked()"
                    :aria-pressed="isChosen(option)"
                    @click="choose(option)"
                >
                    <span class="answer__letter" aria-hidden="true" x-text="letter(n)"></span>
                    <span x-text="option.body"></span>
                    <span class="answer__badge" x-show="showBadgeRight(option)">
                        <x-icon name="check" /> {{ __('public.player.badge_right') }}
                    </span>
                    <span class="answer__badge" x-show="showBadgeAnswer(option)">
                        <x-icon name="check" /> {{ __('public.player.badge_answer') }}
                    </span>
                    <span class="answer__badge" x-show="showBadgeMine(option)">{{ __('public.player.badge_mine') }}</span>
                </button>
            </template>
        </div>

        <p class="alert alert--warn" x-show="answerFailed" x-cloak role="alert">
            <x-icon name="wifi-off" /> {{ __('public.player.error_answer') }}
        </p>

        {{-- Always in the page, so assistive technology announces the result reliably. --}}
        <p class="visually-hidden" role="status" aria-live="polite" x-text="announcement"></p>

        <div class="feedback" x-show="showFeedback" x-cloak :data-kind="feedbackKind">
            <div class="feedback__mascot" aria-hidden="true">
                <x-mascot mood="cheer" size="md" x-show="isOk" />
                <x-mascot mood="hint" size="md" x-show="isHint" x-cloak />
                <x-mascot mood="happy" size="md" x-show="isRecorded" x-cloak />
            </div>

            <div class="feedback__body">
                <p class="feedback__title">
                    <x-icon name="circle-check" x-show="isOk || isRecorded" />
                    <x-icon name="lightbulb" x-show="isHint" x-cloak />
                    <span x-text="feedbackTitle"></span>
                </p>
                <p class="feedback__answer" x-show="hasRightAnswer" x-text="rightAnswerText"></p>
                <p class="feedback__explanation" x-show="hasExplanation" x-text="explanationText"></p>
            </div>

            <button type="button" class="btn btn--primary feedback__next" x-ref="next" @click="next()">
                <span x-text="nextLabel"></span>
                <x-icon name="arrow-right" />
            </button>
        </div>
    </div>

    {{-- A concept may add its own panels here (the quest's level checkpoint) in games/{key}/extras.blade.php. --}}
    @includeIf('games.'.$concept->key().'.extras')
</section>
