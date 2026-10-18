<?php

namespace App\Enums;

use App\Enums\Concerns\HasLabel;

enum CategoryType: string
{
    use HasLabel;

    case Subject = 'subject';
    case Topic = 'topic';
}
