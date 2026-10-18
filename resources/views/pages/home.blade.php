<x-layouts.public
    :title="__('public.home.title')"
    :description="__('public.home.meta_description')"
    body-class="page-home"
>
    {{-- 1. The claim, with the proof next to it: a real question to answer --}}
    <section class="hero" aria-labelledby="hero-title">
        <div class="container hero__grid">
            <div class="hero__copy">
                <h1 id="hero-title">{{ __('public.home.title') }}</h1>
                <p class="hero__lead">{{ __('public.home.lead') }}</p>
                <x-button variant="primary" :href="route('quizzes.index')">
                    {{ __('public.home.cta') }}
                    <x-icon name="arrow-right" />
                </x-button>
            </div>

            <div class="hero__live">
                @if ($live)
                    @include('pages.home.live', ['live' => $live])
                @else
                    <x-mascot mood="wave" size="xl" />
                @endif
            </div>
        </div>
    </section>

    {{-- 2. Find a quiz by year and subject --}}
    @include('pages.home.subjects')

    {{-- 3. Three ways to play --}}
    @include('pages.home.ways')

    {{-- 4. For parents, on the river --}}
    @include('pages.home.parents')

    {{-- 5. Quizizz --}}
    @if ($collection && $links->isNotEmpty())
        @include('pages.home.quizizz')
    @endif
</x-layouts.public>
