@php
    $editing = $collection->exists;
    $chosen = old('links', $editing ? $collection->links->pluck('id')->all() : []);
    $config = [
        'all' => $allLinks->map(fn ($link) => ['id' => $link->id, 'title' => $link->title, 'status' => $link->status->label()])->values()->all(),
        'chosen' => array_map('intval', $chosen),
    ];
@endphp

<x-layouts.admin :title="$editing ? __('collections.edit_title') : __('collections.create_title')">
    <form class="panel form" method="post" novalidate
          action="{{ $editing ? route('admin.collections.update', $collection) : route('admin.collections.store') }}">
        @csrf
        @if ($editing) @method('PUT') @endif

        @include('admin.partials.errors')

        <x-field name="title" :label="__('collections.fields.title')" :value="$collection->title" maxlength="120" required />
        <x-field name="description" control="textarea" :label="__('collections.fields.description')" :value="$collection->description" maxlength="600" />

        <div class="form__grid form__grid--2">
            <x-field name="status" control="select" :label="__('collections.fields.status')" required>
                @foreach (\App\Enums\LinkStatus::cases() as $case)
                    @continue(in_array($case, [\App\Enums\LinkStatus::Broken], true))
                    <option value="{{ $case->value }}" @selected(old('status', $collection->status?->value) === $case->value)>{{ $case->label() }}</option>
                @endforeach
            </x-field>
            <x-field name="position" type="number" min="0" max="999" :label="__('collections.fields.position')" :help="__('collections.fields.position_help')" :value="$collection->position" />
        </div>

        <fieldset class="form__section" x-data="linkList(@js($config))">
            <legend class="field__label">{{ __('collections.fields.links') }}</legend>
            <p class="field__hint">{{ __('collections.fields.links_help') }}</p>

            <p class="panel__note" x-show="!hasItems" x-cloak>{{ __('collections.fields.none_yet') }}</p>

            <ol class="ordered">
                <template x-for="(link, index) in items" :key="link.id">
                    <li>
                        <input type="hidden" name="links[]" :value="link.id">
                        <span><strong x-text="link.title"></strong> <span class="status" x-text="link.status"></span></span>
                        <span class="table__actions">
                            <button type="button" class="btn btn--sm btn--icon" @click="move(index, -1)" :disabled="isFirst(index)" :aria-label="label('{{ __('collections.fields.up', ['title' => ':title']) }}', link)"><x-icon name="arrow-up" /></button>
                            <button type="button" class="btn btn--sm btn--icon" @click="move(index, 1)" :disabled="isLast(index)" :aria-label="label('{{ __('collections.fields.down', ['title' => ':title']) }}', link)"><x-icon name="arrow-down" /></button>
                            <button type="button" class="btn btn--sm btn--icon" @click="remove(index)" :aria-label="label('{{ __('collections.fields.remove', ['title' => ':title']) }}', link)"><x-icon name="x" /></button>
                        </span>
                    </li>
                </template>
            </ol>

            <div class="toolbar" x-show="hasAvailable" x-cloak>
                <div class="field toolbar__grow">
                    <label class="field__label" for="pick-link">{{ __('collections.fields.add_link') }}</label>
                    <select class="field__control" id="pick-link" x-model="picking">
                        <option value="">{{ __('collections.fields.pick') }}</option>
                        <template x-for="link in available" :key="link.id">
                            <option :value="link.id" x-text="link.title + ' (' + link.status + ')'"></option>
                        </template>
                    </select>
                </div>
                <button type="button" class="btn" @click="add()"><x-icon name="plus" /> {{ __('collections.fields.add_link') }}</button>
            </div>
            <p class="panel__note" x-show="!hasAvailable" x-cloak>{{ __('collections.fields.no_more') }}</p>
            <p class="panel__note">{{ __('collections.not_public') }}</p>
            @error('links')<p class="field__error"><x-icon name="circle-alert" /> {{ $message }}</p>@enderror
        </fieldset>

        <div class="form__actions">
            <x-button variant="primary" type="submit">{{ __('admin.common.save') }}</x-button>
            <x-button :href="route('admin.collections.index')">{{ __('admin.common.cancel') }}</x-button>
        </div>
    </form>
</x-layouts.admin>
