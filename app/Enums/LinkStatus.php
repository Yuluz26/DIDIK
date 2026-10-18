<?php

namespace App\Enums;

use App\Enums\Concerns\HasLabel;

enum LinkStatus: string
{
    use HasLabel;

    case Draft = 'draft';
    case Published = 'published';
    case Broken = 'broken';
    case Archived = 'archived';
}
