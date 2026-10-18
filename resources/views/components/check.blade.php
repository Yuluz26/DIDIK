{{-- A checkbox that always submits 0 or 1: the hidden input covers the unchecked case. --}}
@props(['name', 'label', 'help' => null, 'checked' => false])

@php($id = str_replace(['[', ']'], ['-', ''], $name))

<label class="check" for="{{ $id }}">
    <input type="hidden" name="{{ $name }}" value="0">
    <input type="checkbox" id="{{ $id }}" name="{{ $name }}" value="1" @checked(old(str_replace(['[', ']'], ['.', ''], rtrim($name, ']')), $checked))>
    <span>
        {{ $label }}
        @if ($help)<small>{{ $help }}</small>@endif
    </span>
</label>
