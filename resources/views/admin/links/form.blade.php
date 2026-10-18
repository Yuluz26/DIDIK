@php($editing = $link->exists)

<x-layouts.admin :title="$editing ? __('links.edit_title') : __('links.create_title')">
    <form class="panel form" method="post" novalidate enctype="multipart/form-data"
          action="{{ $editing ? route('admin.links.update', $link) : route('admin.links.store') }}">
        @csrf
        @if ($editing) @method('PUT') @endif

        @include('admin.partials.errors')

        <x-field name="title" :label="__('links.fields.title')" :value="$link->title" maxlength="160" required />
        <x-field name="url" type="url" :label="__('links.fields.url')" :help="__('links.fields.url_help')" :value="$link->url" maxlength="500" placeholder="https://quizizz.com/…" autocomplete="off" required />
        <x-field name="description" control="textarea" :label="__('links.fields.description')" :value="$link->description" maxlength="600" />

        <div class="form__grid form__grid--2">
            <x-field name="category_id" control="select" :label="__('links.fields.category')">
                <option value="">{{ __('quizzes.fields.select') }}</option>
                @foreach ($subjects as $subject)
                    <optgroup label="{{ $subject->name }}">
                        <option value="{{ $subject->id }}" @selected((string) old('category_id', $link->category_id) === (string) $subject->id)>{{ $subject->name }}</option>
                        @foreach ($subject->children as $topic)
                            <option value="{{ $topic->id }}" @selected((string) old('category_id', $link->category_id) === (string) $topic->id)>{{ $subject->name }} › {{ $topic->name }}</option>
                        @endforeach
                    </optgroup>
                @endforeach
            </x-field>

            <x-field name="school_level_id" control="select" :label="__('links.fields.level')">
                <option value="">{{ __('quizzes.fields.select') }}</option>
                @foreach ($levels as $level)
                    <option value="{{ $level->id }}" @selected((string) old('school_level_id', $link->school_level_id) === (string) $level->id)>{{ $level->name }}</option>
                @endforeach
            </x-field>
        </div>

        <x-field name="tags" :label="__('links.fields.tags')" :help="__('links.fields.tags_help')" :value="$editing ? $link->tagList() : ''" maxlength="300" />

        <x-field name="status" control="select" :label="__('links.fields.status')" :help="__('links.fields.status_help')" required>
            @foreach (\App\Enums\LinkStatus::cases() as $case)
                <option value="{{ $case->value }}" @selected(old('status', $link->status?->value) === $case->value)>{{ $case->label() }}</option>
            @endforeach
        </x-field>

        <div class="form__section">
            @if ($link->thumbnailUrl())
                <p class="field__label">{{ __('links.fields.thumbnail_current') }}</p>
                <img class="thumb-preview" src="{{ $link->thumbnailUrl() }}" alt="" width="64" height="64">
                <x-check name="remove_thumbnail" :label="__('links.fields.thumbnail_remove')" :checked="false" />
            @endif
            <x-field name="thumbnail" type="file" accept="image/jpeg,image/png,image/webp" :label="__('links.fields.thumbnail')" :help="__('links.fields.thumbnail_help')" />
        </div>

        <div class="form__actions">
            <x-button variant="primary" type="submit">{{ __('admin.common.save') }}</x-button>
            <x-button :href="route('admin.links.index')">{{ __('admin.common.cancel') }}</x-button>
        </div>
    </form>
</x-layouts.admin>
