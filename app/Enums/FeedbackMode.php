<?php

namespace App\Enums;

use App\Enums\Concerns\HasLabel;

enum FeedbackMode: string
{
    use HasLabel;

    /** Tell the child right after each answer. */
    case Instant = 'instant';

    /** Hold every result back until the quiz is finished. */
    case End = 'end';
}
