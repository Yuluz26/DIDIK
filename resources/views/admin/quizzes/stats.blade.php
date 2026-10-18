<x-layouts.admin :title="__('admin.stats.title', ['title' => $quiz->title])">
    <x-slot:actions>
        <x-button size="sm" :href="route('admin.quizzes.edit', $quiz)"><x-icon name="arrow-left" /> {{ __('admin.common.back') }}</x-button>
    </x-slot:actions>

    @if ($stats['started'] === 0)
        <section class="panel">
            <div class="empty">
                <x-mascot mood="sleep" size="md" />
                <p>{{ __('admin.stats.no_attempts') }}</p>
            </div>
        </section>
    @else
        <section class="panel">
            <dl class="stats">
                <div><dt class="stats__label">{{ __('admin.stats.started') }}</dt><dd class="stats__value">{{ $stats['started'] }}</dd></div>
                <div><dt class="stats__label">{{ __('admin.stats.completed') }}</dt><dd class="stats__value">{{ $stats['completed'] }}</dd></div>
                <div><dt class="stats__label">{{ __('admin.stats.completion') }}</dt><dd class="stats__value">{{ $stats['completion_percent'] }}%</dd></div>
                <div><dt class="stats__label">{{ __('admin.stats.average') }}</dt><dd class="stats__value">{{ $stats['average_percent'] === null ? '—' : $stats['average_percent'].'%' }}</dd></div>
            </dl>
        </section>

        <section class="panel">
            <div class="table-wrap">
                <table class="table">
                    <caption class="visually-hidden">{{ __('admin.stats.title', ['title' => $quiz->title]) }}</caption>
                    <thead>
                        <tr>
                            <th scope="col">{{ __('admin.stats.question') }}</th>
                            <th scope="col" class="table__num">{{ __('admin.stats.answers') }}</th>
                            <th scope="col" class="table__num">{{ __('admin.stats.correct') }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach ($stats['questions'] as $row)
                            <tr>
                                <td><span class="table__title">{{ $row['number'] }}. {{ $row['body'] }}</span></td>
                                <td class="table__num">{{ $row['answers'] }}</td>
                                <td class="table__num">
                                    @if ($row['answers'] === 0)
                                        —
                                    @elseif (! $row['enough'])
                                        <span class="table__sub">{{ __('admin.stats.not_enough', ['count' => $minAnswers]) }}</span>
                                    @else
                                        {{ $row['percent'] }}%
                                    @endif
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
            <p class="panel__note">{{ __('admin.stats.note') }}</p>
        </section>
    @endif
</x-layouts.admin>
