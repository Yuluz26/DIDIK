<section class="section ways" aria-labelledby="ways-title">
    <div class="container">
        <div class="ways__intro">
            <h2 id="ways-title">{{ __('public.home.ways.heading') }}</h2>
            <p>{{ __('public.home.ways.lead') }}</p>
        </div>

        <ol class="ways__list">
            @foreach ($demos as $demo)
                @php($concept = $demo['concept'])
                <li class="way">
                    <div class="way__visual surface" aria-hidden="true">
                        <x-concept-demo :concept="$concept->key()" />
                    </div>

                    <div class="way__text">
                        <h3>{{ $concept->name() }}</h3>
                        <p>{{ $concept->description() }}</p>
                        @if ($demo['quiz'])
                            <a class="btn" href="{{ route('quizzes.play', $demo['quiz']->slug) }}">
                                {{ __('public.home.ways.try', ['title' => $demo['quiz']->title]) }}
                                <x-icon name="arrow-right" />
                            </a>
                        @endif
                    </div>
                </li>
            @endforeach
        </ol>
    </div>
</section>
