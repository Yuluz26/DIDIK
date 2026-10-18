<x-layouts.admin :title="__('links.title')" :description="__('links.lead')">
    <x-slot:actions>
        <x-button variant="primary" size="sm" :href="route('admin.links.create')"><x-icon name="plus" /> {{ __('links.create') }}</x-button>
    </x-slot:actions>

    <section class="panel">
        <form class="toolbar" method="get" action="{{ route('admin.links.index') }}" role="search">
            <div class="field toolbar__grow">
                <label class="field__label" for="q">{{ __('admin.common.search') }}</label>
                <input class="field__control" id="q" name="q" type="search" value="{{ $search }}" placeholder="{{ __('links.search') }}" maxlength="80">
            </div>
            <div class="field">
                <label class="field__label" for="status">{{ __('admin.common.status') }}</label>
                <select class="field__control" id="status" name="status">
                    <option value="">{{ __('quizzes.all_statuses') }}</option>
                    @foreach (\App\Enums\LinkStatus::cases() as $case)
                        <option value="{{ $case->value }}" @selected($status === $case)>{{ $case->label() }}</option>
                    @endforeach
                </select>
            </div>
            <x-button type="submit">{{ __('admin.common.filter') }}</x-button>
            @if ($search !== '' || $status)
                <x-button variant="quiet" :href="route('admin.links.index')">{{ __('admin.common.clear') }}</x-button>
            @endif
        </form>

        @if ($links->isEmpty())
            <div class="empty">
                <x-mascot mood="sleep" size="md" />
                @if ($search !== '' || $status)
                    <p>{{ __('admin.common.empty_filtered') }}</p>
                @else
                    <h2 class="empty__title">{{ __('links.empty_title') }}</h2>
                    <p>{{ __('links.empty_text') }}</p>
                    <x-button variant="primary" :href="route('admin.links.create')"><x-icon name="plus" /> {{ __('links.create') }}</x-button>
                @endif
            </div>
        @else
            <div class="table-wrap">
                <table class="table">
                    <caption class="visually-hidden">{{ __('links.title') }}</caption>
                    <thead>
                        <tr>
                            <th scope="col">{{ __('links.cols.title') }}</th>
                            <th scope="col">{{ __('links.cols.subject') }}</th>
                            <th scope="col">{{ __('links.cols.status') }}</th>
                            <th scope="col"><span class="visually-hidden">{{ __('admin.common.actions') }}</span></th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach ($links as $link)
                            <tr>
                                <td>
                                    <span class="table__title"><a href="{{ route('admin.links.edit', $link) }}">{{ $link->title }}</a></span>
                                    <span class="table__sub url-hint">{{ parse_url($link->url, PHP_URL_HOST) }}{{ parse_url($link->url, PHP_URL_PATH) }}</span>
                                </td>
                                <td>
                                    {{ $link->category?->name ?? '—' }}
                                    @if ($link->level)<span class="table__sub">{{ $link->level->name }}</span>@endif
                                </td>
                                <td><span class="status status--{{ $link->status->value }}">{{ $link->status->label() }}</span></td>
                                <td>
                                    <div class="table__actions">
                                        <x-button size="sm" :href="$link->url" target="_blank" rel="noopener noreferrer" :aria-label="__('links.open').': '.$link->title"><x-icon name="external-link" /> {{ __('admin.common.open') }}</x-button>
                                        <x-button size="sm" :href="route('admin.links.edit', $link)"><x-icon name="pencil" /> {{ __('admin.common.edit') }}</x-button>
                                        @include('admin.partials.delete', ['action' => route('admin.links.destroy', $link), 'name' => $link->title, 'text' => null])
                                    </div>
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>

            {{ $links->links() }}
        @endif
    </section>
</x-layouts.admin>
