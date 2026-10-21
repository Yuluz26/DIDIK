<x-layouts.public :title="__('public.privacy.title')" :description="__('public.privacy.meta_description')" body-class="page-privacy">
    <div class="reading">
        <header class="page-head">
            <h1 class="page-title">{{ __('public.privacy.title') }}</h1>
            <p class="lead">{{ __('public.privacy.lead') }}</p>
        </header>

        <div class="prose">
            @foreach ($sections as $section)
                <h2>{{ $section['heading'] }}</h2>
                <ul>
                    @foreach ($section['items'] as $item)
                        <li>{{ $item }}</li>
                    @endforeach
                </ul>
            @endforeach

            @if ($email)
                <p>{{ __('public.privacy.contact', ['email' => $email]) }}</p>
            @endif

            <section lang="en" aria-labelledby="privacy-en">
                <h2 id="privacy-en">{{ __('public.privacy.english.heading') }}</h2>
                <ul>
                    @foreach ($english as $item)
                        <li>{{ $item }}</li>
                    @endforeach
                </ul>
            </section>
        </div>
    </div>
</x-layouts.public>
