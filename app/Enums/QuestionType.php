<?php

namespace App\Enums;

use App\Enums\Concerns\HasLabel;

enum QuestionType: string
{
    use HasLabel;

    case Single = 'single';
    case TrueFalse = 'truefalse';
}
