<?php

namespace App\Services\QuizEngine;

use App\Enums\FeedbackMode;
use App\Models\Attempt;
use App\Models\Question;
use App\Models\Quiz;
use App\Services\QuizEngine\Exceptions\AlreadyAnswered;
use App\Services\QuizEngine\Exceptions\AttemptClosed;
use App\Services\QuizEngine\Exceptions\AttemptNotFinished;
use App\Services\QuizEngine\Exceptions\AttemptsExhausted;
use App\Services\QuizEngine\Exceptions\InvalidAnswer;
use App\Services\QuizEngine\Exceptions\QuizUnavailable;
use Illuminate\Support\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

/**
 * The quiz engine: starts attempts, checks answers on the server, scores, and builds what the
 * player and the result page are allowed to see. It knows nothing about game concepts.
 *
 * The browser never receives which option is correct before it has answered, and in
 * "feedback at the end" mode it does not learn that until the attempt is finished.
 */
class AttemptService
{
    /** An unfinished attempt older than this counts as abandoned and is not resumed. */
    public const RESUME_WINDOW_HOURS = 6;

    /**
     * Start a new attempt, or resume the visitor's unfinished one unless $restart is true.
     *
     * @throws QuizUnavailable
     * @throws AttemptsExhausted
     */
    public function startOrResume(Quiz $quiz, string $sessionHash, bool $restart = false): Attempt
    {
        if (! $quiz->isAvailable()) {
            throw new QuizUnavailable;
        }

        $open = $this->openAttempt($quiz, $sessionHash);

        if ($open && ! $restart) {
            return $open;
        }

        if ($this->attemptsRemaining($quiz, $sessionHash) === 0) {
            throw new AttemptsExhausted;
        }

        $layout = AttemptLayout::build($quiz);

        if ($layout['questions'] === []) {
            throw new QuizUnavailable;
        }

        return Attempt::create([
            'uuid' => (string) Str::uuid(),
            'quiz_id' => $quiz->id,
            'session_hash' => $sessionHash,
            'layout' => $layout,
            'started_at' => now(),
            'question_count' => count($layout['questions']),
            'max_score' => $this->maxScore($layout['questions']),
        ]);
    }

    /** Attempts the visitor may still make, or null when the quiz allows unlimited attempts. */
    public function attemptsRemaining(Quiz $quiz, string $sessionHash): ?int
    {
        if ($quiz->attempts_allowed === null) {
            return null;
        }

        $completed = Attempt::where('quiz_id', $quiz->id)
            ->where('session_hash', $sessionHash)
            ->whereNotNull('completed_at')
            ->count();

        return max(0, $quiz->attempts_allowed - $completed);
    }

    /**
     * Record one answer and check it. Posting the same answer again returns the same result,
     * so a retry after a dropped connection is safe. A different answer to an answered
     * question is refused. The last answer completes the attempt.
     *
     * @throws AttemptClosed
     * @throws InvalidAnswer
     * @throws AlreadyAnswered
     */
    public function answer(Attempt $attempt, int $questionId, int $optionId): AnswerResult
    {
        return DB::transaction(function () use ($attempt, $questionId, $optionId) {
            // Serialise concurrent answers on the same attempt (a double tap, a retry).
            $attempt = Attempt::whereKey($attempt->id)->lockForUpdate()->firstOrFail();

            $layout = $attempt->layout;

            if (! in_array($questionId, $layout['questions'], true)
                || ! in_array($optionId, $layout['options'][$questionId] ?? [], true)) {
                throw new InvalidAnswer;
            }

            $existing = $attempt->answers()->where('question_id', $questionId)->first();

            if ($existing === null && $attempt->isCompleted()) {
                throw new AttemptClosed;
            }

            if ($existing !== null && $existing->option_id !== $optionId) {
                throw new AlreadyAnswered;
            }

            $question = Question::withTrashed()
                ->with(['options' => fn ($query) => $query->withTrashed()])
                ->findOrFail($questionId);

            $answer = $existing ?? $attempt->answers()->create($this->grade($question, $optionId));

            $answered = $attempt->answers()->count();
            $total = count($layout['questions']);
            $finished = $attempt->isCompleted() || $answered >= $total;

            if ($finished && ! $attempt->isCompleted()) {
                $this->complete($attempt);
            }

            return new AnswerResult(
                correct: $answer->is_correct,
                correctOptionId: $question->options->firstWhere('is_correct', true)->id,
                explanation: $question->explanation,
                points: $answer->points_awarded,
                score: (int) $attempt->answers()->sum('points_awarded'),
                answered: $answered,
                total: $total,
                finished: $finished,
            );
        });
    }

    /**
     * Everything the player needs to run or resume an attempt. Option objects carry no
     * "correct" flag; correctness is only included for answers already given in instant mode.
     */
    public function playerState(Attempt $attempt): array
    {
        $quiz = $attempt->quiz;
        $layout = $attempt->layout;
        $instant = $quiz->feedback_mode === FeedbackMode::Instant;

        $questions = $this->questionsFor($layout['questions']);
        $answers = $attempt->answers()->get()->keyBy('question_id');

        return [
            'attempt' => $attempt->uuid,
            'finished' => $attempt->isCompleted(),
            'feedback_mode' => $quiz->feedback_mode->value,
            'questions' => collect($layout['questions'])->map(function (int $id) use ($questions, $layout) {
                $question = $questions[$id];

                return [
                    'id' => $question->id,
                    'type' => $question->type->value,
                    'body' => $question->body,
                    'points' => $question->points,
                    'options' => collect($layout['options'][$id])->map(fn (int $optionId) => [
                        'id' => $optionId,
                        'body' => $question->options->firstWhere('id', $optionId)->body,
                    ])->all(),
                ];
            })->values()->all(),
            'answers' => $answers->mapWithKeys(function ($answer) use ($questions, $instant) {
                $entry = ['option_id' => $answer->option_id];

                if ($instant) {
                    $question = $questions[$answer->question_id];
                    $entry += [
                        'correct' => $answer->is_correct,
                        'correct_option_id' => $question->options->firstWhere('is_correct', true)->id,
                        'explanation' => $question->explanation,
                    ];
                }

                return [$answer->question_id => $entry];
            })->all(),
            'score' => $instant ? (int) $answers->sum('points_awarded') : null,
        ];
    }

    /**
     * Question by question review of a finished attempt: the child's choice, the right
     * answer and the explanation.
     *
     * @return list<array<string, mixed>>
     *
     * @throws AttemptNotFinished
     */
    public function review(Attempt $attempt): array
    {
        if (! $attempt->isCompleted()) {
            throw new AttemptNotFinished;
        }

        $layout = $attempt->layout;
        $questions = $this->questionsFor($layout['questions']);
        $answers = $attempt->answers()->get()->keyBy('question_id');

        return collect($layout['questions'])->values()->map(function (int $id, int $index) use ($questions, $answers, $layout) {
            $question = $questions[$id];
            $answer = $answers->get($id);

            return [
                'number' => $index + 1,
                'body' => $question->body,
                'explanation' => $question->explanation,
                'correct' => (bool) $answer?->is_correct,
                'points' => $answer?->points_awarded ?? 0,
                'options' => collect($layout['options'][$id])->map(function (int $optionId) use ($question, $answer) {
                    $option = $question->options->firstWhere('id', $optionId);

                    return [
                        'id' => $optionId,
                        'body' => $option->body,
                        'chosen' => $answer?->option_id === $optionId,
                        'correct' => $option->is_correct,
                    ];
                })->all(),
            ];
        })->all();
    }

    /** Close the attempt and write its score, star count and finish time. */
    public function complete(Attempt $attempt): Attempt
    {
        $answers = $attempt->answers()->get(['is_correct', 'points_awarded']);
        $score = (int) $answers->sum('points_awarded');
        $max = $this->maxScore($attempt->layout['questions']);

        $attempt->update([
            'score' => $score,
            'max_score' => $max,
            'correct_count' => $answers->where('is_correct', true)->count(),
            'stars' => Scoring::stars($score, $max),
            'completed_at' => now(),
        ]);

        return $attempt;
    }

    private function openAttempt(Quiz $quiz, string $sessionHash): ?Attempt
    {
        return Attempt::where('quiz_id', $quiz->id)
            ->where('session_hash', $sessionHash)
            ->whereNull('completed_at')
            ->where('started_at', '>=', now()->subHours(self::RESUME_WINDOW_HOURS))
            ->latest('id')
            ->first();
    }

    /** @return array{question_id: int, option_id: int, is_correct: bool, points_awarded: int, answered_at: Carbon} */
    private function grade(Question $question, int $optionId): array
    {
        $correct = (bool) $question->options->firstWhere('id', $optionId)->is_correct;

        return [
            'question_id' => $question->id,
            'option_id' => $optionId,
            'is_correct' => $correct,
            'points_awarded' => $correct ? $question->points : 0,
            'answered_at' => now(),
        ];
    }

    /** @param  list<int>  $questionIds */
    private function maxScore(array $questionIds): int
    {
        return (int) Question::withTrashed()->whereIn('id', $questionIds)->sum('points');
    }

    /**
     * @param  list<int>  $ids
     * @return Collection<int, Question> keyed by id, with all options (soft-deleted ones included,
     *                                   because an admin may edit a quiz while an attempt is under way)
     */
    private function questionsFor(array $ids): Collection
    {
        return Question::withTrashed()
            ->with(['options' => fn ($query) => $query->withTrashed()->orderBy('position')->orderBy('id')])
            ->whereIn('id', $ids)
            ->get()
            ->keyBy('id');
    }
}
