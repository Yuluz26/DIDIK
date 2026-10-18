<x-layouts.public :title="__('public.quizizz.title')" :description="__('public.quizizz.lead')" body-class="page-quizizz">
    <div class="container">
        <header class="page-head">
            <h1 class="page-title">{{ __('public.quizizz.title') }}</h1>
            <p class="lead">{{ __('public.quizizz.lead') }}</p>
        </header>

        @if ($collections->isEmpty())
            <div class="empty">
                <x-mascot mood="sleep" size="lg" />
                <h2 class="empty__title">{{ __('public.quizizz.empty_title') }}</h2>
                <p>{{ __('public.quizizz.empty_text') }}</p>
            </div>
        @else
            <div class="collections">
                @foreach ($collections as $collection)
                    <section class="collection" aria-labelledby="collection-{{ $collection->id }}">
                        <div class="collection__head">
                            <h2 id="collection-{{ $collection->id }}"><a href="{{ route('quizizz.show', $collection) }}">{{ $collection->title }}</a></h2>
                            @if ($collection->description)
                                <p>{{ $collection->description }}</p>
                            @endif
                        </div>
                        <div class="stack">
                            @foreach ($collection->publishedLinks as $link)
                                <x-link-row :link="$link" />
                            @endforeach
                        </div>
                    </section>
                @endforeach
            </div>
        @endif
    </div>
</x-layouts.public>
