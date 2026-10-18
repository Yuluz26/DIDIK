<?php

namespace Tests\Concerns;

use App\Models\Question;
use App\Models\Quiz;

trait CreatesQuizzes
{
    /**
     * A published quiz whose questions each have three options; option "A" (position 0) is correct.
     *
     * @param  array<string, mixed>  $attributes
     */
    protected function publishedQuiz(int $questions = 3, array $attributes = []): Quiz
    {
        $quiz = Quiz::factory()->published()->create($attributes);

        for ($i = 1; $i <= $questions; $i++) {
            Question::factory()->for($quiz)->withOptions(3, 0)->create(['position' => $i]);
        }

        return $quiz->fresh();
    }

    /** The id of the correct option of a question. */
    protected function correctOptionId(int $questionId): int
    {
        return Question::withTrashed()->findOrFail($questionId)->options()->where('is_correct', true)->value('id');
    }

    /** The id of an option of a question that is NOT correct. */
    protected function wrongOptionId(int $questionId): int
    {
        return Question::withTrashed()->findOrFail($questionId)->options()->where('is_correct', false)->value('id');
    }
}
