<?php

namespace Tests\Feature\Admin;

use App\Models\Attempt;
use App\Models\Question;
use App\Models\Quiz;
use App\Models\User;
use App\Services\Stats\QuizStatistics;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Str;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class QuizStatisticsTest extends TestCase
{
    use CreatesQuizzes, RefreshDatabase;

    private function stats(): QuizStatistics
    {
        return app(QuizStatistics::class);
    }

    /** One finished attempt with the given result. */
    private function attempt(Quiz $quiz, int $score, int $max, ?\DateTimeInterface $finishedAt = null, ?\DateTimeInterface $startedAt = null): Attempt
    {
        return $quiz->attempts()->create([
            'uuid' => (string) Str::uuid(),
            'session_hash' => str_repeat('a', 64),
            'layout' => ['questions' => [], 'options' => []],
            'started_at' => $startedAt ?? now()->subMinutes(10),
            'completed_at' => $finishedAt,
            'score' => $score,
            'max_score' => $max,
        ]);
    }

    /** A fresh attempt that answered one question (each attempt may answer a question only once). */
    private function answer(Quiz $quiz, Question $question, bool $correct): void
    {
        $attempt = $this->attempt($quiz, 0, 0);
        $option = $question->options()->where('is_correct', $correct)->firstOrFail();

        $attempt->answers()->create([
            'question_id' => $question->id, 'option_id' => $option->id,
            'is_correct' => $correct, 'points_awarded' => $correct ? 1 : 0, 'answered_at' => now(),
        ]);
    }

    public function test_the_overview_counts_only_the_last_seven_days_and_only_finished_attempts_for_the_average(): void
    {
        $quiz = $this->publishedQuiz(1);
        Quiz::factory()->create();   // a draft

        $this->attempt($quiz, 3, 4, now()->subDay());                                         // 75 %
        $this->attempt($quiz, 1, 4, now()->subDays(2));                                       // 25 %
        $this->attempt($quiz, 4, 4, now()->subDays(20), now()->subDays(20));                  // too old
        $this->attempt($quiz, 0, 4, null);                                                    // started, never finished
        $this->attempt($quiz, 0, 0, now()->subHour());                                        // nothing to score: left out of the average

        $overview = $this->stats()->overview();

        $this->assertSame(1, $overview['published']);
        $this->assertSame(1, $overview['drafts']);
        $this->assertSame(4, $overview['started_week']);     // everything except the 20 day old one
        $this->assertSame(3, $overview['completed_week']);
        $this->assertEquals(50.0, $overview['average_percent']);
    }

    public function test_with_no_attempts_the_average_is_unknown_not_zero(): void
    {
        $this->assertNull($this->stats()->overview()['average_percent']);
        $this->assertNull($this->stats()->forQuiz($this->publishedQuiz(1))['completion_percent']);
    }

    public function test_attention_flags_published_quizzes_that_can_no_longer_be_played_and_drafts_that_are_ready(): void
    {
        $healthy = $this->publishedQuiz(2, ['title' => 'Sihat']);
        $broken = $this->publishedQuiz(2, ['title' => 'Rosak']);
        $broken->questions()->get()->each->delete();                                   // every question removed after publishing

        $ready = Quiz::factory()->create(['title' => 'Siap Draf']);
        Question::factory()->for($ready)->withOptions(3, 0)->create(['position' => 1]);
        Quiz::factory()->create(['title' => 'Draf Kosong']);                           // nothing to publish yet

        $attention = $this->stats()->attention();

        $this->assertSame(['Rosak'], $attention['broken']->map(fn ($row) => $row['quiz']->title)->all());
        $this->assertNotEmpty($attention['broken'][0]['problems']);
        $this->assertSame(['Siap Draf'], $attention['ready']->pluck('title')->all());
        $this->assertNotContains($healthy->id, $attention['broken']->map(fn ($row) => $row['quiz']->id)->all());
    }

    public function test_the_hardest_questions_need_enough_answers_and_are_ranked_from_the_lowest_score(): void
    {
        $quiz = $this->publishedQuiz(3);
        [$easy, $hard, $thin] = $quiz->questions()->with('options')->get()->all();

        foreach ([true, true, true, true, false] as $correct) {    // 80 %
            $this->answer($quiz, $easy, $correct);
        }
        foreach ([false, false, false, true, false] as $correct) { // 20 %
            $this->answer($quiz, $hard, $correct);
        }
        foreach ([false, false] as $correct) {                      // 0 %, but only two answers: noise
            $this->answer($quiz, $thin, $correct);
        }

        $rows = $this->stats()->hardestQuestions();

        $this->assertSame([$hard->id, $easy->id], $rows->pluck('id')->all());
        $this->assertSame([20.0, 80.0], $rows->pluck('percent')->all());
        $this->assertSame([5, 5], $rows->pluck('answers')->all());
    }

    public function test_deleted_questions_drop_out_of_the_hardest_list(): void
    {
        $quiz = $this->publishedQuiz(1);
        $question = $quiz->questions()->with('options')->firstOrFail();

        foreach (range(1, 5) as $i) {
            $this->answer($quiz, $question, false);
        }
        $this->assertCount(1, $this->stats()->hardestQuestions());

        $question->delete();

        $this->assertCount(0, $this->stats()->hardestQuestions());
    }

    public function test_quiz_statistics_report_completion_average_and_a_per_question_breakdown(): void
    {
        $quiz = $this->publishedQuiz(2);
        [$first, $second] = $quiz->questions()->with('options')->get()->all();

        $this->attempt($quiz, 2, 2, now());
        $this->attempt($quiz, 1, 2, now());
        $this->attempt($quiz, 0, 0, null);   // wandered off
        $this->attempt($quiz, 0, 0, null);

        foreach ([true, true, true, false, true] as $correct) {
            $this->answer($quiz, $first, $correct);
        }
        $this->answer($quiz, $second, false);

        $report = $this->stats()->forQuiz($quiz);

        // The answer() helper opens an attempt each time, so those count as started too.
        $this->assertSame(4 + 6, $report['started']);
        $this->assertSame(2, $report['completed']);
        $this->assertEquals(20.0, $report['completion_percent']);
        $this->assertEquals(75.0, $report['average_percent']);

        $this->assertSame(1, $report['questions'][0]['number']);
        $this->assertSame(5, $report['questions'][0]['answers']);
        $this->assertEquals(80.0, $report['questions'][0]['percent']);
        $this->assertTrue($report['questions'][0]['enough']);

        $this->assertSame(1, $report['questions'][1]['answers']);
        $this->assertFalse($report['questions'][1]['enough'], 'one answer is not enough to judge a question');
    }

    public function test_a_question_nobody_has_answered_has_no_percentage(): void
    {
        $report = $this->stats()->forQuiz($this->publishedQuiz(1));

        $this->assertNull($report['questions'][0]['percent']);
        $this->assertSame(0, $report['questions'][0]['answers']);
    }

    public function test_the_dashboard_and_statistics_pages_render_with_real_data(): void
    {
        $this->actingAs(User::factory()->admin()->create());

        $quiz = $this->publishedQuiz(1);
        $question = $quiz->questions()->with('options')->firstOrFail();
        $this->attempt($quiz, 1, 1, now());
        foreach (range(1, 5) as $i) {
            $this->answer($quiz, $question, $i === 1);
        }

        $this->get(route('admin.dashboard'))->assertOk()->assertSee($quiz->title);
        $this->get(route('admin.quizzes.stats', $quiz))->assertOk()->assertSee($question->body);
    }
}
