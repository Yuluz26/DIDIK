@php
    $theme = $quiz->category?->displayTheme()->value ?? 'mint';
    $exhausted = $remaining === 0 && ! $resumable;
@endphp

<x-layouts.public
    :title="$quiz->title"
    :description="$quiz->summary ?: __('public.home.meta_description')"
    :body-class="'page-intro theme-'.$theme"
>
    <div class="container">
        <div class="page-head">
            <div><x-button variant="quiet" :href="route('quizzes.index')"><x-icon name="arrow-left" /> {{ __('public.quiz.back') }}</x-button></div>
        </div>

        <div class="intro">
            <div class="intro__main">
                <x-subject-tag :category="$quiz->category" />
                <h1 class="page-title">{{ $quiz->title }}</h1>
                @if ($quiz->summary)
                    <p class="lead">{{ $quiz->summary }}</p>
                @endif

                <dl class="facts">
                    @if ($quiz->level)
                        <dt>{{ __('public.quiz.level') }}</dt>
                        <dd>{{ $quiz->level->name }} ({{ $quiz->level->ageLabel() }})</dd>
                    @endif
                    <dt>{{ __('public.quiz.difficulty') }}</dt>
                    <dd>{{ $quiz->difficulty->label() }}</dd>
                    <dt>{{ __('public.quiz.questions') }}</dt>
                    <dd>{{ $quiz->questions_count }}</dd>
                    <dt>{{ __('public.quiz.feedback') }}</dt>
                    <dd>{{ $quiz->feedback_mode->label() }}</dd>
                    <dt>{{ __('public.quiz.attempts') }}</dt>
                    <dd>{{ $quiz->attempts_allowed === null ? __('public.quiz.attempts_unlimited') : __('public.quiz.attempts_count', ['count' => $quiz->attempts_allowed]) }}</dd>
                </dl>

                <div class="intro__start">
                    @if ($exhausted)
                        <p class="alert alert--info"><x-icon name="info" /> {{ __('public.quiz.exhausted') }}</p>
                        @if ($lastResult)
                            <x-button variant="primary" :href="route('results.show', $lastResult)">{{ __('public.quiz.last_result') }} <x-icon name="arrow-right" /></x-button>
                        @endif
                    @else
                        <x-button variant="primary" :href="route('quizzes.play', $quiz->slug)">
                            {{ $resumable ? __('public.quiz.resume') : __('public.quiz.start') }}
                            <x-icon name="play" />
                        </x-button>
                        @if ($remaining !== null)
                            <p class="intro__note">{{ __('public.quiz.attempts_left', ['count' => $remaining]) }}</p>
                        @endif
                    @endif
                </div>

                <section class="intro__rules" aria-labelledby="rules-title">
                    <h2 id="rules-title" class="subhead">{{ __('public.quiz.rules_heading') }}</h2>
                    <ul class="stone-list">
                        <li>{{ __('public.quiz.rule_one') }}</li>
                        <li>{{ __('public.quiz.rule_two') }}</li>
                        <li>{{ __('public.quiz.rule_three') }}</li>
                    </ul>
                </section>
            </div>

            <aside class="intro__visual" aria-labelledby="concept-title">
                <h2 id="concept-title">{{ __('public.quiz.how') }}: {{ $concept->name() }}</h2>
                <div class="way__visual surface" aria-hidden="true">
                    <x-concept-demo :concept="$concept->key()" />
                </div>
                <p>{{ $concept->description() }}</p>
            </aside>
        </div>
    </div>
</x-layouts.public>
