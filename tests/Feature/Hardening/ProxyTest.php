<?php

namespace Tests\Feature\Hardening;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use Tests\TestCase;

class ProxyTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        Route::middleware('web')->get('/__whoami', fn (Request $request) => response()->json([
            'ip' => $request->ip(),
            'secure' => $request->isSecure(),
            'url' => url('/x'),
        ]));
    }

    private function viaProxy(): array
    {
        return $this->withServerVariables(['REMOTE_ADDR' => '10.0.0.7'])
            ->withHeaders(['X-Forwarded-For' => '203.0.113.9', 'X-Forwarded-Proto' => 'https', 'X-Forwarded-Host' => 'didik.test'])
            ->getJson('/__whoami')
            ->json();
    }

    public function test_forwarded_headers_are_ignored_unless_a_proxy_is_trusted(): void
    {
        $seen = $this->viaProxy();

        // Anyone can send these headers, so by default they mean nothing.
        $this->assertSame('10.0.0.7', $seen['ip']);
        $this->assertFalse($seen['secure']);
        $this->assertStringStartsWith('http://', $seen['url']);
    }

    public function test_a_trusted_proxy_gives_the_visitors_address_and_the_https_scheme(): void
    {
        config(['trustedproxy.proxies' => ['10.0.0.0/8']]);

        $seen = $this->viaProxy();

        $this->assertSame('203.0.113.9', $seen['ip']);
        $this->assertTrue($seen['secure']);
        $this->assertSame('https://didik.test/x', $seen['url']);
    }

    public function test_a_connection_from_outside_the_trusted_range_cannot_forge_them(): void
    {
        config(['trustedproxy.proxies' => ['10.0.0.0/8']]);

        $seen = $this->withServerVariables(['REMOTE_ADDR' => '198.51.100.20'])
            ->withHeaders(['X-Forwarded-For' => '203.0.113.9', 'X-Forwarded-Proto' => 'https'])
            ->getJson('/__whoami')
            ->json();

        $this->assertSame('198.51.100.20', $seen['ip']);
        $this->assertFalse($seen['secure']);
    }

    public function test_the_environment_setting_is_read_as_a_list_or_a_wildcard(): void
    {
        $read = function (string $value): mixed {
            putenv("TRUSTED_PROXIES={$value}");
            $_ENV['TRUSTED_PROXIES'] = $value;

            return (require base_path('config/trustedproxy.php'))['proxies'];
        };

        try {
            $this->assertSame('*', $read('*'));
            $this->assertSame(['10.0.0.1', '172.16.0.0/12'], $read(' 10.0.0.1 , 172.16.0.0/12 '));
            $this->assertNull($read(''));
        } finally {
            putenv('TRUSTED_PROXIES');
            unset($_ENV['TRUSTED_PROXIES']);
        }
    }
}
