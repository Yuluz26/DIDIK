@php
    $isTopic = $category->type === \App\Enums\CategoryType::Topic;
    $editing = $category->exists;
    $title = $isTopic
        ? ($editing ? __('categories.edit_topic_title') : __('categories.create_topic_title'))
        : ($editing ? __('categories.edit_subject_title') : __('categories.create_subject_title'));
@endphp

<x-layouts.admin :title="$title">
    <form class="panel form" method="post" novalidate
          action="{{ $editing ? route('admin.categories.update', $category) : route('admin.categories.store') }}">
        @csrf
        @if ($editing) @method('PUT') @endif

        @include('admin.partials.errors')

        <input type="hidden" name="type" value="{{ $category->type->value }}">

        <div class="form__grid form__grid--2">
            <x-field name="name" :label="__('categories.name')" :value="$category->name" maxlength="80" required />

            @if ($isTopic)
                <x-field name="parent_id" control="select" :label="__('categories.parent')" required>
                    <option value="">{{ __('admin.common.select') }}</option>
                    @foreach ($subjects as $subject)
                        <option value="{{ $subject->id }}" @selected((string) old('parent_id', $category->parent_id) === (string) $subject->id)>{{ $subject->name }}</option>
                    @endforeach
                </x-field>
            @endif
        </div>

        @if ($isTopic)
            <p class="panel__note">{{ __('categories.topic_follows') }}</p>
        @else
            <div class="form__grid form__grid--2">
                <x-field name="theme" control="select" :label="__('categories.theme')" required>
                    @foreach ($themes as $theme)
                        <option value="{{ $theme->value }}" @selected(old('theme', $category->theme?->value) === $theme->value)>{{ $theme->label() }}</option>
                    @endforeach
                </x-field>
                <x-field name="icon" control="select" :label="__('categories.icon')" required>
                    @foreach ($icons as $icon)
                        <option value="{{ $icon }}" @selected(old('icon', $category->icon) === $icon)>{{ __('categories.icons.'.$icon) }}</option>
                    @endforeach
                </x-field>
            </div>
        @endif

        <x-field name="position" type="number" min="0" max="999" :label="__('categories.position')" :help="__('categories.position_help')" :value="$category->position" />

        <div class="form__actions">
            <x-button variant="primary" type="submit">{{ __('admin.common.save') }}</x-button>
            <x-button :href="route('admin.categories.index')">{{ __('admin.common.cancel') }}</x-button>
        </div>
    </form>
</x-layouts.admin>
