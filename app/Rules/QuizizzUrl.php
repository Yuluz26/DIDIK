<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\ValidationRule;

/**
 * Accepts only https links on quizizz.com (or one of its subdomains), with no embedded
 * credentials and no custom port. DIDIK stores these as plain external links; it never
 * fetches, embeds or imports them, so this is about what an admin can point visitors to.
 */
class QuizizzUrl implements ValidationRule
{
    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        $parts = is_string($value) ? parse_url(trim($value)) : false;

        $valid = is_array($parts)
            && ($parts['scheme'] ?? null) === 'https'
            && isset($parts['host'])
            && ! isset($parts['user'], $parts['pass'])
            && ! isset($parts['port'])
            && $this->isQuizizzHost(strtolower($parts['host']));

        if (! $valid) {
            $fail(__('links.url_invalid'));
        }
    }

    private function isQuizizzHost(string $host): bool
    {
        return $host === 'quizizz.com' || str_ends_with($host, '.quizizz.com');
    }
}
