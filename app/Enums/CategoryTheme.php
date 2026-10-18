<?php

namespace App\Enums;

use App\Enums\Concerns\HasLabel;

/**
 * Subject colours. Each case maps to a tint/ink pair in resources/css/tokens.css
 * (--tint-{value} and --ink-{value}); the two are always used together.
 */
enum CategoryTheme: string
{
    use HasLabel;

    case Peach = 'peach';
    case Sky = 'sky';
    case Butter = 'butter';
    case Lilac = 'lilac';
    case Mint = 'mint';
}
