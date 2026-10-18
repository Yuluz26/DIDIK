<?php

namespace Tests\Feature\Site;

use App\Enums\QuizStatus;
use App\Models\Quiz;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Testing\TestResponse;
use Tests\Concerns\ActsAsVisitors;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class ResultPageTest extends TestCase
{
    use ActsAsVisitors, CreatesQuizzes, RefreshDatabase;

    /** Play a quiz as $visitor; every question is answered correctly unless listed in $wrong (by position). */
    private function play(string $visitor, Quiz $quiz, array $wrong = []): array
    {
        $state = $this->asVisitor($visitor, fn () => $this->postJson(route('attempts.start', $quiz->slug)))->json();

        foreach ($state['questions'] as $index => $question) {
            $option = in_array($index, $wrong, true)
                ? $this->wrongOptionId($question['id'])
                : $this->correctOptionId($question['id']);

            $this->asVisitor($visitor, fn () => $this->postJson($state['urls']['answer'], [
                'question_id' => $question['id'],
                'option_id' => $option,
            ]))->assertOk();
        }

        return $state;
    }

    private function resultPage(string $visitor, array $state): TestResponse
    {
        return $this->asVisitor($visitor, fn () => $this->get($state['urls']['result']));
    }

    public function test_the_player_sees_stars_the_score_and_a_review_with_explanations(): void
    {
        $quiz = $this->publishedQuiz(4);
        $state = $this->play('child', $quiz, wrong: [3]);

        $this->resultPage('child', $state)
            ->assertOk()
            ->assertSee(__('public.result.score', ['correct' => 3, 'total' => 4]))
            ->assertSee(__('public.result.stars', ['count' => 2]))
            ->assertSee(__('public.result.two'))
            ->assertSee(__('public.result.question_correct'))
            ->assertSee(__('public.result.question_wrong'))
            ->assertSee(__('public.result.replay'))
            ->assertSee('<meta name="robots" content="noindex">', false);
    }

    public function test_points_are_only_listed_when_questions_are_worth_different_amounts(): void
    {
        // One point each: "3 of 4 questions" already says it all.
        $even = $this->publishedQuiz(4);
        $this->resultPage('even', $this->play('even', $even, wrong: [3]))
            ->assertSee(__('public.result.score', ['correct' => 3, 'total' => 4]))
            ->assertDontSee(__('public.result.points', ['score' => 3, 'max' => 4]));

        // A question worth three points makes the points line meaningful.
        $weighted = $this->publishedQuiz(2);
        $weighted->questions()->orderBy('position')->first()->update(['points' => 3]);
        $this->resultPage('weighted', $this->play('weighted', $weighted, wrong: [1]))
            ->assertSee(__('public.result.points', ['score' => 3, 'max' => 4]));
    }

    public function test_a_perfect_run_earns_three_stars_and_everyone_earns_at_least_one(): void
    {
        $quiz = $this->publishedQuiz(2);

        $this->resultPage('proud', $this->play('proud', $quiz))->assertSee(__('public.result.three'));
        $this->resultPage('trying', $this->play('trying', $quiz, wrong: [0, 1]))->assertSee(__('public.result.one'));
    }

    public function test_only_the_device_that_played_can_read_the_review(): void
    {
        $quiz = $this->publishedQuiz(2);
        $state = $this->play('child', $quiz);

        $this->resultPage('stranger', $state)
            ->assertNotFound()
            ->assertSee(__('public.result.private_title'))
            ->assertDontSee('explanation');
    }

    public function test_an_unfinished_attempt_goes_back_to_the_player(): void
    {
        $quiz = $this->publishedQuiz(2);
        $state = $this->asVisitor('child', fn () => $this->postJson(route('attempts.start', $quiz->slug)))->json();

        $this->resultPage('child', $state)->assertRedirect(route('quizzes.play', $quiz->slug));
    }

    public function test_the_result_survives_the_quiz_being_archived_but_offers_no_replay(): void
    {
        $quiz = $this->publishedQuiz(2);
        $state = $this->play('child', $quiz);
        $quiz->update(['status' => QuizStatus::Archived]);

        $this->resultPage('child', $state)
            ->assertOk()
            ->assertSee(__('public.result.review'))
            ->assertDontSee(__('public.result.replay'));
    }

    public function test_replay_is_withheld_once_the_attempts_are_used(): void
    {
        $quiz = $this->publishedQuiz(2, ['attempts_allowed' => 1]);
        $state = $this->play('child', $quiz);

        $this->resultPage('child', $state)
            ->assertOk()
            ->assertDontSee(__('public.result.replay'))
            ->assertSee(__('public.result.attempts_none'));
    }

    public function test_the_review_marks_the_right_answer_and_the_childs_choice(): void
    {
        $quiz = $this->publishedQuiz(1);
        $state = $this->play('child', $quiz, wrong: [0]);

        $this->resultPage('child', $state)
            ->assertSee('data-right="true"', false)
            ->assertSee('data-mine="true"', false)
            ->assertSee(__('public.result.yours'))
            ->assertSee(__('public.result.right'));
    }
}
