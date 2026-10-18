<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\ValidationRule;
use Illuminate\Support\Arr;

/**
 * Accepts only https links on the Quizizz hosts listed in config/didik.php (or their
 * subdomains), with no embedded credentials, no custom port, and no whitespace or control
 * characters. DIDIK stores these as plain external links; it never fetches, embeds or imports
 * them, so this is about what an admin can point visitors to.
 *
 * The whole string is matched instead of going through parse_url(): URL parsers disagree on input
 * such as backslashes and user info, and what a browser does with the saved link is what counts.
 */
class QuizizzUrl implements ValidationRule
{
    /** @return list<string> */
    public static function hosts(): array
    {
        return array_values(array_filter((array) config('didik.quizizz_hosts'), 'is_string'));
    }

    /** The hosts as a sentence fragment for messages: "quizizz.com, wayground.com atau joinmyquiz.com". */
    public static function hostsText(): string
    {
        return Arr::join(self::hosts(), ', ', ' '.__('links.or').' ');
    }

    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        $url = is_string($value) ? trim($value) : '';

        if (! $this->matches($url)) {
            $fail(__('links.url_invalid', ['hosts' => self::hostsText()]));
        }
    }

    private function matches(string $url): bool
    {
        $hosts = self::hosts();

        // With no host configured the pattern below would accept anything, so refuse everything.
        if ($hosts === []) {
            return false;
        }

        $alternatives = implode('|', array_map(fn (string $host) => preg_quote($host, '~'), $hosts));

        // https://, any number of host labels, one allowed host, then optionally a path, query or fragment.
        return preg_match('~^https://(?:[a-z0-9-]+\.)*(?:'.$alternatives.')(?:[/?#][^\x00-\x20\x7f\\\\]*)?\z~i', $url) === 1;
    }
}
