<x-layouts.admin :title="__('collections.title')" :description="__('collections.lead')">
    <x-slot:actions>
        <x-button variant="primary" size="sm" :href="route('admin.collections.create')"><x-icon name="plus" /> {{ __('collections.create') }}</x-button>
    </x-slot:actions>

    <section class="panel">
        @if ($collections->isEmpty())
            <div class="empty">
                <x-mascot mood="sleep" size="md" />
                <h2 class="empty__title">{{ __('collections.empty_title') }}</h2>
                <p>{{ __('collections.empty_text') }}</p>
                <x-button variant="primary" :href="route('admin.collections.create')"><x-icon name="plus" /> {{ __('collections.create') }}</x-button>
            </div>
        @else
            <div class="table-wrap">
                <table class="table">
                    <caption class="visually-hidden">{{ __('collections.title') }}</caption>
                    <thead>
                        <tr>
                            <th scope="col">{{ __('collections.cols.title') }}</th>
                            <th scope="col" class="table__num">{{ __('collections.cols.links') }}</th>
                            <th scope="col">{{ __('collections.cols.status') }}</th>
                            <th scope="col"><span class="visually-hidden">{{ __('admin.common.actions') }}</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach ($collections as $collection)
                            <tr>
                                <td><span class="table__title"><a href="{{ route('admin.collections.edit', $collection) }}">{{ $collection->title }}</a></span></td>
                                <td class="table__num">{{ $collection->links_count }}</td>
                                <td><span class="status status--{{ $collection->status->value }}">{{ $collection->status->label() }}</span></td>
                                <td>
                                    <div class="table__actions">
                                        @if ($collection->status === \App\Enums\LinkStatus::Published)
                                            <x-button size="sm" :href="route('quizizz.show', $collection)" target="_blank" rel="noopener"><x-icon name="external-link" /> {{ __('admin.common.view') }}</x-button>
                                        @endif
                                        <x-button size="sm" :href="route('admin.collections.edit', $collection)"><x-icon name="pencil" /> {{ __('admin.common.edit') }}</x-button>
                                        @include('admin.partials.delete', ['action' => route('admin.collections.destroy', $collection), 'name' => $collection->title, 'text' => __('collections.keep_links')])
                                    </div>
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        @endif
    </section>
</x-layouts.admin>
