<x-layouts.admin :title="__('categories.title')" :description="__('categories.lead')">
    <x-slot:actions>
        <x-button variant="primary" size="sm" :href="route('admin.categories.create')"><x-icon name="plus" /> {{ __('categories.new_subject') }}</x-button>
    </x-slot:actions>

    @forelse ($subjects as $subject)
        <section class="panel theme-{{ $subject->theme->value }}" aria-labelledby="subject-{{ $subject->id }}">
            <div class="panel__head">
                <h2 class="panel__title" id="subject-{{ $subject->id }}">
                    <span class="tag"><x-icon :name="$subject->icon" /> {{ $subject->name }}</span>
                    <small class="panel__note">{{ __('categories.quizzes', ['count' => $counts->get($subject->id, 0)]) }}</small>
                </h2>
                <div class="table__actions">
                    <x-button size="sm" :href="route('admin.categories.create', ['jenis' => 'topik', 'subjek' => $subject->id])"><x-icon name="plus" /> {{ __('categories.add_topic') }}</x-button>
                    <x-button size="sm" :href="route('admin.categories.edit', $subject)"><x-icon name="pencil" /> {{ __('admin.common.edit') }}</x-button>
                    @include('admin.partials.delete', ['action' => route('admin.categories.destroy', $subject), 'name' => $subject->name, 'text' => null])
                </div>
            </div>

            @if ($subject->children->isEmpty())
                <p class="panel__note">{{ __('categories.no_topics') }}</p>
            @else
                <div class="table-wrap">
                    <table class="table">
                        <caption class="visually-hidden">{{ $subject->name }}</caption>
                        <thead><tr><th scope="col">{{ __('categories.name') }}</th><th scope="col" class="table__num">{{ __('categories.quizzes', ['count' => '']) }}</th><th scope="col"><span class="visually-hidden">{{ __('admin.common.actions') }}</span></th></tr></thead>
                        <tbody>
                            @foreach ($subject->children as $topic)
                                <tr>
                                    <td><span class="table__title">{{ $topic->name }}</span></td>
                                    <td class="table__num">{{ $counts->get($topic->id, 0) }}</td>
                                    <td>
                                        <div class="table__actions">
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
