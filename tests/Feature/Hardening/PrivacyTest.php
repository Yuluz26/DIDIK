<?php

namespace Tests\Feature\Hardening;

use App\Models\Attempt;
use App\Models\Quiz;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class PrivacyTest extends TestCase
{
    use CreatesQuizzes, RefreshDatabase;

    public function test_sessions_are_stored_without_the_visitors_address_or_browser(): void
    {
        config(['session.driver' => 'database']);

        $this->withServerVariables(['REMOTE_ADDR' => '203.0.113.9'])
            ->withHeaders(['User-Agent' => 'SomeBrowser/1.0'])
            ->get('/')
            ->assertOk();

        $row = DB::table('sessions')->first();

        $this->assertNotNull($row, 'the session was stored');
        $this->assertNull($row->ip_address);
        $this->assertNull($row->user_agent);
        $this->assertStringNotContainsString('203.0.113.9', json_encode($row));
    }

    public function test_the_site_sets_one_cookie_and_it_is_the_session(): void
    {
        $response = $this->get('/')->assertOk();

        $names = collect($response->headers->getCookies())->map->getName()->all();

        $this->assertSame([config('session.cookie')], $names);
        $response->assertCookieMissing('XSRF-TOKEN');
    }

    public function test_the_notice_states_the_real_retention_and_cookie_facts(): void
    {
        config(['didik.retention_days' => 45, 'session.lifetime' => 480, 'didik.contact_email' => 'ibu.bapa@didik.test']);

        $page = $this->get(route('pages.privacy'))->assertOk();

        $page->assertSee('45 hari');
        $page->assertSee('8 jam');
        $page->assertSee('ibu.bapa@didik.test');
        // English summary for readers who need it.
        $page->assertSee('In English');
        $page->assertSee('45 days', false);
        $page->assertDontSee('apa-apa maklumat peribadi');
    }

    private function attemptAged(Quiz $quiz, int $days, bool $finished = true): Attempt
    {
        return $quiz->attempts()->create([
            'uuid' => (string) Str::uuid(), 'session_hash' => str_repeat('a', 64),
            'layout' => ['questions' => [], 'options' => []],
            'started_at' => now()->subDays($days),
            'completed_at' => $finished ? now()->subDays($days) : null,
        ]);
    }

    public function test_pruning_removes_old_attempts_with_their_answers_and_keeps_recent_ones(): void
    {
        config(['didik.retention_days' => 30]);
        $quiz = $this->publishedQuiz(1);
        $question = $quiz->questions()->with('options')->first();

        $old = $this->attemptAged($quiz, 31);
        $abandoned = $this->attemptAged($quiz, 40, finished: false);
        $recent = $this->attemptAged($quiz, 29);
        $old->answers()->create(['question_id' => $question->id, 'option_id' => $question->options->first()->id, 'is_correct' => true, 'points_awarded' => 1, 'answered_at' => now()]);

        $this->artisan('didik:prune')->assertSuccessful();

        $this->assertModelMissing($old);
        $this->assertModelMissing($abandoned);
        $this->assertModelExists($recent);
        $this->assertDatabaseCount('attempt_answers', 0);
    }

    public function test_a_dry_run_deletes_nothing_and_the_days_option_overrides_the_setting(): void
    {
        config(['didik.retention_days' => 365]);
        $quiz = $this->publishedQuiz(1);
        $old = $this->attemptAged($quiz, 10);

        $this->artisan('didik:prune', ['--days' => 5, '--dry-run' => true])
            ->expectsOutputToContain('akan dipadam: 1')
            ->assertSuccessful();
        $this->assertModelExists($old);

        $this->artisan('didik:prune', ['--days' => 5])->assertSuccessful();
        $this->assertModelMissing($old);
    }

    public function test_pruning_refuses_a_retention_of_less_than_a_day(): void
    {
        config(['didik.retention_days' => 0]);

        $this->artisan('didik:prune')->assertFailed();
    }

    public function test_pruning_clears_expired_sessions_only(): void
    {
        config(['session.driver' => 'database', 'session.lifetime' => 120]);

        DB::table('sessions')->insert([
            ['id' => 'expired', 'payload' => 'x', 'last_activity' => now()->subMinutes(121)->getTimestamp()],
            ['id' => 'live', 'payload' => 'x', 'last_activity' => now()->subMinutes(5)->getTimestamp()],
        ]);

        $this->artisan('didik:prune')->assertSuccessful();

        $this->assertSame(['live'], DB::table('sessions')->pluck('id')->all());
    }

    public function test_the_prune_command_is_scheduled_daily(): void
    {
        $this->artisan('schedule:list')->expectsOutputToContain('didik:prune')->assertSuccessful();
    }
}
