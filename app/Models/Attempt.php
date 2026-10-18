<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Attributes\Hidden;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable([
    'uuid', 'quiz_id', 'session_hash', 'layout', 'started_at', 'completed_at', 'score',
    'max_score', 'correct_count', 'question_count', 'stars',
])]
#[Hidden(['session_hash'])]
class Attempt extends Model
{
    use HasFactory;

    protected function casts(): array
    {
        return [
            'layout' => 'array',
            'started_at' => 'datetime',
            'completed_at' => 'datetime',
            'score' => 'integer',
            'max_score' => 'integer',
            'correct_count' => 'integer',
            'question_count' => 'integer',
            'stars' => 'integer',
        ];
    }

    public function getRouteKeyName(): string
    {
        return 'uuid';
    }

    public function quiz(): BelongsTo
    {
        return $this->belongsTo(Quiz::class);
    }

    public function answers(): HasMany
    {
        return $this->hasMany(AttemptAnswer::class);
    }

    public function isCompleted(): bool
    {
        return $this->completed_at !== null;
    }
}
