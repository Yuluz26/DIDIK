@php
    // Where an error-summary link should land: the specific control if there is one.
    $anchors = [];
    foreach ($errors->keys() as $key) {
        if (preg_match('/^questions\.(\d+)\.options\.(\d+)\.body$/', $key, $m)) {
            $anchors[$key] = "q-{$m[1]}-option-{$m[2]}";
        } elseif (preg_match('/^questions\.(\d+)\.(\w+)$/', $key, $m)) {
            $anchors[$key] = "q-{$m[1]}-".($m[2] === 'options' || $m[2] === 'correct' ? 'type' : $m[2]);
        }
    }

    $config = [
        'questions' => old('questions', $questions),
        'errors' => $errors->getMessages(),
        'max' => $maxQuestions,
        'strings' => [
            'dirty' => __('editor.dirty'),
            'clean' => __('editor.clean'),
            'removeTitle' => __('editor.remove_title', ['number' => ':number']),
            'option' => __('editor.option', ['letter' => ':letter']),
            'correctFor' => __('editor.correct_for', ['letter' => ':letter']),
            'removeOption' => __('editor.remove_option', ['letter' => ':letter']),
            'questionN' => __('editor.question_n', ['number' => ':number']),
            'noBody' => __('editor.no_body'),
            'answer' => __('editor.answer_is', ['answer' => ':answer']),
            'truth' => [__('enums.true_false.true'), __('enums.true_false.false')],
        ],
    ];
@endphp

<x-layouts.admin :title="__('editor.title', ['title' => $quiz->title])" :description="__('editor.intro')">
    <x-slot:actions>
        <x-button size="sm" :href="route('admin.quizzes.edit', $quiz)"><x-icon name="arrow-left" /> {{ __('editor.back') }}</x-button>
    </x-slot:actions>

    <form method="post" action="{{ route('admin.quizzes.questions.update', $quiz) }}" novalidate
          x-data="questionEditor(@literal($config))" @input="markDirty()" @submit="submit()" @click="reveal($event)">
        @csrf
        @method('PUT')

        @include('admin.partials.errors')

        <div class="editor">
            {{-- Nothing yet --}}
            <section class="panel" x-show="isEmpty" x-cloak>
                <div class="empty">
                    <x-mascot mood="think" size="md" />
                    <h2 class="empty__title">{{ __('editor.empty_title') }}</h2>
                    <p>{{ __('editor.empty_text') }}</p>
                </div>
            </section>

            {{-- Past a few questions the page is long: let the admin fold and unfold them together --}}
            <div class="actions" x-show="canFold" x-cloak>
                <button type="button" class="btn btn--sm" @click="openAll()"><x-icon name="chevron-down" /> {{ __('editor.open_all') }}</button>
                <button type="button" class="btn btn--sm" @click="closeAll()"><x-icon name="chevron-up" /> {{ __('editor.close_all') }}</button>
            </div>

            <template x-for="(q, i) in questions" :key="q.key">
                <section class="q-card" :id="'q-' + i" :aria-labelledby="fieldId(i, 'heading')" :data-open="q.open">
                    <div class="q-card__head">
                        <h2 class="q-card__number" :id="fieldId(i, 'heading')">
                            <button type="button" class="q-card__toggle" :aria-expanded="q.open" :aria-controls="'q-body-' + i" @click="toggle(q)">
                                <x-icon name="chevron-down" />
                                <span class="q-card__label">
                                    <span x-text="questionLabel(i)"></span>
                                    <span class="q-card__summary" x-show="!q.open" x-text="summary(q)"></span>
                                    <span class="q-card__answer" x-show="!q.open && answerText(q) !== ''" x-text="answerText(q)"></span>
                                </span>
                            </button>
                        </h2>
                        <div class="actions">
                            <button type="button" class="btn btn--sm" :id="fieldId(i, 'up')" @click="move(i, -1)" :aria-disabled="isFirst(i)" :disabled="isFirst(i)"><x-icon name="arrow-up" /> {{ __('editor.move_up') }}</button>
                            <button type="button" class="btn btn--sm" :id="fieldId(i, 'down')" @click="move(i, 1)" :aria-disabled="isLast(i)" :disabled="isLast(i)"><x-icon name="arrow-down" /> {{ __('editor.move_down') }}</button>
                            <button type="button" class="btn btn--sm" @click="duplicate(i)" :disabled="!canAdd"><x-icon name="copy" /> {{ __('editor.duplicate') }}</button>
                            <button type="button" class="btn btn--sm" @click="askRemove(i)"><x-icon name="trash-2" /> {{ __('editor.remove') }}</button>
                        </div>
                    </div>

                    {{-- Everything below stays in the page when folded (x-show, not x-if), so it is still submitted. --}}
                    <div class="q-card__body" :id="'q-body-' + i" x-show="q.open">

                    <input type="hidden" :name="name(i, 'id')" :value="q.id" :disabled="q.id === null">

                    {{-- The value that is submitted. The radios below only set it: Alpine binds a radio's
                         value once and never again, so after an option is removed a radio would keep a
                         stale index. --}}
                    <input type="hidden" :name="name(i, 'correct')" :value="q.correct">

                    <div class="form__grid form__grid--3">
                        <div class="field">
                            <label class="field__label" :for="fieldId(i, 'type')">{{ __('editor.type') }}</label>
                            <select class="field__control" :id="fieldId(i, 'type')" :name="name(i, 'type')" :value="q.type" @change="setType(q, $event.target.value)">
                                @foreach (\App\Enums\QuestionType::cases() as $case)
                                    <option value="{{ $case->value }}" :selected="q.type === '{{ $case->value }}'">{{ $case->label() }}</option>
                                @endforeach
                            </select>
                        </div>
                        <div class="field">
                            <label class="field__label" :for="fieldId(i, 'points')">{{ __('editor.points') }}</label>
                            <input class="field__control" type="number" min="1" max="10" :id="fieldId(i, 'points')" :name="name(i, 'points')" x-model.number="q.points" :aria-invalid="hasError(i, 'points')">
                            <p class="field__error" x-show="hasError(i, 'points')" x-text="errorFor(i, 'points')" x-cloak></p>
                        </div>
                    </div>

                    <div :class="hasError(i, 'body') ? 'field field--invalid' : 'field'">
                        <label class="field__label" :for="fieldId(i, 'body')">{{ __('editor.body') }}<span class="field__flag">{{ __('admin.common.required') }}</span></label>
                        <textarea class="field__control" rows="2" maxlength="1000" :id="fieldId(i, 'body')" :name="name(i, 'body')" x-model="q.body" :aria-invalid="hasError(i, 'body')"></textarea>
                        <p class="field__error" x-show="hasError(i, 'body')" x-cloak><x-icon name="circle-alert" /> <span x-text="errorFor(i, 'body')"></span></p>
                    </div>

                    {{-- Multiple choice: two to five options, one marked right.
                         x-if, not x-show: both variants name their radios questions[i][correct], and
                         radios with one name form one group even when hidden, so only the live one may exist. --}}
                    <template x-if="isSingle(q)">
                    <fieldset class="q-fixed">
                        <legend class="field__label">{{ __('editor.options') }}</legend>
                        <ul class="q-options">
                            <template x-for="(o, j) in q.options" :key="o.key">
                                <li class="q-option">
                                    <label class="q-option__correct">
                                        <input type="radio" :name="'pick-' + q.key" :checked="q.correct === j" @change="q.correct = j" :aria-label="correctLabel(j)">
                                        <span aria-hidden="true">{{ __('editor.correct') }}</span>
                                    </label>
                                    <div class="field">
                                        <input type="hidden" :name="name(i, 'options', j, 'id')" :value="o.id" :disabled="o.id === null">
                                        <input class="field__control" type="text" maxlength="255" :id="fieldId(i, 'option-' + j)" :name="name(i, 'options', j, 'body')" x-model="o.body" :aria-label="optionLabel(j)" :placeholder="optionLabel(j)" :aria-invalid="optionError(i, j) !== ''">
                                        <p class="field__error" x-show="optionError(i, j) !== ''" x-cloak><x-icon name="circle-alert" /> <span x-text="optionError(i, j)"></span></p>
                                    </div>
                                    <button type="button" class="btn btn--sm btn--icon" @click="removeOption(q, j)" :disabled="!canRemoveOption(q)" :aria-label="removeOptionLabel(j)"><x-icon name="x" /></button>
                                </li>
                            </template>
                        </ul>
                        <p class="field__error" x-show="hasError(i, 'options') || hasError(i, 'correct')" x-cloak><x-icon name="circle-alert" /> <span x-text="errorFor(i, 'options') || errorFor(i, 'correct')"></span></p>
                        <div><button type="button" class="btn btn--sm" @click="addOption(q)" :disabled="!canAddOption(q)"><x-icon name="plus" /> {{ __('editor.add_option') }}</button></div>
                    </fieldset>
                    </template>

                    {{-- True or false: the two answers are fixed, only the right one is chosen --}}
                    <template x-if="isTrueFalse(q)">
                    <fieldset class="q-fixed">
                        <legend class="field__label">{{ __('editor.true_false') }}</legend>
                        <label class="q-option__correct">
                            <input type="radio" :name="'pick-' + q.key" :checked="q.correct === 0" @change="q.correct = 0">
                            {{ __('enums.true_false.true') }}
                        </label>
                        <label class="q-option__correct">
                            <input type="radio" :name="'pick-' + q.key" :checked="q.correct === 1" @change="q.correct = 1">
                            {{ __('enums.true_false.false') }}
                        </label>
                    </fieldset>
                    </template>

                    <div class="field">
                        <label class="field__label" :for="fieldId(i, 'explanation')">{{ __('editor.explanation') }}<span class="field__flag">{{ __('admin.common.optional') }}</span></label>
                        <p class="field__hint">{{ __('editor.explanation_help') }}</p>
                        <textarea class="field__control" rows="2" maxlength="1000" :id="fieldId(i, 'explanation')" :name="name(i, 'explanation')" x-model="q.explanation"></textarea>
                        <p class="field__error" x-show="hasError(i, 'explanation')" x-text="errorFor(i, 'explanation')" x-cloak></p>
                    </div>
                    </div>
                </section>
            </template>

            <div class="form__actions">
                <button type="button" class="btn" @click="addQuestion()" :disabled="!canAdd"><x-icon name="plus" /> {{ __('editor.add_question') }}</button>
                <button type="button" class="btn" @click="addTrueFalse()" :disabled="!canAdd"><x-icon name="plus" /> {{ __('editor.add_true_false') }}</button>
                <p class="panel__note" x-show="!canAdd" x-cloak>{{ __('editor.limit', ['max' => $maxQuestions]) }}</p>
            </div>

            <div class="savebar">
                <p class="savebar__state" role="status" :data-dirty="dirtyFlag" x-text="stateText">{{ __('editor.clean') }}</p>
                <p class="panel__note">{{ __('editor.publish_hint') }}</p>
                <x-button variant="primary" type="submit"><x-icon name="save" /> {{ __('editor.save_all') }}</x-button>
            </div>
        </div>

        <dialog class="dialog" x-ref="removeDialog" aria-labelledby="remove-title">
            <h2 id="remove-title" class="dialog__title" x-text="removeTitle"></h2>
            <p>{{ __('editor.remove_text') }}</p>
            <div class="dialog__actions">
                <button type="button" class="btn" data-dialog-close>{{ __('admin.common.cancel') }}</button>
                <button type="button" class="btn btn--danger" @click="confirmRemove()"><x-icon name="trash-2" /> {{ __('editor.remove_confirm') }}</button>
            </div>
        </dialog>
    </form>
</x-layouts.admin>
