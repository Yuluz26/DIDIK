<section class="section quizizz-teaser" aria-labelledby="quizizz-title">
    <div class="container">
        <div class="quizizz-teaser__head">
            <div>
                <h2 id="quizizz-title">{{ __('public.home.quizizz.heading') }}</h2>
                <p>{{ __('public.home.quizizz.lead') }}</p>
            </div>
            <a class="btn" href="{{ route('quizizz.index') }}">
                {{ __('public.home.quizizz.all') }}
                <x-icon name="arrow-right" />
            </a>
        </div>

        <div class="stack">
            @foreach ($links as $link)
                <x-link-row :link="$link" />
            @endforeach
        </div>
    </div>
</section>
