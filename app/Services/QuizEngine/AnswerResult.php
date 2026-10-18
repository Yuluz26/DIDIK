<?php

namespace App\Services\QuizEngine;

/** What happened when one answer was recorded. Plain data; the controller decides what to reveal. */
final readonly class AnswerResult
{
    public function __construct(
        public bool $correct,
        public int $correctOptionId,
        public ?string $explanation,
        public int $points,
        public int $score,
        public int $answered,
        public int $total,
        public bool $finished,
    ) {}
}
