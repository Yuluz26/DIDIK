<?php

namespace App\Enums;

use App\Enums\Concerns\HasLabel;

enum Difficulty: string
{
    use HasLabel;

    case Easy = 'mudah';
    case Medium = 'sederhana';
    case Hard = 'mencabar';
}
