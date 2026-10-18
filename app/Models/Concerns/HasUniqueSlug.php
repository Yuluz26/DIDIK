<?php

namespace App\Models\Concerns;

use Illuminate\Database\Eloquent\SoftDeletes;
use Illuminate\Support\Str;

/**
 * Fills `slug` from a source attribute when a model is created. The slug is not
 * rewritten afterwards, so public URLs stay stable when a title is edited.
 */
trait HasUniqueSlug
{
    protected static function bootHasUniqueSlug(): void
    {
        static::creating(function ($model) {
            if (blank($model->slug)) {
                $model->slug = $model->makeUniqueSlug((string) $model->{$model->slugSource()});
            }
        });
    }

    /** Attribute the slug is built from; override in the model when it is not `title`. */
    protected function slugSource(): string
    {
        return 'title';
    }

    public function makeUniqueSlug(string $source): string
    {
        $base = Str::limit(Str::slug($source), 80, '') ?: 'item';
        $slug = $base;
        $suffix = 2;

        while ($this->slugExists($slug)) {
            $slug = $base.'-'.$suffix++;
        }

        return $slug;
    }

    private function slugExists(string $slug): bool
    {
        $query = static::query()->where('slug', $slug);

        if (in_array(SoftDeletes::class, class_uses_recursive(static::class), true)) {
            $query->withTrashed();
        }

        return $query->exists();
    }
}
