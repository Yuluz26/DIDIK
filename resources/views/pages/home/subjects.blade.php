<section class="section subjects" aria-labelledby="subjects-title">
    <div class="container subjects__grid">
        <div class="subjects__copy">
            <h2 id="subjects-title">{{ __('public.home.subjects.heading') }}</h2>
            <p class="subjects__lead">{{ __('public.home.subjects.lead') }}</p>

            <h3 class="subjects__levels-title" id="levels-title">{{ __('public.home.subjects.levels') }}</h3>
            <ul class="chip-list" aria-labelledby="levels-title">
                @foreach ($levels as $level)
                    <li>
                        <a class="chip" href="{{ route('quizzes.index', ['tahap' => $level->slug]) }}">{{ $level->name }}</a>
                    </li>
                @endforeach
            </ul>
        </div>

        <ul class="subjects__stones">
            @foreach ($subjects as $subject)
                <li>
                    <a
                        class="subject-stone theme-{{ $subject->theme->value }}"
                        href="{{ route('quizzes.index', ['subjek' => $subject->slug]) }}"
                    >
                        <x-icon :name="$subject->icon" />
                        <span class="subject-stone__name">{{ $subject->name }}</span>
                        <span class="subject-stone__count">
                            {{ $subject->quiz_total > 0 ? __('public.home.subjects.count', ['count' => $subject->quiz_total]) : __('public.home.subjects.none') }}
                        </span>
                    </a>
                </li>
            @endforeach
        </ul>
    </div>
</section>
