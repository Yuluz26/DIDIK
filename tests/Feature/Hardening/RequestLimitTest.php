<?php

namespace Tests\Feature\Hardening;

use App\Models\Attempt;
use App\Support\ClientKey;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Str;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\Concerns\ActsAsVisitors;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class RequestLimitTest extends TestCase
{
    use ActsAsVisitors, CreatesQuizzes, RefreshDatabase;

    /** @return array<string, array{string, string}> */
    public static function addresses(): array
    {
        return [
            'ipv4 is itself' => ['203.0.113.9', '203.0.113.9'],
            'ipv4 written as ipv6' => ['::ffff:203.0.113.9', '203.0.113.9'],
            'ipv6 is grouped by its /64' => ['2001:db8:1:2:aaaa:bbbb:cccc:dddd', '2001:db8:1:2::/64'],
            'another host in the same /64' => ['2001:db8:1:2:1:2:3:4', '2001:db8:1:2::/64'],
            'a different /64' => ['2001:db8:1:3::1', '2001:db8:1:3::/64'],
        ];
    }

    #[DataProvider('addresses')]
    public function test_clients_are_counted_by_address_with_ipv6_grouped_by_block(string $ip, string $key): void
    {
        $request = Request::create('/', server: ['REMOTE_ADDR' => $ip]);

        $this->assertSame($key, ClientKey::address($request));
    }

    public function test_one_visitor_hits_their_own_limit_without_blocking_another_behind_the_same_address(): void
    {
        // Two children on one school or home connection.
        $answer = fn (string $child) => $this->asVisitor($child, fn () => $this->postJson(route('attempts.answer', Str::uuid()), ['question_id' => 1, 'option_id' => 1]));

        // Unknown attempt: 404 once past the limiter. 90 per visitor per minute.
        foreach (range(1, 90) as $i) {
            $this->assertSame(404, $answer('first')->status(), "request {$i}");
        }

        $this->assertSame(429, $answer('first')->status());
        $this->assertSame(404, $answer('second')->status(), 'a second child on the same address is not locked out');
    }

    public function test_starting_attempts_has_its_own_per_visitor_ceiling(): void
    {
        $quiz = $this->publishedQuiz(1);
        $start = fn (string $child) => $this->asVisitor($child, fn () => $this->postJson(route('attempts.start', $quiz->slug), ['restart' => true]));

        foreach (range(1, 20) as $i) {
            $start('eager')->assertOk();
        }

        $start('eager')->assertStatus(429);
        $start('calm')->assertOk();
    }

    public function test_restarting_replaces_the_unfinished_attempt_instead_of_piling_up(): void
    {
        $quiz = $this->publishedQuiz(2);
        $uuids = [];

        foreach (range(1, 5) as $i) {
            $uuids[] = $this->asVisitor('child', fn () => $this->postJson(route('attempts.start', $quiz->slug), ['restart' => true]))->json('urls.result');
        }

        $this->assertSame(1, Attempt::where('quiz_id', $quiz->id)->count());
        $this->assertCount(5, array_unique($uuids));
    }

    public function test_sign_in_has_a_ceiling_per_address_whatever_the_email(): void
    {
        RateLimiter::clear('x');

        foreach (range(1, 20) as $i) {
            $status = $this->post(route('admin.login.store'), ['email' => "nobody{$i}@didik.test", 'password' => 'salah'])->status();
            $this->assertContains($status, [302, 422], "attempt {$i}");
        }

        $this->post(route('admin.login.store'), ['email' => 'another@didik.test', 'password' => 'salah'])->assertStatus(429);
    }

    public function test_every_page_has_a_generous_ceiling_per_address(): void
    {
        foreach (range(1, 600) as $i) {
            $this->assertSame(200, $this->get(route('pages.about'))->status(), "request {$i}");
        }

        $this->get(route('pages.about'))->assertStatus(429);
    }
}
