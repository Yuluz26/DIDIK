<x-layouts.public :title="$collection->title" :description="$collection->description ?: __('public.quizizz.lead')" body-class="page-quizizz">
    <div class="container">
        <header class="page-head">
            <div><x-button variant="quiet" :href="route('quizizz.index')"><x-icon name="arrow-left" /> {{ __('public.quizizz.all') }}</x-button></div>
            <h1 class="page-title">{{ $collection->title }}</h1>
            @if ($collection->description)
                <p class="lead">{{ $collection->description }}</p>
            @endif
            <p class="alert alert--info"><x-icon name="external-link" /> {{ __('public.home.quizizz.lead') }}</p>
        </header>

        @if ($collection->publishedLinks->isEmpty())
            <div class="empty">
                <x-mascot mood="sleep" size="lg" />
                <p>{{ __('public.quizizz.collection_empty') }}</p>
            </div>
        @else
            <div class="stack">
                @foreach ($collection->publishedLinks as $link)
                    <x-link-row :link="$link" heading="h2" />
                @endforeach
            </div>
        @endif
    </div>
</x-layouts.public>
