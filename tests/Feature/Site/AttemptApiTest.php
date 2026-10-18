<?php

namespace Tests\Feature\Site;

use App\Enums\FeedbackMode;
use App\Models\Quiz;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Testing\TestResponse;
use Tests\Concerns\ActsAsVisitors;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class AttemptApiTest extends TestCase
{
    use ActsAsVisitors, CreatesQuizzes, RefreshDatabase;

    private function start(string $visitor, Quiz $quiz, array $body = []): TestResponse
    {
        return $this->asVisitor($visitor, fn () => $this->postJson(route('attempts.start', $quiz->slug), $body));
    }

    private function answer(string $visitor, string $url, int $questionId, int $optionId): TestResponse
    {
        return $this->asVisitor($visitor, fn () => $this->postJson($url, ['question_id' => $questionId, 'option_id' => $optionId]));
    }

    public function test_starting_returns_questions_without_any_hint_of_the_answer(): void
    {
        $quiz = $this->publishedQuiz(3);

        $response = $this->start('child', $quiz)->assertOk();
        $json = $response->json();

        $this->assertCount(3, $json['questions']);
        $this->assertFalse($json['finished']);
        $this->assertSame('instant', $json['feedback_mode']);

        foreach ($json['questions'] as $question) {
            $this->assertSame(['id', 'type', 'body', 'points', 'options'], array_keys($question));

            foreach ($question['options'] as $option) {
                $this->assertSame(['id', 'body'], array_keys($option));
            }
        }

        $raw = $response->getContent();
        $this->assertStringNotContainsString('is_correct', $raw);
        $this->assertStringNotContainsString('explanation', $raw);
        // No answers yet must be an empty object, not an empty list.
        $this->assertStringContainsString('"answers":{}', $raw);
    }

    public function test_starting_again_resumes_unless_a_restart_is_requested(): void
    {
        $quiz = $this->publishedQuiz(2);

        $first = $this->start('child', $quiz)->json('attempt');
        $again = $this->start('child', $quiz)->json('attempt');
        $fresh = $this->start('child', $quiz, ['restart' => true])->json('attempt');
        $other = $this->start('sibling', $quiz)->json('attempt');

        $this->assertSame($first, $again);
        $this->assertNotSame($first, $fresh);
        $this->assertNotSame($fresh, $other);
    }

    public function test_a_visitor_who_used_every_attempt_is_told_so(): void
    {
        $quiz = $this->publishedQuiz(1, ['attempts_allowed' => 1]);
        $state = $this->start('child', $quiz)->json();
        $question = $state['questions'][0];
        $this->answer('child', $state['urls']['answer'], $question['id'], $question['options'][0]['id'])->assertOk();

        $this->start('child', $quiz, ['restart' => true])
            ->assertForbidden()
            ->assertJson(['code' => 'exhausted']);
    }

    public function test_an_instant_answer_reveals_the_result_and_the_explanation(): void
    {
        $quiz = $this->publishedQuiz(2);
        $state = $this->start('child', $quiz)->json();
        $question = $state['questions'][0];
        $right = $this->correctOptionId($question['id']);
        $wrong = $this->wrongOptionId($question['id']);

        $this->answer('child', $state['urls']['answer'], $question['id'], $wrong)
            ->assertOk()
            ->assertJson([
                'recorded' => true,
                'correct' => false,
                'correct_option_id' => $right,
                'score' => 0,
                'answered' => 1,
                'total' => 2,
                'finished' => false,
            ])
            ->assertJsonStructure(['explanation']);
    }

    public function test_the_last_answer_finishes_the_attempt_and_points_to_the_result(): void
    {
        $quiz = $this->publishedQuiz(2);
        $state = $this->start('child', $quiz)->json();

        foreach ($state['questions'] as $question) {
            $last = $this->answer('child', $state['urls']['answer'], $question['id'], $this->correctOptionId($question['id']))->assertOk();
        }

        $last->assertJson(['finished' => true, 'score' => 2, 'result_url' => $state['urls']['result']]);
    }

    public function test_in_end_mode_nothing_about_correctness_is_sent_at_any_point(): void
    {
        $quiz = $this->publishedQuiz(2, ['feedback_mode' => FeedbackMode::End]);
        $state = $this->start('child', $quiz)->json();
        $this->assertSame('end', $state['feedback_mode']);
        [$first, $second] = $state['questions'];

        $one = $this->answer('child', $state['urls']['answer'], $first['id'], $this->correctOptionId($first['id']))->assertOk();
        $one->assertJson(['recorded' => true, 'finished' => false]);

        $two = $this->answer('child', $state['urls']['answer'], $second['id'], $this->wrongOptionId($second['id']))->assertOk();
        $two->assertJson(['finished' => true]);

        foreach ([$one, $two] as $response) {
            $this->assertEqualsCanonicalizing(['recorded', 'answered', 'total', 'finished', 'result_url'], array_keys($response->json()));
        }

        // Resuming mid-quiz must not leak it either.
        $other = $this->publishedQuiz(2, ['feedback_mode' => FeedbackMode::End]);
        $s = $this->start('resumer', $other)->json();
        $this->answer('resumer', $s['urls']['answer'], $s['questions'][0]['id'], $this->correctOptionId($s['questions'][0]['id']));
        $resumed = $this->start('resumer', $other)->json();
        $this->assertNull($resumed['score']);
        $this->assertSame(['option_id' => $this->correctOptionId($s['questions'][0]['id'])], $resumed['answers'][$s['questions'][0]['id']]);
    }

    public function test_resuming_in_instant_mode_restores_progress(): void
    {
        $quiz = $this->publishedQuiz(3);
        $state = $this->start('child', $quiz)->json();
        $first = $state['questions'][0];
        $this->answer('child', $state['urls']['answer'], $first['id'], $this->wrongOptionId($first['id']));

        $resumed = $this->start('child', $quiz)->json();

        $this->assertSame($this->correctOptionId($first['id']), $resumed['answers'][$first['id']]['correct_option_id']);
        $this->assertFalse($resumed['answers'][$first['id']]['correct']);
        $this->assertSame(0, $resumed['score']);
    }

    public function test_repeating_the_same_answer_is_safe_and_changing_it_is_refused(): void
    {
        $quiz = $this->publishedQuiz(2);
        $state = $this->start('child', $quiz)->json();
        $question = $state['questions'][0];
        $wrong = $this->wrongOptionId($question['id']);

        $first = $this->answer('child', $state['urls']['answer'], $question['id'], $wrong)->assertOk()->json();
        $retry = $this->answer('child', $state['urls']['answer'], $question['id'], $wrong)->assertOk()->json();

        $this->assertSame($first, $retry);

        $this->answer('child', $state['urls']['answer'], $question['id'], $this->correctOptionId($question['id']))
            ->assertStatus(409)
            ->assertJson(['code' => 'answered']);
    }

    public function test_another_visitor_cannot_answer_someone_elses_attempt(): void
    {
        $quiz = $this->publishedQuiz(2);
        $state = $this->start('child', $quiz)->json();
        $question = $state['questions'][0];

        $this->answer('stranger', $state['urls']['answer'], $question['id'], $this->correctOptionId($question['id']))->assertNotFound();
        $this->postJson('/percubaan/00000000-0000-0000-0000-000000000000/jawapan', ['question_id' => 1, 'option_id' => 1])->assertNotFound();

        // The child's own attempt is untouched.
        $this->assertDatabaseCount('attempt_answers', 0);
    }

    public function test_answers_are_validated(): void
    {
        $quiz = $this->publishedQuiz(2);
        $other = $this->publishedQuiz(1);
        $state = $this->start('child', $quiz)->json();
        $question = $state['questions'][0];
        $foreign = $other->questions()->first();

        $this->asVisitor('child', fn () => $this->postJson($state['urls']['answer'], []))->assertUnprocessable();
        $this->asVisitor('child', fn () => $this->postJson($state['urls']['answer'], ['question_id' => 'x', 'option_id' => 'y']))->assertUnprocessable();

        // A real option, but not one of this question's: refused, not scored.
        $this->answer('child', $state['urls']['answer'], $question['id'], $this->correctOptionId($foreign->id))
            ->assertStatus(422)
            ->assertJson(['code' => 'invalid']);
        $this->answer('child', $state['urls']['answer'], $foreign->id, $this->correctOptionId($foreign->id))->assertStatus(422);
    }

    public function test_starting_is_rate_limited_per_address(): void
    {
        $quiz = $this->publishedQuiz(1);

        for ($i = 0; $i < 30; $i++) {
            $this->postJson(route('attempts.start', $quiz->slug))->assertOk();
        }

        $this->postJson(route('attempts.start', $quiz->slug))->assertStatus(429);
    }
}
