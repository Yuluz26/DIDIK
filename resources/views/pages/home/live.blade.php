@php
    $payload = [
        'question' => [
            'id' => $live['question_id'],
            'url' => route('live.answer'),
            'options' => $live['options'],
        ],
        'strings' => [
            'help' => __('public.home.live.help'),
            'correct' => __('public.home.live.correct'),
            'hint' => __('public.home.live.hint'),
            'error' => __('public.home.live.error'),
        ],
    ];
@endphp

<div class="live" x-data="liveQuestion(@js($payload))">
    <div class="live__head">
        <h2 class="live__title">{{ __('public.home.live.heading') }}</h2>
        <p class="live__from">{{ __('public.home.live.from', ['title' => $live['quiz']->title]) }}</p>
    </div>

    <div class="live__panel">
        <p class="live__question" id="live-question" lang="{{ $live['quiz']->language }}">{{ $live['body'] }}</p>

        <div class="live__field">
            <div class="live__didi" x-ref="didi" :style="didiStyle" aria-hidden="true">
                {{-- Didi changes expression with the state; only the matching drawing is shown. --}}
                <x-mascot mood="think" size="sm" x-show="isThinking" />
                <x-mascot mood="cheer" size="sm" x-show="isCheering" x-cloak />
                <x-mascot mood="hint" size="sm" x-show="isHinting" x-cloak />
            </div>

            <ul class="live__stones" role="group" aria-labelledby="live-question" lang="{{ $live['quiz']->language }}">
                <template x-for="(option, n) in question.options" :key="option.id">
                    <li>
                        <button
                            type="button"
                            class="answer"
                            :data-state="stateOf(option)"
                            :aria-disabled="isLocked(option)"
                            @click="choose(option, $event)"
                        >
                            <span class="answer__letter" aria-hidden="true" x-text="letter(n)"></span>
                            <span x-text="option.body"></span>
                            <span class="answer__badge" x-show="isRight(option)">
                                <x-icon name="check" /> {{ __('public.player.badge_right') }}
                            </span>
                            <span class="answer__badge" x-show="isWrong(option)">
                                {{ __('public.player.badge_mine') }}
                            </span>
                        </button>
                    </li>
                </template>
            </ul>
        </div>
    </div>

    <div class="live__feedback" role="status" aria-live="polite">
        <p class="live__message" x-text="message">{{ __('public.home.live.help') }}</p>
        <p class="live__explanation" x-show="showExplanation" x-text="explanation" x-cloak></p>
        <a class="btn btn--primary" x-show="done" x-cloak href="{{ route('quizzes.show', $live['quiz']->slug) }}">
            {{ __('public.home.live.continue') }}
            <x-icon name="arrow-right" />
        </a>
    </div>

    <noscript>
        <p>{{ __('public.home.live.fallback') }}</p>
        <x-button variant="primary" :href="route('quizzes.show', $live['quiz']->slug)">{{ __('public.home.live.continue') }}</x-button>
    </noscript>
</div>
