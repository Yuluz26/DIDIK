<?php

namespace Tests\Feature\QuizEngine;

use App\Enums\FeedbackMode;
use App\Enums\QuestionType;
use App\Enums\QuizStatus;
use App\Models\Attempt;
use App\Models\Question;
use App\Models\QuestionOption;
use App\Models\Quiz;
use App\Services\QuizEngine\AttemptService;
use App\Services\QuizEngine\Exceptions\AlreadyAnswered;
use App\Services\QuizEngine\Exceptions\AttemptClosed;
use App\Services\QuizEngine\Exceptions\AttemptNotFinished;
use App\Services\QuizEngine\Exceptions\AttemptsExhausted;
use App\Services\QuizEngine\Exceptions\InvalidAnswer;
use App\Services\QuizEngine\Exceptions\QuizUnavailable;
use Illuminate\Database\QueryException;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class AttemptServiceTest extends TestCase
{
    use CreatesQuizzes, RefreshDatabase;

    private const SESSION = 'hash-of-session-one';

    private AttemptService $engine;

    protected function setUp(): void
    {
        parent::setUp();

        $this->engine = app(AttemptService::class);
    }

    public function test_starting_builds_a_layout_from_playable_questions_only(): void
    {
        $quiz = $this->publishedQuiz(3);
        // Unplayable: one option only, and no correct option.
        Question::factory()->for($quiz)->create(['position' => 4]);
        $noCorrect = Question::factory()->for($quiz)->create(['position' => 5]);
        QuestionOption::create(['question_id' => $noCorrect->id, 'body' => 'x', 'position' => 1]);
        QuestionOption::create(['question_id' => $noCorrect->id, 'body' => 'y', 'position' => 2]);

        $attempt = $this->engine->startOrResume($quiz, self::SESSION);

        $this->assertCount(3, $attempt->layout['questions']);
        $this->assertSame(3, $attempt->question_count);
        $this->assertSame(3, $attempt->max_score);
        $this->assertNull($attempt->completed_at);
    }

    public function test_an_unfinished_attempt_is_resumed_unless_a_restart_is_asked_for(): void
    {
        $quiz = $this->publishedQuiz(2);

        $first = $this->engine->startOrResume($quiz, self::SESSION);
        $again = $this->engine->startOrResume($quiz, self::SESSION);
        $restarted = $this->engine->startOrResume($quiz, self::SESSION, restart: true);
        $other = $this->engine->startOrResume($quiz, 'hash-of-someone-else');

        $this->assertTrue($first->is($again));
        $this->assertFalse($first->is($restarted));
        $this->assertFalse($restarted->is($other));
    }

    public function test_an_attempt_abandoned_long_ago_is_not_resumed(): void
    {
        $quiz = $this->publishedQuiz(2);
        $old = $this->engine->startOrResume($quiz, self::SESSION);
        $old->update(['started_at' => now()->subHours(AttemptService::RESUME_WINDOW_HOURS + 1)]);

        $new = $this->engine->startOrResume($quiz, self::SESSION);

        $this->assertFalse($old->is($new));
    }

    public function test_quizzes_that_are_not_available_cannot_be_started(): void
    {
        $draft = Quiz::factory()->create();
        $archived = Quiz::factory()->archived()->create();
        $future = $this->publishedQuiz(1, ['available_from' => now()->addDay()]);
        $expired = $this->publishedQuiz(1, ['available_until' => now()->subDay()]);
        $empty = Quiz::factory()->published()->create();

        foreach ([$draft, $archived, $future, $expired, $empty] as $quiz) {
            try {
                $this->engine->startOrResume($quiz, self::SESSION);
                $this->fail("Quiz {$quiz->title} should not be startable.");
            } catch (QuizUnavailable) {
                $this->addToAssertionCount(1);
            }
        }
    }

    public function test_the_attempt_limit_counts_finished_attempts_only(): void
    {
        $quiz = $this->publishedQuiz(1, ['attempts_allowed' => 2]);

        $this->assertSame(2, $this->engine->attemptsRemaining($quiz, self::SESSION));

        // An abandoned attempt does not use one up.
        $this->engine->startOrResume($quiz, self::SESSION);
        $this->assertSame(2, $this->engine->attemptsRemaining($quiz, self::SESSION));

        $this->finish($quiz);
        $this->assertSame(1, $this->engine->attemptsRemaining($quiz, self::SESSION));

        $this->finish($quiz);
        $this->assertSame(0, $this->engine->attemptsRemaining($quiz, self::SESSION));

        $this->expectException(AttemptsExhausted::class);
        $this->engine->startOrResume($quiz, self::SESSION);
    }

    public function test_unlimited_quizzes_report_no_limit(): void
    {
        $this->assertNull($this->engine->attemptsRemaining($this->publishedQuiz(1), self::SESSION));
    }

    public function test_a_correct_answer_earns_the_question_points(): void
    {
        $quiz = $this->publishedQuiz(2);
        $quiz->questions()->update(['points' => 3]);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        $questionId = $attempt->layout['questions'][0];

        $result = $this->engine->answer($attempt, $questionId, $this->correctOptionId($questionId));

        $this->assertTrue($result->correct);
        $this->assertSame(3, $result->points);
        $this->assertSame(3, $result->score);
        $this->assertSame(1, $result->answered);
        $this->assertSame(2, $result->total);
        $this->assertFalse($result->finished);
    }

    public function test_a_wrong_answer_earns_nothing_and_reveals_the_right_option(): void
    {
        $quiz = $this->publishedQuiz(2);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        $questionId = $attempt->layout['questions'][0];

        $result = $this->engine->answer($attempt, $questionId, $this->wrongOptionId($questionId));

        $this->assertFalse($result->correct);
        $this->assertSame(0, $result->points);
        $this->assertSame($this->correctOptionId($questionId), $result->correctOptionId);
    }

    public function test_answering_the_same_option_twice_is_safe_to_retry(): void
    {
        $quiz = $this->publishedQuiz(2);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        $questionId = $attempt->layout['questions'][0];
        $optionId = $this->correctOptionId($questionId);

        $first = $this->engine->answer($attempt, $questionId, $optionId);
        $retry = $this->engine->answer($attempt, $questionId, $optionId);

        $this->assertEquals($first, $retry);
        $this->assertSame(1, $attempt->answers()->count());
    }

    public function test_changing_an_answer_is_refused(): void
    {
        $quiz = $this->publishedQuiz(2);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        $questionId = $attempt->layout['questions'][0];
        $this->engine->answer($attempt, $questionId, $this->wrongOptionId($questionId));

        $this->expectException(AlreadyAnswered::class);
        $this->engine->answer($attempt, $questionId, $this->correctOptionId($questionId));
    }

    public function test_questions_and_options_from_outside_the_attempt_are_rejected(): void
    {
        $quiz = $this->publishedQuiz(2);
        $other = $this->publishedQuiz(1);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        $questionId = $attempt->layout['questions'][0];
        $foreignQuestion = $other->questions()->first();

        $this->assertThrowsInvalid(fn () => $this->engine->answer($attempt, $foreignQuestion->id, $this->correctOptionId($foreignQuestion->id)));
        // An option that exists but belongs to a different question.
        $this->assertThrowsInvalid(fn () => $this->engine->answer($attempt, $questionId, $this->correctOptionId($foreignQuestion->id)));
        $this->assertThrowsInvalid(fn () => $this->engine->answer($attempt, $questionId, 999999));
        $this->assertSame(0, $attempt->answers()->count());
    }

    public function test_the_last_answer_completes_the_attempt_with_score_and_stars(): void
    {
        $quiz = $this->publishedQuiz(4);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);

        foreach ($attempt->layout['questions'] as $index => $questionId) {
            $optionId = $index < 3 ? $this->correctOptionId($questionId) : $this->wrongOptionId($questionId);
            $result = $this->engine->answer($attempt, $questionId, $optionId);
        }

        $attempt->refresh();

        $this->assertTrue($result->finished);
        $this->assertNotNull($attempt->completed_at);
        $this->assertSame(3, $attempt->score);
        $this->assertSame(4, $attempt->max_score);
        $this->assertSame(3, $attempt->correct_count);
        $this->assertSame(2, $attempt->stars); // 75 percent
    }

    public function test_a_completed_attempt_accepts_no_new_answers(): void
    {
        $quiz = $this->publishedQuiz(2);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        $questionId = $attempt->layout['questions'][0];
        $this->engine->complete($attempt);

        $this->expectException(AttemptClosed::class);
        $this->engine->answer($attempt, $questionId, $this->correctOptionId($questionId));
    }

    public function test_the_player_state_never_carries_the_correct_flag(): void
    {
        $quiz = $this->publishedQuiz(3);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);

        $json = json_encode($this->engine->playerState($attempt));

        $this->assertStringNotContainsString('is_correct', $json);
        $this->assertStringNotContainsString('"correct"', $json);
        $this->assertStringNotContainsString('explanation', $json);
    }

    public function test_in_instant_mode_a_resumed_state_includes_feedback_for_answered_questions_only(): void
    {
        $quiz = $this->publishedQuiz(3);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        [$first, $second] = $attempt->layout['questions'];
        $this->engine->answer($attempt, $first, $this->wrongOptionId($first));

        $state = $this->engine->playerState($attempt->fresh());

        $this->assertSame(FeedbackMode::Instant->value, $state['feedback_mode']);
        $this->assertArrayHasKey($first, $state['answers']);
        $this->assertFalse($state['answers'][$first]['correct']);
        $this->assertSame($this->correctOptionId($first), $state['answers'][$first]['correct_option_id']);
        $this->assertArrayNotHasKey($second, $state['answers']);
        $this->assertSame(0, $state['score']);
    }

    public function test_in_end_mode_nothing_about_correctness_is_revealed_until_the_review(): void
    {
        $quiz = $this->publishedQuiz(2, ['feedback_mode' => FeedbackMode::End]);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        $first = $attempt->layout['questions'][0];
        $this->engine->answer($attempt, $first, $this->correctOptionId($first));

        $state = $this->engine->playerState($attempt->fresh());

        $this->assertSame(['option_id' => $this->correctOptionId($first)], $state['answers'][$first]);
        $this->assertNull($state['score']);

        $this->expectException(AttemptNotFinished::class);
        $this->engine->review($attempt->fresh());
    }

    public function test_the_review_lists_choice_right_answer_and_explanation(): void
    {
        $quiz = $this->publishedQuiz(2);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        [$first, $second] = $attempt->layout['questions'];
        $this->engine->answer($attempt, $first, $this->correctOptionId($first));
        $wrong = $this->wrongOptionId($second);
        $this->engine->answer($attempt, $second, $wrong);

        $review = $this->engine->review($attempt->fresh());

        $this->assertCount(2, $review);
        $this->assertTrue($review[0]['correct']);
        $this->assertFalse($review[1]['correct']);
        $this->assertNotNull($review[1]['explanation']);
        $chosen = collect($review[1]['options'])->firstWhere('chosen', true);
        $this->assertSame($wrong, $chosen['id']);
        $this->assertSame(1, collect($review[1]['options'])->where('correct', true)->count());
    }

    public function test_shuffled_order_is_fixed_for_the_attempt_and_true_false_is_never_shuffled(): void
    {
        $quiz = $this->publishedQuiz(0, ['shuffle_questions' => true, 'shuffle_options' => true]);
        $tf = Question::factory()->for($quiz)->create(['type' => QuestionType::TrueFalse, 'position' => 1]);
        QuestionOption::create(['question_id' => $tf->id, 'body' => 'Betul', 'is_correct' => true, 'position' => 1]);
        QuestionOption::create(['question_id' => $tf->id, 'body' => 'Salah', 'is_correct' => false, 'position' => 2]);

        for ($i = 0; $i < 10; $i++) {
            $attempt = $this->engine->startOrResume($quiz, "hash-{$i}");
            $this->assertSame(
                $tf->options()->orderBy('position')->pluck('id')->all(),
                $attempt->layout['options'][$tf->id],
            );
        }

        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        // assertEquals, not assertSame: MySQL's JSON type reorders object keys, the data is the same.
        $this->assertEquals($attempt->layout, $this->engine->startOrResume($quiz, self::SESSION)->layout);
    }

    public function test_the_database_allows_only_one_correct_option_per_question(): void
    {
        $quiz = $this->publishedQuiz(1);
        $question = $quiz->questions()->first();

        $this->expectException(QueryException::class);
        QuestionOption::create(['question_id' => $question->id, 'body' => 'Second right answer', 'is_correct' => true, 'position' => 9]);
    }

    public function test_a_soft_deleted_correct_option_frees_the_slot(): void
    {
        $quiz = $this->publishedQuiz(1);
        $question = $quiz->questions()->first();
        $question->options()->where('is_correct', true)->first()->delete();

        $replacement = QuestionOption::create(['question_id' => $question->id, 'body' => 'New right answer', 'is_correct' => true, 'position' => 9]);

        $this->assertTrue($replacement->exists);
    }

    public function test_an_admin_editing_a_quiz_mid_attempt_does_not_break_the_attempt(): void
    {
        $quiz = $this->publishedQuiz(2);
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);
        [$first, $second] = $attempt->layout['questions'];

        // The admin deletes the second question while the child is playing.
        Question::findOrFail($second)->delete();
        $quiz->update(['status' => QuizStatus::Archived]);

        $this->engine->answer($attempt, $first, $this->correctOptionId($first));
        $result = $this->engine->answer($attempt, $second, $this->correctOptionId($second));

        $this->assertTrue($result->finished);
        $this->assertSame(2, $attempt->fresh()->correct_count);
    }

    private function assertThrowsInvalid(callable $call): void
    {
        try {
            $call();
            $this->fail('Expected InvalidAnswer.');
        } catch (InvalidAnswer) {
            $this->addToAssertionCount(1);
        }
    }

    /** Play a fresh attempt to the end, answering everything correctly. */
    private function finish(Quiz $quiz): Attempt
    {
        $attempt = $this->engine->startOrResume($quiz, self::SESSION);

        foreach ($attempt->layout['questions'] as $questionId) {
            $this->engine->answer($attempt, $questionId, $this->correctOptionId($questionId));
        }

        return $attempt->fresh();
    }
}
