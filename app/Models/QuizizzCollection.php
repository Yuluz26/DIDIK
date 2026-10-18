<?php

namespace App\Models;

use App\Enums\LinkStatus;
use App\Models\Concerns\HasUniqueSlug;
use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

#[Fillable(['title', 'slug', 'description', 'status', 'position'])]
class QuizizzCollection extends Model
{
    use HasFactory, HasUniqueSlug;

    protected function casts(): array
    {
        return ['status' => LinkStatus::class];
    }

    public function links(): BelongsToMany
    {
        return $this->belongsToMany(QuizizzLink::class, 'quizizz_collection_link')
            ->withPivot('position')
            ->orderByPivot('position');
    }

    /** Only the links the public may see, in curated order. */
    public function publishedLinks(): BelongsToMany
    {
        return $this->links()->where('quizizz_links.status', LinkStatus::Published);
    }

    public function scopePublished(Builder $query): void
    {
        $query->where('status', LinkStatus::Published);
    }
}
