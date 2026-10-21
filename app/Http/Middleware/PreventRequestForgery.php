<?php

namespace App\Http\Middleware;

use Illuminate\Foundation\Http\Middleware\PreventRequestForgery as BaseMiddleware;

/**
 * The framework's CSRF protection, without the extra XSRF-TOKEN cookie. That cookie exists for
 * front ends that copy it into a header; ours send the token from the page itself (the csrf-token
 * meta tag and @csrf), so the site sets a single cookie, the session's, and says so in the notice.
 */
class PreventRequestForgery extends BaseMiddleware
{
    protected $addHttpCookie = false;
}
