<?php

namespace App\Services\Admin;

use App\Enums\QuizStatus;
use App\Models\Quiz;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;

/** Publishing, un-publishing, archiving and copying quizzes. */
class QuizWorkflow
{
    /**
     * Make the quiz public, or explain exactly why it cannot be yet.
     *
     * @throws ValidationException
     */
    public function publish(Quiz $quiz): void
    {
        $problems = $quiz->publishingProblems();

        if ($problems !== []) {
            throw ValidationException::withMessages(['status' => $problems]);
        }

        $quiz->update([
            'status' => QuizStatus::Published,
            'published_at' => $quiz->published_at ?? now(),
        ]);
    }

    public function unpublish(Quiz $quiz): void
    {
        $quiz->update(['status' => QuizStatus::Draft]);
    }

    public function archive(Quiz $quiz): void
    {
        $quiz->update(['status' => QuizStatus::Archived]);
    }

    /** A draft copy with its questions, answers and tags. Attempts are not copied. */
    public function duplicate(Quiz $quiz): Quiz
    {
        return DB::transaction(function () use ($quiz) {
            $quiz->loadMissing(['questions.options', 'tags']);

            $copy = $quiz->replicate(['slug', 'published_at']);
            $copy->title = __('quizzes.copy_title', ['title' => $quiz->title]);
            $copy->status = QuizStatus::Draft;
            $copy->save();

            $copy->syncTagNames($quiz->tags->pluck('name')->all());

            foreach ($quiz->questions as $question) {
                $newQuestion = $copy->questions()->create($question->only(['type', 'body', 'explanation', 'points', 'position']));

                foreach ($question->options as $option) {
                    $newQuestion->options()->create($option->only(['body', 'is_correct', 'position']));
                }
            }

            return $copy;
        });
    }
}
