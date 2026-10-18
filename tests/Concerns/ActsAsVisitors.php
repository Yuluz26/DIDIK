<?php

namespace Tests\Concerns;

use Illuminate\Testing\TestResponse;

/**
 * Feature tests do not keep a session between requests. This lets a test play several anonymous
 * visitors, each with their own session cookie, to check that one cannot touch another's attempt.
 */
trait ActsAsVisitors
{
    /** @var array<string, string> visitor name => encrypted session cookie value */
    private array $visitorCookies = [];

    /**
     * Run a request as a named visitor. The first call gives that visitor a fresh session; later
     * calls send the cookie that session was given.
     *
     * @param  callable(): TestResponse  $request
     */
    protected function asVisitor(string $name, callable $request): TestResponse
    {
        $cookie = config('session.cookie');

        $this->unencryptedCookies = isset($this->visitorCookies[$name])
            ? [$cookie => $this->visitorCookies[$name]]
            : [];
        $this->defaultCookies = [];

        // JSON requests only carry cookies when asked to, as with a browser's fetch().
        $this->withCredentials();

        $response = $request();

        foreach ($response->headers->getCookies() as $received) {
            if ($received->getName() === $cookie) {
                $this->visitorCookies[$name] = $received->getValue();
            }
        }

        return $response;
    }
}
