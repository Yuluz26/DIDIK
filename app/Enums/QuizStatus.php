<?php

namespace App\Enums;

use App\Enums\Concerns\HasLabel;

enum QuizStatus: string
{
    use HasLabel;

    case Draft = 'draft';
    case Published = 'published';
    case Archived = 'archived';
}
