<?php

namespace App\Http\Requests\Admin;

use App\Enums\QuestionType;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

/**
 * Validates every question of a quiz at once. Rules are built per question because a true/false
 * question has no option list and a multiple-choice one needs two to five options and exactly
 * one marked correct. Error messages name the question ("Soalan 3"), not a form path.
 */
class QuestionSetRequest extends FormRequest
{
    public const MAX_QUESTIONS = 100;

    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, mixed> */
    public function rules(): array
    {
        $rules = ['questions' => ['nullable', 'array', 'max:'.self::MAX_QUESTIONS]];

        foreach ((array) $this->input('questions', []) as $i => $question) {
            $isTrueFalse = ($question['type'] ?? null) === QuestionType::TrueFalse->value;

            $rules["questions.{$i}.id"] = ['nullable', 'integer'];
            $rules["questions.{$i}.type"] = ['required', Rule::enum(QuestionType::class)];
            $rules["questions.{$i}.body"] = ['required', 'string', 'max:1000'];
            $rules["questions.{$i}.explanation"] = ['nullable', 'string', 'max:1000'];
            $rules["questions.{$i}.points"] = ['required', 'integer', 'between:1,10'];

            if ($isTrueFalse) {
                $rules["questions.{$i}.correct"] = ['required', 'integer', 'between:0,1'];

                continue;
            }

            $count = count((array) ($question['options'] ?? []));

            $rules["questions.{$i}.options"] = ['required', 'array', 'min:2', 'max:5'];
            $rules["questions.{$i}.options.*.id"] = ['nullable', 'integer'];
            $rules["questions.{$i}.options.*.body"] = ['required', 'string', 'max:255'];
            $rules["questions.{$i}.correct"] = ['required', 'integer', 'between:0,'.max(0, $count - 1)];
        }

        return $rules;
    }

    /** @return array<string, string> */
    public function attributes(): array
    {
        $attributes = ['questions' => __('editor.questions')];

        foreach ((array) $this->input('questions', []) as $i => $question) {
            $number = $i + 1;

            $attributes["questions.{$i}.body"] = __('editor.attr_body', ['number' => $number]);
            $attributes["questions.{$i}.explanation"] = __('editor.attr_explanation', ['number' => $number]);
            $attributes["questions.{$i}.points"] = __('editor.attr_points', ['number' => $number]);
            $attributes["questions.{$i}.type"] = __('editor.attr_type', ['number' => $number]);
            $attributes["questions.{$i}.options"] = __('editor.attr_options', ['number' => $number]);
            $attributes["questions.{$i}.correct"] = __('editor.attr_correct', ['number' => $number]);

            foreach (array_keys((array) ($question['options'] ?? [])) as $j) {
                $attributes["questions.{$i}.options.{$j}.body"] = __('editor.attr_option', [
                    'number' => $number,
                    'letter' => chr(65 + (int) $j),
                ]);
            }
        }

        return $attributes;
    }

    /** @return list<array<string, mixed>> */
    public function questions(): array
    {
        return array_values($this->validated()['questions'] ?? []);
    }
}
