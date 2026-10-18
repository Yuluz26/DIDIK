<x-layouts.public :title="__('public.about.title')" :description="__('public.about.meta_description')" body-class="page-about">
    <div class="reading">
        <header class="page-head">
            <h1 class="page-title">{{ __('public.about.title') }}</h1>
            <p class="lead">{{ __('public.about.lead') }}</p>
        </header>

        <div class="prose">
            <h2>{{ __('public.about.how_heading') }}</h2>
            <ol>
                @foreach (__('public.about.how') as $step)
                    <li>{{ $step }}</li>
                @endforeach
            </ol>

            <h2>{{ __('public.about.games_heading') }}</h2>
            <p>{{ __('public.about.games_text') }}</p>
            <ul>
                @foreach ($concepts as $concept)
                    <li><strong>{{ $concept->name() }}</strong>. {{ $concept->description() }}</li>
                @endforeach
            </ul>

            <h2>{{ __('public.about.quizizz_heading') }}</h2>
            <p>{{ __('public.about.quizizz_text') }}</p>
            <p><x-button :href="route('pages.privacy')">{{ __('public.footer.privacy') }} <x-icon name="arrow-right" /></x-button></p>
        </div>
    </div>
</x-layouts.public>
