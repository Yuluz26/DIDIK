<?php

namespace App\Services;

use App\Enums\QuestionType;
use App\Models\Question;
use App\Models\Quiz;

/**
 * The homepage's "try one question". Picks one real single-answer question from an available
 * quiz, the same one all day, and checks answers on the server like the quizzes do.
 */
class LiveQuestion
{
    private const MAX_OPTION_LENGTH = 30;

    private const MAX_BODY_LENGTH = 140;

    /** @return array{question_id: int, body: string, options: list<array{id: int, body: string}>, quiz: Quiz}|null */
    public function today(): ?array
    {
        $ids = Question::query()
            ->where('type', QuestionType::Single)
            ->whereHas('quiz', fn ($quiz) => $quiz->available())
            ->pluck('id')
            ->sortBy(fn (int $id) => crc32(now()->toDateString().'|'.$id))
            ->take(12);

        foreach ($ids as $id) {
            $question = Question::with(['options', 'quiz'])->find($id);

            if ($question && $this->fitsTheStones($question)) {
                return [
                    'question_id' => $question->id,
                    'body' => $question->body,
                    'options' => $question->options->map(fn ($option) => ['id' => $option->id, 'body' => $option->body])->all(),
                    'quiz' => $question->quiz,
                ];
            }
        }

        return null;
    }

    /** @return array{correct: bool, correct_option_id: int, explanation: ?string}|null null when the question is not publicly available */
    public function check(int $questionId, int $optionId): ?array
    {
        $question = Question::with('options')
            ->where('type', QuestionType::Single)
            ->whereHas('quiz', fn ($quiz) => $quiz->available())
            ->find($questionId);

        $option = $question?->options->firstWhere('id', $optionId);
        $correct = $question?->options->firstWhere('is_correct', true);

        if (! $option || ! $correct) {
            return null;
        }

        return [
            'correct' => $option->is_correct,
            'correct_option_id' => $correct->id,
            'explanation' => $question->explanation,
        ];
    }

    private function fitsTheStones(Question $question): bool
    {
        $options = $question->options;

        return $options->count() >= 2
            && $options->count() <= 4
            && $options->where('is_correct', true)->count() === 1
            && mb_strlen($question->body) <= self::MAX_BODY_LENGTH
            && $options->every(fn ($option) => mb_strlen($option->body) <= self::MAX_OPTION_LENGTH);
    }
}
