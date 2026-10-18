<?php

namespace App\Models;

use App\Enums\LinkStatus;
use App\Models\Concerns\HasTags;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Support\Facades\Storage;

#[Fillable(['title', 'url', 'description', 'category_id', 'school_level_id', 'thumbnail_path', 'status'])]
class QuizizzLink extends Model
{
    use HasFactory, HasTags, SoftDeletes;

    protected function casts(): array
    {
        return ['status' => LinkStatus::class];
    }

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function level(): BelongsTo
    {
        return $this->belongsTo(SchoolLevel::class, 'school_level_id');
    }

    public function collections(): BelongsToMany
    {
        return $this->belongsToMany(QuizizzCollection::class, 'quizizz_collection_link')->withPivot('position');
    }

    public function scopePublished(Builder $query): void
    {
        $query->where('status', LinkStatus::Published);
    }

    public function thumbnailUrl(): ?string
    {
        return $this->thumbnail_path ? Storage::disk('public')->url($this->thumbnail_path) : null;
    }
}
