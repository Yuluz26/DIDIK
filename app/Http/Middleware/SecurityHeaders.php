<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Vite;
use Symfony\Component\HttpFoundation\Response;

/**
 * Browser-side protections for every response: a Content-Security-Policy that allows scripts from
 * this site only (no inline script, no eval: the pages ship Alpine's CSP build for exactly this),
 * no framing, no sniffing, a quiet Referer, and HSTS once the visit is over HTTPS.
 *
 * Inline style attributes stay allowed (style-src-attr): the pages set a few custom properties and
 * widths that way, and a style attribute cannot run code. Everything else comes from 'self'.
 */
class SecurityHeaders
{
    /** Pages that must never be served from a cache after the visitor has left (back button, shared proxy). */
    private const UNCACHED = ['admin', 'admin/*', 'keputusan/*'];

    public function handle(Request $request, Closure $next): Response
    {
        $response = $next($request);

        $headers = [
            'X-Content-Type-Options' => 'nosniff',
            'X-Frame-Options' => 'DENY',
            'Referrer-Policy' => 'strict-origin-when-cross-origin',
            'Permissions-Policy' => 'accelerometer=(), camera=(), geolocation=(), gyroscope=(), microphone=(), payment=(), usb=()',
            'Cross-Origin-Opener-Policy' => 'same-origin',
        ];

        if ($this->shouldSendPolicy()) {
            $headers['Content-Security-Policy'] = $this->policy($request);
        }

        if ($request->isSecure() && ($seconds = (int) config('didik.hsts_seconds')) > 0) {
            $headers['Strict-Transport-Security'] = "max-age={$seconds}";
        }

        foreach ($headers as $name => $value) {
            if (! $response->headers->has($name)) {
                $response->headers->set($name, $value);
            }
        }

        if ($request->is(...self::UNCACHED)) {
            $response->headers->set('Cache-Control', 'no-store, private');
        }

        // Do not advertise the PHP version.
        $response->headers->remove('X-Powered-By');

        return $response;
    }

    /** Off while the Vite dev server is running (it serves scripts and styles from another origin). */
    private function shouldSendPolicy(): bool
    {
        return config('didik.csp') && ! Vite::isRunningHot();
    }

    private function policy(Request $request): string
    {
        // Built assets come from this site, or from ASSET_URL when they are served from a CDN.
        $assets = "'self'".(($origin = $this->assetOrigin()) ? " {$origin}" : '');

        $directives = [
            "default-src 'self'",
            "script-src {$assets}",
            "style-src {$assets}",
            "style-src-attr 'unsafe-inline'",
            "img-src {$assets} data:",
            "font-src {$assets}",
            "connect-src 'self'",
            "manifest-src 'self'",
            "form-action 'self'",
            "base-uri 'self'",
            "frame-ancestors 'none'",
            "object-src 'none'",
        ];

        if ($request->isSecure()) {
            $directives[] = 'upgrade-insecure-requests';
        }

        return implode('; ', $directives);
    }

    private function assetOrigin(): ?string
    {
        $parts = parse_url((string) config('app.asset_url'));

        if (! isset($parts['scheme'], $parts['host'])) {
            return null;
        }

        return $parts['scheme'].'://'.$parts['host'].(isset($parts['port']) ? ':'.$parts['port'] : '');
    }
}
