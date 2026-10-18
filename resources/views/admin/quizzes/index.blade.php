<x-layouts.admin :title="__('quizzes.title')">
    <x-slot:actions>
        <x-button variant="primary" size="sm" :href="route('admin.quizzes.create')"><x-icon name="plus" /> {{ __('quizzes.create') }}</x-button>
    </x-slot:actions>

    <section class="panel">
        <form class="toolbar" method="get" action="{{ route('admin.quizzes.index') }}" role="search">
            <div class="field toolbar__grow">
                <label class="field__label" for="q">{{ __('admin.common.search') }}</label>
                <input class="field__control" id="q" name="q" type="search" value="{{ $search }}" placeholder="{{ __('quizzes.search') }}" maxlength="80">
            </div>
            <div class="field">
                <label class="field__label" for="status">{{ __('admin.common.status') }}</label>
                <select class="field__control" id="status" name="status">
                    <option value="">{{ __('quizzes.all_statuses') }}</option>
                    @foreach (\App\Enums\QuizStatus::cases() as $case)
                        <option value="{{ $case->value }}" @selected($status === $case)>{{ $case->label() }}</option>
                    @endforeach
                </select>
            </div>
            <x-button type="submit">{{ __('admin.common.filter') }}</x-button>
            @if ($search !== '' || $status)
                <x-button variant="quiet" :href="route('admin.quizzes.index')">{{ __('admin.common.clear') }}</x-button>
            @endif
        </form>

        @if ($quizzes->isEmpty())
            <div class="empty">
                <x-mascot mood="sleep" size="md" />
                @if ($search !== '' || $status)
                    <p>{{ __('admin.common.empty_filtered') }}</p>
                @else
                    <h2 class="empty__title">{{ __('quizzes.empty_title') }}</h2>
                    <p>{{ __('quizzes.empty_text') }}</p>
                    <x-button variant="primary" :href="route('admin.quizzes.create')"><x-icon name="plus" /> {{ __('quizzes.create') }}</x-button>
                @endif
            </div>
        @else
            <div class="table-wrap">
                <table class="table table--stack" role="table">
                    <caption class="visually-hidden">{{ __('quizzes.title') }}</caption>
                    <thead role="rowgroup">
                        <tr role="row">
                            <th role="columnheader" scope="col">{{ __('quizzes.cols.title') }}</th>
                            <th role="columnheader" scope="col">{{ __('quizzes.cols.level') }}</th>
                            <th role="columnheader" scope="col">{{ __('quizzes.cols.status') }}</th>
                            <th role="columnheader" scope="col" class="table__num">{{ __('quizzes.cols.questions') }}</th>
                            <th role="columnheader" scope="col" class="table__num">{{ __('quizzes.cols.plays') }}</th>
                            <th role="columnheader" scope="col"><span class="visually-hidden">{{ __('admin.common.actions') }}</span></th>
                        </tr>
                    </thead>
                    <tbody role="rowgroup">
                        @foreach ($quizzes as $quiz)
                            <tr role="row">
                                <td role="cell">
                                    <span class="table__title"><a href="{{ route('admin.quizzes.edit', $quiz) }}">{{ $quiz->title }}</a></span>
                                    <span class="table__sub">{{ $quiz->category?->name }}</span>
                                </td>
                                <td role="cell" @class(['table__none' => ! $quiz->level])>{{ $quiz->level?->name ?? '—' }}</td>
                                <td role="cell"><span class="status status--{{ $quiz->status->value }}">{{ $quiz->status->label() }}</span></td>
                                <td role="cell" class="table__num" data-suffix="{{ mb_strtolower(__('quizzes.cols.questions')) }}">{{ $quiz->questions_count }}</td>
                                <td role="cell" class="table__num" data-suffix="{{ mb_strtolower(__('quizzes.cols.plays')) }}">{{ $quiz->attempts_count }}</td>
                                <td role="cell">
                                    <div class="actions">
                                        <x-button size="sm" :href="route('admin.quizzes.questions.edit', $quiz)"><x-icon name="list-checks" /> {{ __('quizzes.questions') }}</x-button>
                                        <x-button size="sm" :href="route('admin.quizzes.edit', $quiz)"><x-icon name="pencil" /> {{ __('admin.common.edit') }}</x-button>
                                    </div>
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>

            {{ $quizzes->links() }}
        @endif
    </section>
</x-layouts.admin>
