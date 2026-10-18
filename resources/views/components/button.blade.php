@props(['variant' => 'secondary', 'href' => null, 'size' => null, 'type' => 'button'])

@php($classes = 'btn btn--'.$variant.($size ? ' btn--'.$size : ''))

@if ($href)
    <a href="{{ $href }}" {{ $attributes->class($classes) }}>{{ $slot }}</a>
@else
    <button type="{{ $type }}" {{ $attributes->class($classes) }}>{{ $slot }}</button>
@endif
