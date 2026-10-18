<?php

namespace App\Games;

/** Kutip Bintang: every correct answer lights a star slot. */
class StarCollector extends GameConcept
{
    public function key(): string
    {
        return 'stars';
    }

    public function fields(): array
    {
        return [
            'show_streak' => ['type' => 'boolean', 'default' => true],
        ];
    }
}
