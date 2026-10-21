<?php

use App\Http\Middleware\EnsureAdmin;
use App\Http\Middleware\PreventRequestForgery;
use App\Http\Middleware\SecurityHeaders;
use Illuminate\Contracts\Auth\Middleware\AuthenticatesRequests;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Foundation\Http\Middleware\PreventRequestForgery as FrameworkPreventRequestForgery;
use Illuminate\Http\Request;
use Illuminate\Routing\Middleware\ThrottleRequests;
use Illuminate\Support\Facades\Route;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
        then: function (): void {
            Route::middleware('web')
                ->prefix('admin')
                ->name('admin.')
                ->group(base_path('routes/admin.php'));
        },
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->alias(['admin' => EnsureAdmin::class]);
        $middleware->append(SecurityHeaders::class);
        $middleware->web(
            // One cookie only: the session's (see the class for why the XSRF-TOKEN cookie goes).
            replace: [FrameworkPreventRequestForgery::class => PreventRequestForgery::class],
            // A generous ceiling per network address for every page, so one client cannot flood the
            // server (every cookie-less request would otherwise create a session row).
            append: [ThrottleRequests::using('web')],
        );
        // Requests for any other Host are refused (400), so a forged Host header cannot put an
        // attacker's address into generated links. Off in local and testing (the framework skips it).
        $middleware->trustHosts(
            at: fn () => array_map(fn (string $host) => '^'.preg_quote($host, '/').'$', config('didik.trusted_hosts')),
        );
        // The role check must run before route-model binding: otherwise a signed-in user without
        // the role learns which records exist (404 vs 403) before being refused.
        $middleware->appendToPriorityList(AuthenticatesRequests::class, EnsureAdmin::class);
        $middleware->redirectGuestsTo(fn () => route('admin.login'));
        $middleware->redirectUsersTo(fn () => route('admin.dashboard'));
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->shouldRenderJsonWhen(
            fn (Request $request) => $request->is('api/*') || $request->expectsJson(),
        );
    })->create();
