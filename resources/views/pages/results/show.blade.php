@php
    $mood = [3 => 'cheer', 2 => 'happy', 1 => 'hint'][$attempt->stars] ?? 'happy';
    $message = [3 => __('public.result.three'), 2 => __('public.result.two'), 1 => __('public.result.one')][$attempt->stars];
@endphp

<x-layouts.public :title="__('public.result.title').': '.$quiz->title" :noindex="true" body-class="page-result">
    <div class="container result-layout">
        <section class="result" aria-labelledby="result-title">
            <x-mascot :mood="$mood" size="lg" />

            <ol class="result__stars" aria-label="{{ __('public.result.stars', ['count' => $attempt->stars]) }}">
                @foreach ([1, 2, 3] as $i)
                    <li style="--i: {{ $i }}"><x-star :on="$i <= $attempt->stars" /></li>
                @endforeach
            </ol>

            <h1 class="result__headline" id="result-title">{{ $message }}</h1>

            <p class="result__facts">
                <span>{{ __('public.result.score', ['correct' => $attempt->correct_count, 'total' => $attempt->question_count]) }}</span>
                <span>{{ __('public.result.points', ['score' => $attempt->score, 'max' => $attempt->max_score]) }}</span>
                <span>{{ __('public.result.stars', ['count' => $attempt->stars]) }}</span>
            </p>

            <div class="result__actions">
                @if ($canReplay)
                    <x-button variant="primary" :href="route('quizzes.play', $quiz->slug)"><x-icon name="rotate-ccw" /> {{ __('public.result.replay') }}</x-button>
                @endif
                <x-button :href="route('quizzes.index')">{{ __('public.result.others') }}</x-button>
            </div>

            @if ($remaining !== null)
                <p class="intro__note">{{ $remaining > 0 ? __('public.result.attempts_left', ['count' => $remaining]) : __('public.result.attempts_none') }}</p>
            @endif
        </section>

        <section class="review" aria-labelledby="review-title" lang="{{ $quiz->language }}">
            <div lang="{{ app()->getLocale() }}">
                <h2 id="review-title" class="subhead">{{ __('public.result.review') }}</h2>
                <p>{{ __('public.result.review_intro') }}</p>
            </div>

            <ol class="review__list">
                @foreach ($review as $item)
                    <li>
                        <details class="review__item">
                            <summary>
                                <span class="review__number" aria-hidden="true">{{ $item['number'] }}</span>
                                <span>{{ $item['body'] }}</span>
                                <span class="review__verdict" data-correct="{{ $item['correct'] ? 'true' : 'false' }}">
                                    <x-icon :name="$item['correct'] ? 'check' : 'lightbulb'" />
                                    <span lang="{{ app()->getLocale() }}">{{ $item['correct'] ? __('public.result.question_correct') : __('public.result.question_wrong') }}</span>
                                </span>
                            </summary>

                            <div class="review__body">
                                <ul class="review__options">
                                    @foreach ($item['options'] as $option)
                                        <li class="review__option" data-right="{{ $option['correct'] ? 'true' : 'false' }}" data-mine="{{ $option['chosen'] ? 'true' : 'false' }}">
                                            <span>{{ $option['body'] }}</span>
                                            @if ($option['correct'])
                                                <span class="answer__badge" lang="{{ app()->getLocale() }}"><x-icon name="check" /> {{ __('public.result.right') }}</span>
                                            @endif
                                            @if ($option['chosen'])
                                                <span class="answer__badge" lang="{{ app()->getLocale() }}">{{ __('public.result.yours') }}</span>
                                            @endif
                                        </li>
                                    @endforeach
                                </ul>
                                @if ($item['explanation'])
                                    <p class="review__why">{{ $item['explanation'] }}</p>
                                @endif
                            </div>
                        </details>
                    </li>
                @endforeach
            </ol>
        </section>
    </div>
</x-layouts.public>
