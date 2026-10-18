<?php

namespace App\Games;

/** Misi Berlevel (Seberang Sungai): questions grouped into levels along a path of stepping stones. */
class RiverQuest extends GameConcept
{
    public function key(): string
    {
        return 'quest';
    }

    public function fields(): array
    {
        return [
            'level_size' => ['type' => 'integer', 'min' => 3, 'max' => 10, 'default' => 5],
        ];
    }
}
