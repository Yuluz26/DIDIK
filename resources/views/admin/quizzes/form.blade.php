@php
    $editing = $quiz->exists;
    $conceptKey = old('game_concept', $quiz->game_concept);
    $problems = $editing ? $quiz->publishingProblems() : [];
    $format = 'Y-m-d\TH:i';
@endphp

<x-layouts.admin :title="$editing ? $quiz->title : __('quizzes.create_title')">
    @if ($editing)
        <x-slot:actions>
            <x-button size="sm" :href="route('admin.quizzes.questions.edit', $quiz)"><x-icon name="list-checks" /> {{ __('quizzes.questions') }}</x-button>
            <x-button size="sm" :href="route('admin.quizzes.stats', $quiz)"><x-icon name="chart-no-axes-column" /> {{ __('quizzes.stats') }}</x-button>
            @if ($quiz->isAvailable())
                <x-button size="sm" :href="route('quizzes.show', $quiz->slug)" target="_blank" rel="noopener"><x-icon name="external-link" /> {{ __('quizzes.view_public') }}</x-button>
            @endif
        </x-slot:actions>

        {{-- Where the quiz stands, and the next sensible step --}}
        <section class="panel" aria-labelledby="state-title">
            <div class="panel__head">
                <h2 class="panel__title" id="state-title">
                    {{ __('quizzes.fields.status') }}:
                    <span class="status status--{{ $quiz->status->value }}">{{ $quiz->status->label() }}</span>
                    @if ($quiz->attempts_count > 0)
                        <small class="panel__note">{{ __('quizzes.has_attempts', ['count' => $quiz->attempts_count]) }}</small>
                    @endif
                </h2>

                <div class="actions">
                    @if ($quiz->status !== \App\Enums\QuizStatus::Published)
                        <form method="post" action="{{ route('admin.quizzes.publish', $quiz) }}">@csrf
                            <x-button variant="primary" size="sm" type="submit" :aria-disabled="$problems ? 'true' : 'false'"><x-icon name="eye" /> {{ __('quizzes.publish') }}</x-button>
                        </form>
                    @else
                        <form method="post" action="{{ route('admin.quizzes.unpublish', $quiz) }}">@csrf
                            <x-button size="sm" type="submit"><x-icon name="eye-off" /> {{ __('quizzes.unpublish') }}</x-button>
                        </form>
                    @endif
                    @if ($quiz->status !== \App\Enums\QuizStatus::Archived)
                        <form method="post" action="{{ route('admin.quizzes.archive', $quiz) }}">@csrf
                            <x-button size="sm" type="submit"><x-icon name="archive" /> {{ __('quizzes.archive') }}</x-button>
                        </form>
                    @endif
                    <form method="post" action="{{ route('admin.quizzes.duplicate', $quiz) }}">@csrf
                        <x-button size="sm" type="submit"><x-icon name="copy" /> {{ __('quizzes.duplicate') }}</x-button>
                    </form>
                </div>
            </div>

            @if ($problems && $quiz->status !== \App\Enums\QuizStatus::Published)
                <div class="alert alert--warn">
                    <x-icon name="triangle-alert" />
                    <div>
                        <strong>{{ __('quizzes.cannot_publish') }}</strong>
                        <ul>@foreach ($problems as $problem)<li>{{ $problem }}</li>@endforeach</ul>
                    </div>
                </div>
            @endif
        </section>
    @endif

    <form class="form" method="post" novalidate
          action="{{ $editing ? route('admin.quizzes.update', $quiz) : route('admin.quizzes.store') }}">
        @csrf
        @if ($editing) @method('PUT') @endif

        @include('admin.partials.errors')

        {{-- 1. Basics --}}
        <section class="panel form__section" aria-labelledby="sec-basic">
            <h2 class="panel__title" id="sec-basic">{{ __('quizzes.sections.basic') }}</h2>

            <x-field name="title" :label="__('quizzes.fields.title')" :value="$quiz->title" maxlength="160" required />
            <x-field name="summary" control="textarea" :label="__('quizzes.fields.summary')" :help="__('quizzes.fields.summary_help')" :value="$quiz->summary" maxlength="600" />

            <div class="form__grid form__grid--2">
                <x-field name="category_id" control="select" :label="__('quizzes.fields.category')">
                    <option value="">{{ __('quizzes.fields.select') }}</option>
                    @foreach ($subjects as $subject)
                        <optgroup label="{{ $subject->name }}">
                            <option value="{{ $subject->id }}" @selected((string) old('category_id', $quiz->category_id) === (string) $subject->id)>{{ $subject->name }}</option>
                            @foreach ($subject->children as $topic)
                                <option value="{{ $topic->id }}" @selected((string) old('category_id', $quiz->category_id) === (string) $topic->id)>{{ $subject->name }} › {{ $topic->name }}</option>
                            @endforeach
                        </optgroup>
                    @endforeach
                </x-field>

                <x-field name="school_level_id" control="select" :label="__('quizzes.fields.level')">
                    <option value="">{{ __('quizzes.fields.select') }}</option>
                    @foreach ($levels as $level)
                        <option value="{{ $level->id }}" @selected((string) old('school_level_id', $quiz->school_level_id) === (string) $level->id)>{{ $level->name }}</option>
                    @endforeach
                </x-field>

                <x-field name="difficulty" control="select" :label="__('quizzes.fields.difficulty')" required>
                    @foreach (\App\Enums\Difficulty::cases() as $case)
                        <option value="{{ $case->value }}" @selected(old('difficulty', $quiz->difficulty?->value) === $case->value)>{{ $case->label() }}</option>
                    @endforeach
                </x-field>

                <x-field name="language" control="select" :label="__('quizzes.fields.language')" :help="__('quizzes.fields.language_help')" required>
                    <option value="ms" @selected(old('language', $quiz->language) === 'ms')>Bahasa Melayu</option>
                    <option value="en" @selected(old('language', $quiz->language) === 'en')>English</option>
                </x-field>
            </div>

            <x-field name="tags" :label="__('quizzes.fields.tags')" :help="__('quizzes.fields.tags_help')" :value="$editing ? $quiz->tagList() : ''" maxlength="300" />
        </section>

        {{-- 2. How it is played. Settings for each concept come from the concept itself. --}}
        <section class="panel form__section" aria-labelledby="sec-play" x-data="conceptPicker(@js($conceptKey))">
            <h2 class="panel__title" id="sec-play">{{ __('quizzes.sections.play') }}</h2>
            <p class="field__hint">{{ __('quizzes.fields.concept_help') }}</p>

            <div class="choice-list" role="radiogroup" aria-labelledby="sec-play">
                @foreach ($concepts as $concept)
                    <label class="choice">
                        <input type="radio" name="game_concept" value="{{ $concept->key() }}" x-model="concept" @checked($conceptKey === $concept->key())>
                        <span class="choice__name">{{ $concept->name() }}</span>
                        <span class="choice__text">{{ $concept->description() }}</span>
                    </label>
                @endforeach
            </div>
            @error('game_concept')<p class="field__error"><x-icon name="circle-alert" /> {{ $message }}</p>@enderror

            @foreach ($concepts as $concept)
                @php($current = $concept->normalize($quiz->game_settings ?? []))
                {{-- A disabled fieldset submits nothing, so only the chosen concept's settings are sent. --}}
                <fieldset class="settings-box form__grid" x-show="concept === @js($concept->key())" :disabled="concept !== @js($concept->key())" @if ($conceptKey !== $concept->key()) x-cloak @endif>
                    <legend class="visually-hidden">{{ $concept->name() }}</legend>

                    @foreach ($concept->fields() as $name => $field)
                        @php($label = __("games.{$concept->key()}.fields.{$name}.label"))
                        @php($help = \Illuminate\Support\Facades\Lang::has("games.{$concept->key()}.fields.{$name}.help") ? __("games.{$concept->key()}.fields.{$name}.help") : null)

                        @if ($field['type'] === 'select')
                            <x-field :name="'game_settings['.$name.']'" control="select" :label="$label" :help="$help">
                                @foreach ($field['options'] as $option)
                                    <option value="{{ $option }}" @selected((string) old("game_settings.{$name}", $current[$name]) === (string) $option)>{{ __("games.{$concept->key()}.fields.{$name}.options.{$option}") }}</option>
                                @endforeach
                            </x-field>
                        @elseif ($field['type'] === 'boolean')
                            <x-check :name="'game_settings['.$name.']'" :label="$label" :help="$help" :checked="$current[$name]" />
                        @else
                            <x-field :name="'game_settings['.$name.']'" type="number" :min="$field['min']" :max="$field['max']" :label="$label" :help="$help" :value="$current[$name]" />
                        @endif
                    @endforeach
                </fieldset>
            @endforeach
        </section>

        {{-- 3. Rules --}}
        <section class="panel form__section" aria-labelledby="sec-rules">
            <h2 class="panel__title" id="sec-rules">{{ __('quizzes.sections.rules') }}</h2>

            <div class="form__grid form__grid--2">
                <x-field name="attempts_allowed" control="select" :label="__('quizzes.fields.attempts')" :help="__('quizzes.fields.attempts_help')">
                    <option value="">{{ __('quizzes.fields.attempts_unlimited') }}</option>
                    @foreach (range(1, 10) as $count)
                        <option value="{{ $count }}" @selected((string) old('attempts_allowed', $quiz->attempts_allowed) === (string) $count)>{{ $count }}</option>
                    @endforeach
                </x-field>

                <x-field name="feedback_mode" control="select" :label="__('quizzes.fields.feedback')" required>
                    @foreach (\App\Enums\FeedbackMode::cases() as $case)
                        <option value="{{ $case->value }}" @selected(old('feedback_mode', $quiz->feedback_mode?->value) === $case->value)>{{ $case->label() }}</option>
                    @endforeach
                </x-field>
            </div>

            <x-check name="shuffle_questions" :label="__('quizzes.fields.shuffle_questions')" :checked="$quiz->shuffle_questions" />
            <x-check name="shuffle_options" :label="__('quizzes.fields.shuffle_options')" :help="__('quizzes.fields.shuffle_options_help')" :checked="$quiz->shuffle_options" />
        </section>

        {{-- 4. Publishing (once the quiz exists) --}}
        @if ($editing)
            <section class="panel form__section" aria-labelledby="sec-publishing">
                <h2 class="panel__title" id="sec-publishing">{{ __('quizzes.sections.publishing') }}</h2>

                <x-field name="status" control="select" :label="__('quizzes.fields.status')" :help="__('quizzes.fields.status_help')" required>
                    @foreach (\App\Enums\QuizStatus::cases() as $case)
                        <option value="{{ $case->value }}" @selected(old('status', $quiz->status->value) === $case->value)>{{ $case->label() }}</option>
                    @endforeach
                </x-field>

                <div class="form__grid form__grid--2">
                    <x-field name="available_from" type="datetime-local" :label="__('quizzes.fields.from')" :value="$quiz->available_from?->format($format)" />
                    <x-field name="available_until" type="datetime-local" :label="__('quizzes.fields.until')" :value="$quiz->available_until?->format($format)" />
                </div>
                <p class="field__hint">{{ __('quizzes.fields.window_help') }}</p>
            </section>
        @endif

        <div class="form__actions">
            <x-button variant="primary" type="submit">{{ $editing ? __('admin.common.save') : __('quizzes.create') }}</x-button>
            <x-button :href="route('admin.quizzes.index')">{{ __('admin.common.cancel') }}</x-button>
        </div>
    </form>

    @if ($editing)
        <section class="panel">
            <div class="panel__head">
                <p class="panel__note">{{ __('quizzes.delete_text') }}</p>
                @include('admin.partials.delete', ['action' => route('admin.quizzes.destroy', $quiz), 'name' => $quiz->title, 'text' => __('quizzes.delete_text')])
            </div>
        </section>
    @endif
</x-layouts.admin>
