@props(['link'])

@php
    $category = $link->category;
    $meta = array_filter([$category?->name, $link->level?->name]);
    $thumb = $link->thumbnailUrl();
    $theme = $category?->displayTheme()->value ?? 'mint';
@endphp

<article {{ $attributes->class(['link-row', "theme-{$theme}"]) }}>
    @if ($thumb)
        <img class="link-row__thumb" src="{{ $thumb }}" alt="" width="60" height="60" loading="lazy">
    @else
        <span class="quiz-row__disc" aria-hidden="true"><x-icon :name="$category?->displayIcon() ?? 'link'" /></span>
    @endif

    <div class="link-row__body">
        <h3 class="link-row__title">{{ $link->title }}</h3>
        @if ($link->description)
            <p class="link-row__text">{{ $link->description }}</p>
        @endif
        @if ($meta)
            <p class="link-row__meta">{{ implode(' · ', $meta) }}</p>
        @endif
    </div>

    {{-- Always an obvious, honest exit: new tab, no referrer, and the label says it is another site. --}}
    <a
        class="btn"
        href="{{ $link->url }}"
        target="_blank"
        rel="noopener noreferrer"
        aria-label="{{ __('public.quizizz.open_label', ['title' => $link->title]) }}"
    >
        {{ __('public.quizizz.open') }}
        <x-icon name="external-link" />
    </a>
</article>
