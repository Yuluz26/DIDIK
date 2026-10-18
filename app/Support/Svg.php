<?php

namespace App\Support;

use Illuminate\Support\HtmlString;
use InvalidArgumentException;

/**
 * Inlines the SVG files in resources/svg/icons (Lucide, ISC licence) so they follow the text
 * colour and need no extra request. Icons are decorative unless a label is given.
 */
final class Svg
{
    /** @var array<string, string> */
    private static array $cache = [];

    public static function icon(string $name, ?string $class = null, ?string $label = null, string $extra = ''): HtmlString
    {
        if (! preg_match('/^[a-z0-9-]+$/', $name)) {
            throw new InvalidArgumentException("Invalid icon name [{$name}].");
        }

        $markup = self::$cache[$name] ??= self::read($name);

        // $extra arrives already escaped from a Blade attribute bag (for example Alpine's x-show).
        $attributes = 'class="icon'.($class ? ' '.e($class) : '').'" focusable="false"'.($extra !== '' ? ' '.$extra : '');
        $attributes .= $label === null
            ? ' aria-hidden="true"'
            : ' role="img" aria-label="'.e($label).'"';

        // Drop the file's own size and class, keep its viewBox and stroke settings.
        $markup = preg_replace('/\s(width|height|class)="[^"]*"/', '', $markup);

        return new HtmlString(preg_replace('/^<svg/', '<svg '.$attributes, $markup, 1));
    }

    private static function read(string $name): string
    {
        $path = resource_path("svg/icons/{$name}.svg");

        if (! is_file($path)) {
            // A typo should be loud while developing, but never take a public page down.
            if (app()->isProduction()) {
                return self::read('shapes');
            }

            throw new InvalidArgumentException("Icon [{$name}] does not exist.");
        }

        // Strip the licence comment lucide puts first.
        return trim(preg_replace('/<!--.*?-->/s', '', file_get_contents($path)));
    }
}
