<?php

namespace Tests\Unit;

use App\Rules\QuizizzUrl;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

class QuizizzUrlRuleTest extends TestCase
{
    private function passes(mixed $value): bool
    {
        $failed = false;

        (new QuizizzUrl)->validate('url', $value, function () use (&$failed) {
            $failed = true;
        });

        return ! $failed;
    }

    /** @return array<string, array{string}> */
    public static function acceptable(): array
    {
        return [
            'activity page' => ['https://quizizz.com/admin/quiz/5f2a9c0b1d3e4a001b2c3d4e'],
            'join code with query' => ['https://quizizz.com/join?gc=12345678'],
            'www' => ['https://www.quizizz.com/library'],
            'other subdomain' => ['https://app.quizizz.com/x'],
            'bare host' => ['https://quizizz.com'],
            'its new name' => ['https://wayground.com/admin/quiz/5f2a9c0b1d3e4a001b2c3d4e'],
            'join code domain' => ['https://joinmyquiz.com/?gc=12345678'],
            'subdomain of its new name' => ['https://app.wayground.com/x'],
            'upper case host' => ['https://QUIZIZZ.com/x'],
            'fragment' => ['https://quizizz.com/x#hasil'],
            'surrounding spaces are trimmed by the form, not rejected here' => ['  https://quizizz.com/x  '],
        ];
    }

    /** @return array<string, array{mixed}> */
    public static function unacceptable(): array
    {
        return [
            'plain http' => ['http://quizizz.com/x'],
            'other site' => ['https://example.com/quizizz.com'],
            'other site naming quizizz in the query' => ['https://example.com/?u=https://quizizz.com'],
            'quizizz as a subdomain of another site' => ['https://quizizz.com.example.com/x'],
            'host that only ends the same way' => ['https://notquizizz.com/x'],
            'hyphenated lookalike' => ['https://quizizz-com.example.com/x'],
            'new name as a subdomain of another site' => ['https://wayground.com.example.com/x'],
            'new name suffix only' => ['https://notwayground.com/x'],
            'a site that merely resembles the old name' => ['https://quizizz.co/x'],
            'credentials' => ['https://user:pass@quizizz.com/x'],
            'user name only' => ['https://abc@quizizz.com/x'],
            'password only' => ['https://:pass@quizizz.com/x'],
            'real host hidden after an at sign' => ['https://quizizz.com@example.com/x'],
            'backslash trick browsers read as a slash' => ['https://example.com\\@quizizz.com/x'],
            'custom port' => ['https://quizizz.com:8443/x'],
            'default port written out' => ['https://quizizz.com:443/x'],
            'javascript scheme' => ['javascript:alert(1)'],
            'data scheme' => ['data:text/html,<script>alert(1)</script>'],
            'scheme relative' => ['//quizizz.com/x'],
            'no scheme' => ['quizizz.com/x'],
            'ftp' => ['ftp://quizizz.com/x'],
            'space inside' => ['https://quizizz.com/a b'],
            'line break' => ["https://quizizz.com/x\nSet-Cookie: a=b"],
            'tab' => ["https://quizizz.com/\tx"],
            'null byte' => ["https://quizizz.com/x\0y"],
            'trailing dot host' => ['https://quizizz.com./x'],
            'non ascii look-alike host' => ['https://quіzizz.com/x'],   // Cyrillic "і"
            'empty' => [''],
            'not a string' => [['https://quizizz.com/x']],
            'null' => [null],
        ];
    }

    #[DataProvider('acceptable')]
    public function test_accepts(string $url): void
    {
        $this->assertTrue($this->passes($url), $url);
    }

    #[DataProvider('unacceptable')]
    public function test_rejects(mixed $url): void
    {
        $this->assertFalse($this->passes($url), var_export($url, true));
    }

    public function test_with_no_host_configured_nothing_is_accepted(): void
    {
        config(['didik.quizizz_hosts' => []]);

        $this->assertFalse($this->passes('https://quizizz.com/x'));
        $this->assertFalse($this->passes('https://example.com/x'));
    }

    public function test_the_allowed_hosts_come_from_configuration(): void
    {
        config(['didik.quizizz_hosts' => ['example.org']]);

        $this->assertTrue($this->passes('https://example.org/x'));
        $this->assertTrue($this->passes('https://kelas.example.org/x'));
        $this->assertFalse($this->passes('https://quizizz.com/x'));
        $this->assertFalse($this->passes('https://exampleXorg/x'), 'the dot in a host must not act as a wildcard');
    }

    public function test_the_failure_message_names_the_accepted_hosts(): void
    {
        config(['didik.quizizz_hosts' => ['quizizz.com', 'wayground.com']]);

        $message = null;
        (new QuizizzUrl)->validate('url', 'https://example.com', function (string $m) use (&$message) {
            $message = $m;
        });

        $this->assertStringContainsString('quizizz.com atau wayground.com', (string) $message);
    }
}
