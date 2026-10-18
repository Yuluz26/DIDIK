<?php

namespace App\Games;

/** Soalan & Jawapan: one question per screen, plain and calm. */
class QuestionAnswer extends GameConcept
{
    public function key(): string
    {
        return 'qa';
    }

    public function fields(): array
    {
        return [
            'progress' => ['type' => 'select', 'options' => ['dots', 'bar'], 'default' => 'dots'],
        ];
    }
}
