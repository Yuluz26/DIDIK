<?php

namespace Tests\Feature\Site;

use App\Models\Quiz;
use App\Services\QuizEngine\AttemptService;
use App\Support\SessionFingerprint;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\Request;
use Tests\Concerns\ActsAsVisitors;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class QuizAccessTest extends TestCase
{
    use ActsAsVisitors, CreatesQuizzes, RefreshDatabase;

    public function test_an_available_quiz_can_be_opened_and_played(): void
    {
        $quiz = $this->publishedQuiz(2);

        $this->get(route('quizzes.show', $quiz->slug))
            ->assertOk()
            ->assertSee($quiz->title)
            ->assertSee(route('quizzes.play', $quiz->slug), false);

        $this->get(route('quizzes.play', $quiz->slug))
            ->assertOk()
            ->assertSee('x-data="quizPlayer(', false);
    }

    public function test_quizzes_the_public_may_not_see_are_a_plain_404(): void
    {
        $unavailable = [
            Quiz::factory()->create(),
            Quiz::factory()->archived()->create(),
            $this->publishedQuiz(1, ['available_from' => now()->addDay()]),
            $this->publishedQuiz(1, ['available_until' => now()->subDay()]),
        ];

        foreach ($unavailable as $quiz) {
            foreach (['quizzes.show', 'quizzes.play'] as $route) {
                $this->get(route($route, $quiz->slug))->assertNotFound();
            }

            $this->postJson(route('attempts.start', $quiz->slug))->assertNotFound();
        }

        $this->get('/kuiz/tiada-kuiz-ini')->assertNotFound();
    }

    public function test_every_game_concept_renders_its_own_player(): void
    {
        $markers = [
            'qa' => 'class="dots"',
            'stars' => 'class="slots"',
            'quest' => 'path__cells',
        ];

        foreach ($markers as $key => $marker) {
            $quiz = $this->publishedQuiz(2, ['game_concept' => $key]);

            $this->get(route('quizzes.play', $quiz->slug))
                ->assertOk()
                ->assertSee("concept-{$key}", false)
                ->assertSee($marker, false);
        }
    }

    public function test_the_qa_concept_can_show_a_bar_instead_of_dots(): void
    {
        $quiz = $this->publishedQuiz(2, ['game_settings' => ['progress' => 'bar']]);

        $this->get(route('quizzes.play', $quiz->slug))->assertOk()->assertSee('bar__fill', false)->assertDontSee('class="dots"', false);
    }

    public function test_an_unknown_game_concept_falls_back_to_the_default_player(): void
    {
        $quiz = $this->publishedQuiz(2, ['game_concept' => 'removed-concept']);

        $this->get(route('quizzes.play', $quiz->slug))->assertOk()->assertSee('class="dots"', false);
        $this->get(route('quizzes.show', $quiz->slug))->assertOk();
    }

    public function test_the_player_page_is_not_indexed_and_has_no_site_chrome(): void
    {
        $quiz = $this->publishedQuiz(1);

        $this->get(route('quizzes.play', $quiz->slug))
            ->assertSee('<meta name="robots" content="noindex">', false)
            ->assertDontSee('site-header', false);
    }

    public function test_the_introduction_reflects_attempts_and_resuming(): void
    {
        $quiz = $this->publishedQuiz(1, ['attempts_allowed' => 1]);

        $this->asVisitor('child', fn () => $this->get(route('quizzes.show', $quiz->slug)))
            ->assertSee(__('public.quiz.attempts_left', ['count' => 1]));

        // Start it (an unfinished attempt): the page offers to continue it.
        $this->asVisitor('child', fn () => $this->postJson(route('attempts.start', $quiz->slug)))->assertOk();
        $this->asVisitor('child', fn () => $this->get(route('quizzes.show', $quiz->slug)))
            ->assertSee(__('public.quiz.resume'));
    }

    public function test_when_every_attempt_is_used_the_introduction_says_so_and_play_redirects(): void
    {
        $quiz = $this->publishedQuiz(1, ['attempts_allowed' => 1]);
        $this->finishAs('child', $quiz);

        $this->asVisitor('child', fn () => $this->get(route('quizzes.show', $quiz->slug)))
            ->assertOk()
            ->assertSee(__('public.quiz.exhausted'))
            ->assertSee(__('public.quiz.last_result'));

        $this->asVisitor('child', fn () => $this->get(route('quizzes.play', $quiz->slug)))
            ->assertRedirect(route('quizzes.show', $quiz->slug));

        // Someone else still gets their own attempt.
        $this->asVisitor('sibling', fn () => $this->get(route('quizzes.play', $quiz->slug)))->assertOk();
    }

    /** Finish a one-question quiz as a named visitor. */
    private function finishAs(string $visitor, Quiz $quiz): void
    {
        $state = $this->asVisitor($visitor, fn () => $this->postJson(route('attempts.start', $quiz->slug)))->json();
        $question = $state['questions'][0];

        $this->asVisitor($visitor, fn () => $this->postJson($state['urls']['answer'], [
            'question_id' => $question['id'],
            'option_id' => $question['options'][0]['id'],
        ]))->assertOk();
    }

    public function test_the_fingerprint_is_a_keyed_hash_and_never_the_session_id(): void
    {
        $request = Request::create('/');
        $request->setLaravelSession(app('session.store'));

        $hash = SessionFingerprint::for($request);

        $this->assertSame(64, strlen($hash));
        $this->assertStringNotContainsString($request->session()->getId(), $hash);
        $this->assertTrue(SessionFingerprint::matches($hash, $request));
        $this->assertFalse(SessionFingerprint::matches(str_repeat('0', 64), $request));
        $this->assertInstanceOf(AttemptService::class, app(AttemptService::class));
    }
}
