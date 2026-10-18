@php
    $hasFilters = $subject || $topic || $level || $difficulty || $search !== '';
@endphp

<x-layouts.public :title="__('public.browse.title')" :description="__('public.browse.lead')" body-class="page-browse">
    <div class="container">
        <header class="page-head">
            <h1 class="page-title">{{ __('public.browse.title') }}</h1>
            <p class="lead">{{ __('public.browse.lead') }}</p>
        </header>

        <div class="browse">
            <details class="filters" data-open-on-desktop @if ($hasFilters) open @endif>
                <summary><x-icon name="search" /> {{ __('public.browse.filters') }}</summary>

                <div class="filters__body">
                    <form class="search" method="get" action="{{ route('quizzes.index') }}" role="search">
                        <div class="field">
                            <label class="field__label" for="q">{{ __('public.browse.search') }}</label>
                            <input
                                class="field__control"
                                id="q"
                                name="q"
                                type="search"
                                value="{{ $search }}"
                                maxlength="80"
                                autocomplete="off"
                                placeholder="{{ __('public.browse.search_placeholder') }}"
                            >
                        </div>
                        @foreach (['subjek', 'topik', 'tahap', 'kesukaran'] as $key)
                            @if (request()->filled($key))
                                <input type="hidden" name="{{ $key }}" value="{{ request($key) }}">
                            @endif
                        @endforeach
                        <button class="btn btn--primary" type="submit">{{ __('public.browse.search_button') }}</button>
                    </form>

                    <x-filter-chips
                        :label="__('public.browse.subject')"
                        param="subjek"
                        :options="$subjects->pluck('name', 'slug')->all()"
                        :current="$subject?->slug"
                        :reset="['topik']"
                    />

                    @if ($subject && $subject->children->isNotEmpty())
                        <x-filter-chips
                            :label="__('enums.category_type.topic')"
                            param="topik"
                            :options="$subject->children->pluck('name', 'slug')->all()"
                            :current="$topic?->slug"
                        />
                    @endif

                    <x-filter-chips
                        :label="__('public.browse.level')"
                        param="tahap"
                        :options="$levels->pluck('name', 'slug')->all()"
                        :current="$level?->slug"
                    />

                    <x-filter-chips
                        :label="__('public.browse.difficulty')"
                        param="kesukaran"
                        :options="\App\Enums\Difficulty::options()"
                        :current="$difficulty?->value"
                    />

                    @if ($hasFilters)
                        <div><a class="btn btn--quiet" href="{{ route('quizzes.index') }}"><x-icon name="x" /> {{ __('public.browse.clear') }}</a></div>
                    @endif
                </div>
            </details>

            <section class="results" aria-labelledby="results-title">
                <div class="results__head">
                    <h2 class="results__count" id="results-title">
                        {{ $quizzes->total() > 0 ? __('public.browse.results', ['count' => $quizzes->total()]) : __('public.browse.results_none') }}
                    </h2>
                </div>

                @if ($quizzes->isEmpty())
                    <div class="empty">
                        <x-mascot mood="sleep" size="lg" />
                        @if ($hasFilters)
                            <h3 class="empty__title">{{ __('public.browse.empty_title') }}</h3>
                            <p>{{ __('public.browse.empty_text') }}</p>
                            <x-button variant="primary" :href="route('quizzes.index')">{{ __('public.browse.clear') }}</x-button>
                        @else
                            <h3 class="empty__title">{{ __('public.browse.nothing_title') }}</h3>
                            <p>{{ __('public.browse.nothing_text') }}</p>
                        @endif
                    </div>
                @else
                    <ul class="results__list">
                        @foreach ($quizzes as $quiz)
                            <li><x-quiz-row :quiz="$quiz" /></li>
                        @endforeach
                    </ul>

                    {{ $quizzes->links() }}
                @endif
            </section>
        </div>
    </div>
</x-layouts.public>
