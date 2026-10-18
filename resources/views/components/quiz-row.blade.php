@props(['quiz'])

@php
    $category = $quiz->category;
    $theme = $category?->displayTheme()->value ?? 'mint';
    $icon = $category?->displayIcon() ?? 'shapes';
    $meta = array_filter([
        $category?->name,
        $quiz->level?->name,
        $quiz->difficulty->label(),
        __('public.browse.questions', ['count' => $quiz->questions_count]),
    ]);
@endphp

<article {{ $attributes->class(['quiz-row', "theme-{$theme}"]) }}>
    <span class="quiz-row__disc" aria-hidden="true"><x-icon :name="$icon" /></span>

    <div class="quiz-row__text">
        <h3 class="quiz-row__title"><a href="{{ route('quizzes.show', $quiz->slug) }}">{{ $quiz->title }}</a></h3>
        <p class="quiz-row__meta">{{ implode(' · ', $meta) }}</p>
    </div>

    <a
        class="btn btn--primary btn--icon quiz-row__play"
        href="{{ route('quizzes.play', $quiz->slug) }}"
        aria-label="{{ __('public.browse.play', ['title' => $quiz->title]) }}"
    >
        <x-icon name="play" />
    </a>
</article>
