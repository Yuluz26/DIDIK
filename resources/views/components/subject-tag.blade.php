@props(['category'])

@if ($category)
    @php($subject = $category->subject())
    <span {{ $attributes->class(['tag', 'tag--'.$subject->theme->value]) }}>
        <x-icon :name="$subject->icon" />
        {{ $category->name }}
    </span>
@endif
