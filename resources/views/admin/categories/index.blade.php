<x-layouts.admin :title="__('categories.title')" :description="__('categories.lead')">
    <x-slot:actions>
        <x-button variant="primary" size="sm" :href="route('admin.categories.create')"><x-icon name="plus" /> {{ __('categories.new_subject') }}</x-button>
    </x-slot:actions>

    @forelse ($subjects as $subject)
        <section class="panel theme-{{ $subject->theme->value }}" aria-labelledby="subject-{{ $subject->id }}">
            <div class="panel__head">
                <h2 class="panel__title" id="subject-{{ $subject->id }}">
                    <span class="tag"><x-icon :name="$subject->icon" /> {{ $subject->name }}</span>
                    <small class="panel__note">{{ __('categories.quizzes', ['count' => $totals->get($subject->id, 0)]) }}</small>
                </h2>
                <div class="actions">
                    <x-button size="sm" :href="route('admin.categories.create', ['jenis' => 'topik', 'subjek' => $subject->id])"><x-icon name="plus" /> {{ __('categories.add_topic') }}</x-button>
                    <x-button size="sm" :href="route('admin.categories.edit', $subject)"><x-icon name="pencil" /> {{ __('admin.common.edit') }}</x-button>
                    @include('admin.partials.delete', ['action' => route('admin.categories.destroy', $subject), 'name' => $subject->name, 'text' => null])
                </div>
            </div>

            @if ($subject->children->isEmpty())
                <p class="panel__note">{{ __('categories.no_topics') }}</p>
            @else
                <div class="table-wrap">
                    <table class="table table--stack" role="table">
                        <caption class="visually-hidden">{{ $subject->name }}</caption>
                        <thead role="rowgroup"><tr role="row"><th role="columnheader" scope="col">{{ __('categories.name') }}</th><th role="columnheader" scope="col" class="table__num">{{ __('categories.col_quizzes') }}</th><th role="columnheader" scope="col"><span class="visually-hidden">{{ __('admin.common.actions') }}</span></th></tr></thead>
                        <tbody role="rowgroup">
                            @foreach ($subject->children as $topic)
                                <tr role="row">
                                    <td role="cell"><span class="table__title">{{ $topic->name }}</span></td>
                                    <td role="cell" class="table__num" data-suffix="{{ mb_strtolower(__('categories.col_quizzes')) }}">{{ $counts->get($topic->id, 0) }}</td>
                                    <td role="cell">
                                        <div class="actions">
                                            <x-button size="sm" :href="route('admin.categories.edit', $topic)"><x-icon name="pencil" /> {{ __('admin.common.edit') }}</x-button>
                                            @include('admin.partials.delete', ['action' => route('admin.categories.destroy', $topic), 'name' => $topic->name, 'text' => null])
                                        </div>
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            @endif
        </section>
    @empty
        <section class="panel">
            <div class="empty">
                <x-mascot mood="sleep" size="lg" />
                <h2 class="empty__title">{{ __('categories.empty_title') }}</h2>
                <p>{{ __('categories.empty_text') }}</p>
            </div>
        </section>
    @endforelse
</x-layouts.admin>
