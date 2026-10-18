<?php

namespace App\Models;

use App\Enums\Difficulty;
use App\Enums\FeedbackMode;
use App\Enums\QuizStatus;
use App\Games\GameConcept;
use App\Games\GameConceptRegistry;
use App\Models\Concerns\HasTags;
use App\Models\Concerns\HasUniqueSlug;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

#[Fillable([
    'title', 'summary', 'language', 'category_id', 'school_level_id', 'difficulty', 'status', 'game_concept',
    'game_settings', 'attempts_allowed', 'feedback_mode', 'shuffle_questions', 'shuffle_options',
    'available_from', 'available_until', 'published_at', 'created_by',
])]
class Quiz extends Model
{
    use HasFactory, HasTags, HasUniqueSlug, SoftDeletes;

    protected function casts(): array
    {
        return [
            'status' => QuizStatus::class,
            'difficulty' => Difficulty::class,
            'feedback_mode' => FeedbackMode::class,
            'game_settings' => 'array',
            'attempts_allowed' => 'integer',
            'shuffle_questions' => 'boolean',
            'shuffle_options' => 'boolean',
            'available_from' => 'datetime',
            'available_until' => 'datetime',
            'published_at' => 'datetime',
        ];
    }

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function level(): BelongsTo
    {
        return $this->belongsTo(SchoolLevel::class, 'school_level_id');
    }

    public function creator(): BelongsTo
    {
        return $this->belongsTo(User::class, 'created_by');
    }

    public function questions(): HasMany
    {
        return $this->hasMany(Question::class)->orderBy('position')->orderBy('id');
    }

    public function attempts(): HasMany
    {
        return $this->hasMany(Attempt::class);
    }

    /** Published and inside its availability window: the only quizzes the public may see. */
    public function scopeAvailable(Builder $query): void
    {
        $now = now();

        $query->where('status', QuizStatus::Published)
            ->where(fn (Builder $q) => $q->whereNull('available_from')->orWhere('available_from', '<=', $now))
            ->where(fn (Builder $q) => $q->whereNull('available_until')->orWhere('available_until', '>=', $now));
    }

    public function isAvailable(): bool
    {
        $now = now();

        return $this->status === QuizStatus::Published
            && ($this->available_from === null || $this->available_from->lte($now))
            && ($this->available_until === null || $this->available_until->gte($now));
    }

    /** The game concept, falling back to the default when the stored key is unknown. */
    public function concept(): GameConcept
    {
        return app(GameConceptRegistry::class)->resolve($this->game_concept);
    }

    /** Concept settings merged over the concept's defaults. */
    public function conceptSettings(): array
    {
        return $this->concept()->normalize($this->game_settings ?? []);
    }
}
