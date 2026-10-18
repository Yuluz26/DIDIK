<?php

namespace Tests\Unit;

use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

/**
 * Guards the accessibility numbers in docs/design/DESIGN.md. Reads the real token file, so a
 * colour change that breaks legibility fails the build instead of reaching a child's screen.
 */
class DesignTokenContrastTest extends TestCase
{
    private const TEXT = 4.5;

    private const GRAPHIC = 3.0;

    /** @var array<string, string> */
    private static array $tokens = [];

    public static function setUpBeforeClass(): void
    {
        $css = file_get_contents(dirname(__DIR__, 2).'/resources/css/tokens.css');
        preg_match_all('/--([a-z0-9-]+):\s*(#[0-9a-f]{6});/i', $css, $matches, PREG_SET_ORDER);

        foreach ($matches as [, $name, $hex]) {
            self::$tokens[$name] = strtolower($hex);
        }
    }

    #[DataProvider('pairs')]
    public function test_pair_meets_its_contrast_requirement(string $foreground, string $background, float $minimum): void
    {
        $this->assertArrayHasKey($foreground, self::$tokens, "Token --{$foreground} is missing.");
        $this->assertArrayHasKey($background, self::$tokens, "Token --{$background} is missing.");

        $ratio = self::ratio(self::$tokens[$foreground], self::$tokens[$background]);

        $this->assertGreaterThanOrEqual(
            $minimum,
            $ratio,
            sprintf('--%s on --%s is %.2f:1, needs %.1f:1.', $foreground, $background, $ratio, $minimum),
        );
    }

    /** @return array<string, array{string, string, float}> */
    public static function pairs(): array
    {
        $pairs = [
            // Text on the ground and on the river
            ['ink', 'ground', self::TEXT],
            ['ink-2', 'ground', self::TEXT],
            ['brand', 'ground', self::TEXT],
            ['ink', 'river', self::TEXT],
            ['ink-2', 'river', self::TEXT],
            // Primary action
            ['on-brand', 'brand', self::TEXT],
            ['on-brand', 'brand-hover', self::TEXT],
            // Focus ring and star outline are graphics: 3:1 against what they sit on
            ['focus', 'ground', self::GRAPHIC],
            ['focus', 'panel', self::GRAPHIC],
            ['focus', 'river', self::GRAPHIC],
            ['star-stroke', 'ground', self::GRAPHIC],
            ['brand', 'tint-ok', self::GRAPHIC],
            // Admin
            ['ink', 'admin-bg', self::TEXT],
            ['ink-2', 'admin-bg', self::TEXT],
            ['danger', 'panel', self::TEXT],
            ['danger', 'admin-bg', self::TEXT],
            ['on-brand', 'danger', self::TEXT],
            ['field-border', 'panel', self::GRAPHIC],
            ['warn-ink', 'warn-tint', self::TEXT],
        ];

        // Every tint is used with its own ink, and the main ink is also used over each tint.
        foreach (['ok', 'hint', 'info', 'peach', 'sky', 'butter', 'lilac', 'mint'] as $name) {
            $pairs[] = ["ink-{$name}", "tint-{$name}", self::TEXT];
            $pairs[] = ['ink', "tint-{$name}", self::TEXT];
            $pairs[] = ["ink-{$name}", 'ground', self::TEXT];
        }

        $named = [];

        foreach ($pairs as [$foreground, $background, $minimum]) {
            $named["{$foreground} on {$background}"] = [$foreground, $background, $minimum];
        }

        return $named;
    }

    private static function ratio(string $a, string $b): float
    {
        [$lighter, $darker] = [self::luminance($a), self::luminance($b)];

        if ($lighter < $darker) {
            [$lighter, $darker] = [$darker, $lighter];
        }

        return ($lighter + 0.05) / ($darker + 0.05);
    }

    private static function luminance(string $hex): float
    {
        $channels = array_map(function (string $part) {
            $value = hexdec($part) / 255;

            return $value <= 0.03928 ? $value / 12.92 : (($value + 0.055) / 1.055) ** 2.4;
        }, str_split(ltrim($hex, '#'), 2));

        return 0.2126 * $channels[0] + 0.7152 * $channels[1] + 0.0722 * $channels[2];
    }
}
