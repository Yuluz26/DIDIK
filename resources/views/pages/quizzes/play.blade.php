@php
    $theme = $quiz->category?->displayTheme()->value ?? 'mint';

    $config = [
        'concept' => $concept->key(),
        'settings' => $settings,
        'lang' => $quiz->language,
        'quizUrl' => route('quizzes.show', $quiz->slug),
        'startUrl' => route('attempts.start', $quiz->slug),
        'strings' => [
            'questionOf' => __('public.player.question_of', ['current' => ':current', 'total' => ':total']),
            'next' => __('public.player.next'),
            'finish' => __('public.player.finish'),
            'correct' => __('public.player.correct'),
            'hint' => __('public.player.hint'),
            'recorded' => __('public.player.recorded'),
            'rightAnswer' => __('public.player.right_answer', ['answer' => ':answer']),
            'errorTitle' => __('public.player.error_title'),
            'errorText' => __('public.player.error_text'),
            'exhaustedTitle' => __('public.player.exhausted_title'),
            'unavailableTitle' => __('public.player.unavailable_title'),
            'streak' => __('public.player.stars.streak', ['count' => ':count']),
            'starsCollected' => __('public.player.stars.collected', ['count' => ':count']),
            'starsAnswered' => __('public.player.stars.answered', ['count' => ':count']),
            'level' => __('public.player.quest.level', ['level' => ':level']),
            'stonePosition' => __('public.player.quest.position', ['current' => ':current', 'total' => ':total']),
            'checkpoint' => __('public.player.quest.checkpoint', ['level' => ':level']),
            'checkpointText' => __('public.player.quest.checkpoint_text', ['count' => ':count', 'total' => ':total']),
        ],
    ];
@endphp

<x-layouts.public :title="$quiz->title" :noindex="true" :minimal="true" :body-class="'page-play concept-'.$concept->key()">
    <div class="player theme-{{ $theme }}" x-data="quizPlayer(@js($config))" x-init="start()">
        <noscript>
            <div class="container"><p class="alert alert--warn">{{ __('public.player.no_script') }}</p></div>
        </noscript>

        @include($concept->view(), ['quiz' => $quiz, 'settings' => $settings])

        <dialog class="dialog" id="quit" aria-labelledby="quit-title">
            <h2 id="quit-title" class="dialog__title">{{ __('public.player.quit_title') }}</h2>
            <p>{{ __('public.player.quit_text') }}</p>
            <div class="dialog__actions">
                <button type="button" class="btn btn--primary" data-dialog-close>{{ __('public.player.quit_stay') }}</button>
                <a class="btn" href="{{ route('quizzes.show', $quiz->slug) }}">{{ __('public.player.quit_confirm') }}</a>
            </div>
        </dialog>
    </div>
</x-layouts.public>
