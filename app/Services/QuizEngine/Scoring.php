<?php

namespace App\Services\QuizEngine;

/** Pure scoring rules. Game concepts never call or change these. */
final class Scoring
{
    /** Share of the maximum score that earns three and two stars. */
    public const THREE_STARS = 85;

    public const TWO_STARS = 60;

    /** Everyone who finishes earns at least one star; stars reward effort first. */
    public static function stars(int $score, int $maxScore): int
    {
        if ($maxScore <= 0) {
            return 1;
        }

        $percent = $score / $maxScore * 100;

        return match (true) {
            $percent >= self::THREE_STARS => 3,
            $percent >= self::TWO_STARS => 2,
            default => 1,
        };
    }
}
