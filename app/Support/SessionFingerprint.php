<?php

namespace App\Support;

use Illuminate\Http\Request;

/**
 * Identifies an anonymous visitor to the quiz engine without storing the session id:
 * only a keyed hash of it reaches the database.
 */
final class SessionFingerprint
{
    public static function for(Request $request): string
    {
        return hash_hmac('sha256', $request->session()->getId(), (string) config('app.key'));
    }

    public static function matches(string $stored, Request $request): bool
    {
        return hash_equals($stored, self::for($request));
    }
}
