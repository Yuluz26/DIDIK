<?php

namespace App\Http\Requests\Admin;

use App\Enums\Difficulty;
use App\Enums\FeedbackMode;
use App\Enums\QuizStatus;
use App\Games\GameConceptRegistry;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class QuizRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, mixed> */
    public function rules(): array
    {
        $registry = app(GameConceptRegistry::class);

        return [
            'title' => ['required', 'string', 'max:160'],
            'summary' => ['nullable', 'string', 'max:600'],
            'language' => ['required', Rule::in(['ms', 'en'])],
            'category_id' => ['nullable', 'integer', 'exists:categories,id'],
            'school_level_id' => ['nullable', 'integer', 'exists:school_levels,id'],
            'difficulty' => ['required', Rule::enum(Difficulty::class)],
            'status' => ['sometimes', Rule::enum(QuizStatus::class)],
            'game_concept' => ['required', Rule::in($registry->keys())],
            'game_settings' => ['nullable', 'array'],
            // Only the chosen concept's settings are validated; the rest are discarded on save.
            ...$registry->resolve($this->input('game_concept'))->rules('game_settings'),
            'attempts_allowed' => ['nullable', 'integer', 'min:1', 'max:20'],
            'feedback_mode' => ['required', Rule::enum(FeedbackMode::class)],
            'shuffle_questions' => ['boolean'],
            'shuffle_options' => ['boolean'],
            'available_from' => ['nullable', 'date'],
            'available_until' => ['nullable', 'date', Rule::when($this->filled('available_from'), ['after:available_from'])],
            'tags' => ['nullable', 'string', 'max:300'],
        ];
    }

    /**
     * The fields that go straight onto the quiz (everything but tags and status), with the
     * game settings reduced to what the chosen concept actually supports.
     *
     * @return array<string, mixed>
     */
    public function quizAttributes(): array
    {
        $data = $this->validated();
        $concept = app(GameConceptRegistry::class)->get($data['game_concept']);

        $data['game_settings'] = $concept->normalize($data['game_settings'] ?? []);
        $data['shuffle_questions'] = (bool) ($data['shuffle_questions'] ?? false);
        $data['shuffle_options'] = (bool) ($data['shuffle_options'] ?? false);

        unset($data['tags'], $data['status']);

        return $data;
    }
}
