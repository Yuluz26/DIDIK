<x-layouts.admin :title="__('admin.dashboard.title')">
    @unless ($hasQuizzes)
        <section class="panel">
            <div class="empty">
                <x-mascot mood="wave" size="lg" />
                <h2 class="empty__title">{{ __('admin.dashboard.first_title') }}</h2>
                <p>{{ __('admin.dashboard.first_text') }}</p>
                <x-button variant="primary" :href="route('admin.quizzes.create')"><x-icon name="plus" /> {{ __('admin.dashboard.first_cta') }}</x-button>
            </div>
        </section>
    @endunless

    <section class="panel" aria-label="{{ __('admin.dashboard.title') }}">
        <dl class="stats">
            <div><dt class="stats__label">{{ __('admin.dashboard.published') }}</dt><dd class="stats__value">{{ $overview['published'] }}</dd></div>
            <div><dt class="stats__label">{{ __('admin.dashboard.drafts') }}</dt><dd class="stats__value">{{ $overview['drafts'] }}</dd></div>
            <div><dt class="stats__label">{{ __('admin.dashboard.started') }}</dt><dd class="stats__value">{{ $overview['started_week'] }}</dd></div>
            <div><dt class="stats__label">{{ __('admin.dashboard.completed') }}</dt><dd class="stats__value">{{ $overview['completed_week'] }}</dd></div>
            <div>
                <dt class="stats__label">{{ __('admin.dashboard.average') }}</dt>
                <dd class="stats__value">{{ $overview['average_percent'] === null ? '—' : $overview['average_percent'].'%' }}</dd>
            </div>
        </dl>
    </section>

    <div class="grid-2">
        <section class="panel" aria-labelledby="attention-title">
            <h2 class="panel__title" id="attention-title">{{ __('admin.dashboard.attention') }}</h2>
            @if ($attention['broken']->isEmpty())
                <p class="panel__note">{{ __('admin.dashboard.attention_none') }}</p>
            @else
                <ul class="plain-list">
                    @foreach ($attention['broken'] as $item)
                        <li>
                            <a href="{{ route('admin.quizzes.questions.edit', $item['quiz']) }}">{{ $item['quiz']->title }}</a>
                            <small>{{ implode(' ', $item['problems']) }}</small>
                        </li>
                    @endforeach
                </ul>
            @endif
        </section>

        <section class="panel" aria-labelledby="ready-title">
            <h2 class="panel__title" id="ready-title">{{ __('admin.dashboard.ready') }}</h2>
            @if ($attention['ready']->isEmpty())
                <p class="panel__note">{{ __('admin.dashboard.ready_none') }}</p>
            @else
                <ul class="plain-list">
                    @foreach ($attention['ready'] as $quiz)
                        <li>
                            <a href="{{ route('admin.quizzes.edit', $quiz) }}">{{ $quiz->title }}</a>
                            <small>{{ __('quizzes.ready') }}</small>
                        </li>
                    @endforeach
                </ul>
            @endif
        </section>
    </div>

    <section class="panel" aria-labelledby="hardest-title">
        <h2 class="panel__title" id="hardest-title">{{ __('admin.dashboard.hardest') }}</h2>
        @if ($hardest->isEmpty())
            <p class="panel__note">{{ __('admin.dashboard.hardest_none', ['count' => $minAnswers]) }}</p>
        @else
            <ul class="plain-list">
                @foreach ($hardest as $row)
                    <li>
                        <a href="{{ route('admin.quizzes.stats', $row->quiz_id) }}">{{ $row->body }}</a>
                        <small>{{ $row->title }} · {{ __('admin.dashboard.correct_of', ['percent' => $row->percent, 'answers' => $row->answers]) }}</small>
                    </li>
                @endforeach
            </ul>
        @endif
    </section>
</x-layouts.admin>
