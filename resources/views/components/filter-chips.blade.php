{{--
    One row of filter chips. Each chip is a plain link that keeps every other filter in the URL,
    so filtering works without JavaScript and every result page can be shared or bookmarked.
--}}
@props(['label', 'param', 'options', 'current' => null, 'reset' => []])

@php
    $base = request()->except(['page', $param, ...$reset]);
    $url = fn (?string $value) => route('quizzes.index', $value === null ? $base : [...$base, $param => $value]);
@endphp

<div class="filter-group" role="group" aria-labelledby="filter-{{ $param }}">
    <h3 class="filter-group__label" id="filter-{{ $param }}">{{ $label }}</h3>
    <ul class="chip-list">
        <li>
            <a class="chip" href="{{ $url(null) }}" @if ($current === null) aria-current="true" @endif>
                @if ($current === null)<x-icon name="check" />@endif
                {{ __('public.browse.all') }}
            </a>
        </li>
        @foreach ($options as $value => $text)
            <li>
                <a class="chip" href="{{ $url((string) $value) }}" @if ($current === (string) $value) aria-current="true" @endif>
                    @if ($current === (string) $value)<x-icon name="check" />@endif
                    {{ $text }}
                </a>
            </li>
        @endforeach
    </ul>
</div>
