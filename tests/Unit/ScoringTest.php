<?php

namespace Tests\Unit;

use App\Services\QuizEngine\Scoring;
use PHPUnit\Framework\Attributes\DataProvider;
use PHPUnit\Framework\TestCase;

class ScoringTest extends TestCase
{
    #[DataProvider('cases')]
    public function test_stars_follow_the_published_thresholds(int $score, int $max, int $stars): void
    {
        $this->assertSame($stars, Scoring::stars($score, $max));
    }

    public static function cases(): array
    {
        return [
            'perfect' => [8, 8, 3],
            'exactly 85 percent' => [17, 20, 3],
            'just under 85 percent' => [16, 20, 2],
            'exactly 60 percent' => [12, 20, 2],
            'just under 60 percent' => [11, 20, 1],
            'nothing right still earns one star' => [0, 8, 1],
            'quiz with no points' => [0, 0, 1],
        ];
    }
}
