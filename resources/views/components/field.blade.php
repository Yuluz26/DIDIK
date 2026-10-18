{{--
    A labelled form control with help text and its error beside it. One component for inputs,
    textareas and selects (pass the <option>s as the slot). Error summary links point at the
    control's id, which is the field name with brackets turned into dashes.
--}}
@props([
    'name',
    'label',
    'help' => null,
    'control' => 'input',
    'type' => 'text',
    'value' => null,
    'required' => false,
])

@php
    $id = str_replace(['[', ']'], ['-', ''], $name);
    $key = str_replace(['[', ']'], ['.', ''], rtrim($name, ']'));
    $hasError = $errors->has($key);
    $describedBy = trim(($help ? "{$id}-help " : '').($hasError ? "{$id}-error" : ''));
@endphp

<div @class(['field', 'field--invalid' => $hasError])>
    <label class="field__label" for="{{ $id }}">
        {{ $label }}@if ($required)<span class="field__flag">{{ __('admin.common.required') }}</span>@endif
    </label>

    @if ($control === 'select')
        <select
            {{ $attributes->merge(['class' => 'field__control']) }}
            id="{{ $id }}"
            name="{{ $name }}"
            @if ($required) aria-required="true" @endif
            @if ($hasError) aria-invalid="true" @endif
            @if ($describedBy) aria-describedby="{{ $describedBy }}" @endif
        >{{ $slot }}</select>
    @elseif ($control === 'textarea')
        <textarea
            {{ $attributes->merge(['class' => 'field__control', 'rows' => 3]) }}
            id="{{ $id }}"
            name="{{ $name }}"
            @if ($required) aria-required="true" @endif
            @if ($hasError) aria-invalid="true" @endif
            @if ($describedBy) aria-describedby="{{ $describedBy }}" @endif
        >{{ old($key, $value) }}</textarea>
    @else
        <input
            {{ $attributes->merge(['class' => 'field__control']) }}
            id="{{ $id }}"
            name="{{ $name }}"
            type="{{ $type }}"
            value="{{ $type === 'password' ? '' : old($key, $value) }}"
            @if ($required) aria-required="true" @endif
            @if ($hasError) aria-invalid="true" @endif
            @if ($describedBy) aria-describedby="{{ $describedBy }}" @endif
        >
    @endif

    {{-- Help sits under the control, not between label and control, so controls in one row line up
         whatever the help text above or beside them needs. aria-describedby ties it to the control. --}}
    @if ($help)
        <p class="field__hint" id="{{ $id }}-help">{{ $help }}</p>
    @endif

    @if ($hasError)
        <p class="field__error" id="{{ $id }}-error"><x-icon name="circle-alert" /> <span>{{ $errors->first($key) }}</span></p>
    @endif
</div>
