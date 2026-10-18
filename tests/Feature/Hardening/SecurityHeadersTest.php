<?php

namespace Tests\Feature\Hardening;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Vite;
use Tests\Concerns\ActsAsVisitors;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class SecurityHeadersTest extends TestCase
{
    use ActsAsVisitors, CreatesQuizzes, RefreshDatabase;

    /** @return array<string, string> directive name => value */
    private function policy(string $header): array
    {
        $directives = [];

        foreach (explode(';', $header) as $part) {
            [$name, $value] = array_pad(explode(' ', trim($part), 2), 2, '');
            $directives[$name] = $value;
        }

        return $directives;
    }

    public function test_every_kind_of_response_carries_the_basic_protections(): void
    {
        $quiz = $this->publishedQuiz(1);

        $responses = [
            'page' => $this->get('/'),
            'login' => $this->get(route('admin.login')),
            'not found' => $this->get('/tiada-halaman'),
            'json' => $this->postJson(route('live.answer'), ['question_id' => 1]),
            'player' => $this->get(route('quizzes.play', $quiz->slug)),
        ];

        foreach ($responses as $name => $response) {
            $response->assertHeader('X-Content-Type-Options', 'nosniff');
            $response->assertHeader('X-Frame-Options', 'DENY');
            $response->assertHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
            $response->assertHeader('Cross-Origin-Opener-Policy', 'same-origin');
            $this->assertStringContainsString('camera=()', $response->headers->get('Permissions-Policy'), $name);
            $this->assertTrue($response->headers->has('Content-Security-Policy'), $name);
        }
    }

    public function test_the_policy_allows_scripts_from_this_site_only(): void
    {
        $policy = $this->policy($this->get('/')->headers->get('Content-Security-Policy'));

        $this->assertSame("'self'", $policy['script-src']);
        $this->assertSame("'self'", $policy['default-src']);
        $this->assertSame("'none'", $policy['frame-ancestors']);
        $this->assertSame("'none'", $policy['object-src']);
        $this->assertSame("'self'", $policy['base-uri']);
        $this->assertSame("'self'", $policy['form-action']);
        $this->assertSame("'self'", $policy['connect-src']);

        // No inline script, no eval, no other origin for scripts or styles.
        $this->assertStringNotContainsString('unsafe-eval', implode(' ', $policy));
        $this->assertStringNotContainsString('unsafe-inline', $policy['script-src']);
        $this->assertSame("'self'", $policy['style-src']);
        $this->assertSame("'unsafe-inline'", $policy['style-src-attr']);
    }

    public function test_pages_contain_no_inline_script_for_the_policy_to_block(): void
    {
        $this->publishedQuiz(2);
        $this->actingAs(User::factory()->admin()->create());

        foreach ([route('home'), route('quizzes.index'), route('admin.dashboard'), route('admin.quizzes.create')] as $url) {
            $html = $this->get($url)->assertOk()->getContent();

            preg_match_all('/<script\b([^>]*)>/i', $html, $scripts);

            foreach ($scripts[1] as $attributes) {
                $this->assertMatchesRegularExpression('/\bsrc=/', $attributes, "{$url} has an inline <script>");
            }

            $this->assertDoesNotMatchRegularExpression('/\son[a-z]+\s*=\s*["\']/i', $html, "{$url} has an inline event handler");
            $this->assertDoesNotMatchRegularExpression('/javascript:/i', $html, "{$url} has a javascript: URL");
        }
    }

    public function test_strict_transport_security_is_only_sent_over_https(): void
    {
        $this->get('http://didik.test/')->assertHeaderMissing('Strict-Transport-Security');

        $secure = $this->get('https://didik.test/');
        $secure->assertHeader('Strict-Transport-Security', 'max-age=15552000');
        $this->assertArrayHasKey('upgrade-insecure-requests', $this->policy($secure->headers->get('Content-Security-Policy')));

        config(['didik.hsts_seconds' => 0]);
        $this->get('https://didik.test/')->assertHeaderMissing('Strict-Transport-Security');
    }

    public function test_the_policy_can_be_switched_off_and_is_skipped_while_the_vite_dev_server_runs(): void
    {
        config(['didik.csp' => false]);
        $this->get('/')->assertHeaderMissing('Content-Security-Policy')->assertHeader('X-Frame-Options', 'DENY');

        config(['didik.csp' => true]);
        $hot = storage_path('framework/testing-vite-hot');
        file_put_contents($hot, 'http://127.0.0.1:5173');
        Vite::useHotFile($hot);

        try {
            $this->get('/')->assertHeaderMissing('Content-Security-Policy');
        } finally {
            @unlink($hot);
            Vite::useHotFile(public_path('hot'));
        }
    }

    public function test_assets_served_from_a_cdn_are_allowed_but_scripts_stay_off_every_other_origin(): void
    {
        config(['app.asset_url' => 'https://cdn.didik.test/assets']);

        $policy = $this->policy($this->get('/')->headers->get('Content-Security-Policy'));

        $this->assertSame("'self' https://cdn.didik.test", $policy['script-src']);
        $this->assertSame("'self' https://cdn.didik.test data:", $policy['img-src']);
        $this->assertSame("'self'", $policy['connect-src']);
    }

    public function test_admin_and_result_pages_are_never_cached(): void
    {
        $this->get(route('admin.login'))->assertHeader('Cache-Control');
        $this->actingAs(User::factory()->admin()->create());

        $this->assertStringContainsString('no-store', $this->get(route('admin.dashboard'))->headers->get('Cache-Control'));
        $this->assertStringNotContainsString('no-store', (string) $this->get(route('home'))->headers->get('Cache-Control'));
    }
}
