<?php

namespace App\Services\QuizEngine;

use App\Enums\QuestionType;
use App\Models\Quiz;

/**
 * Decides, once when an attempt starts, which questions are asked and in what order, and the
 * order of each question's options. The result is stored on the attempt, so a refresh or a
 * later edit by an admin cannot reshuffle or change an attempt that is already under way.
 */
final class AttemptLayout
{
    /**
     * @return array{questions: list<int>, options: array<int, list<int>>}
     */
    public static function build(Quiz $quiz): array
    {
        // A question can only be asked if it has a clear right answer to check against.
        $questions = $quiz->questions()->with('options')->get()
            ->filter(fn ($question) => $question->options->count() >= 2
                && $question->options->where('is_correct', true)->count() === 1);

        if ($quiz->shuffle_questions) {
            $questions = $questions->shuffle();
        }

        $options = [];

        foreach ($questions as $question) {
            $ordered = $quiz->shuffle_options && $question->type === QuestionType::Single
                ? $question->options->shuffle()
                : $question->options;

            $options[$question->id] = $ordered->pluck('id')->values()->all();
        }

        return [
            'questions' => $questions->pluck('id')->values()->all(),
            'options' => $options,
        ];
    }
}
