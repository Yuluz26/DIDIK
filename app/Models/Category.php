<?php

namespace App\Models;

use App\Enums\CategoryTheme;
use App\Enums\CategoryType;
use App\Models\Concerns\HasUniqueSlug;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['parent_id', 'type', 'name', 'slug', 'theme', 'icon', 'position'])]
class Category extends Model
{
    use HasFactory, HasUniqueSlug;

    protected function casts(): array
    {
        return [
            'type' => CategoryType::class,
            'theme' => CategoryTheme::class,
        ];
    }

    protected function slugSource(): string
    {
        return 'name';
    }

    public function parent(): BelongsTo
    {
        return $this->belongsTo(self::class, 'parent_id');
    }

    public function children(): HasMany
    {
        return $this->hasMany(self::class, 'parent_id')->orderBy('position')->orderBy('name');
    }

    public function quizzes(): HasMany
    {
        return $this->hasMany(Quiz::class);
    }

    public function scopeSubjects(Builder $query): void
    {
        $query->where('type', CategoryType::Subject)->orderBy('position')->orderBy('name');
    }

    /** The subject this category belongs to (itself when it is a subject). */
    public function subject(): self
    {
        return $this->type === CategoryType::Subject ? $this : ($this->parent ?? $this);
    }

    /** Ids of this category plus all of its topics, for "everything in this subject" filters. */
    public function withDescendantIds(): array
    {
        return [$this->id, ...$this->children()->pluck('id')->all()];
    }

    /** Theme used for display: topics follow their subject. */
    public function displayTheme(): CategoryTheme
    {
        return $this->subject()->theme;
    }

    public function displayIcon(): string
    {
        return $this->subject()->icon;
    }
}
