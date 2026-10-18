<?php

namespace App\Models\Concerns;

use App\Models\Tag;
use Illuminate\Database\Eloquent\Relations\MorphToMany;
use Illuminate\Support\Str;

trait HasTags
{
    public function tags(): MorphToMany
    {
        return $this->morphToMany(Tag::class, 'taggable')->orderBy('tags.name');
    }

    /**
     * Replace this model's tags with the given names (a comma separated string or an array).
     * Names are trimmed, de-duplicated case-insensitively and capped at ten.
     */
    public function syncTagNames(string|array|null $names): void
    {
        $names = is_array($names) ? $names : explode(',', (string) $names);

        $clean = collect($names)
            ->map(fn ($name) => Str::limit(trim((string) $name), 50, ''))
            ->filter()
            ->unique(fn ($name) => mb_strtolower($name))
            ->take(10);

        $ids = $clean->map(function (string $name) {
            $slug = Str::slug($name) ?: md5($name);

            return Tag::firstOrCreate(['slug' => $slug], ['name' => $name])->id;
        });

        $this->tags()->sync($ids->all());
    }

    public function tagList(): string
    {
        return $this->tags->pluck('name')->implode(', ');
    }
}
