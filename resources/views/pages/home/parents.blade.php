<section class="section-flush parents river" aria-labelledby="parents-title">
    <div class="container parents__grid">
        <h2 id="parents-title">{{ __('public.home.parents.heading') }}</h2>

        <div class="parents__body">
            <ul class="stone-list">
                <li>{{ __('public.home.parents.one') }}</li>
                <li>{{ __('public.home.parents.two') }}</li>
                <li>{{ __('public.home.parents.three') }}</li>
            </ul>
            <a class="btn" href="{{ route('pages.privacy') }}">
                {{ __('public.home.parents.link') }}
                <x-icon name="arrow-right" />
            </a>
        </div>
    </div>
</section>
