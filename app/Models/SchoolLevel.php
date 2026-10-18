<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['name', 'slug', 'min_age', 'max_age', 'position'])]
class SchoolLevel extends Model
{
    use HasFactory;

    public function quizzes(): HasMany
    {
        return $this->hasMany(Quiz::class);
    }

    /** "8 tahun" or "5 hingga 6 tahun". */
    public function ageLabel(): string
    {
        return $this->min_age === $this->max_age
            ? __('public.age_single', ['age' => $this->min_age])
            : __('public.age_range', ['min' => $this->min_age, 'max' => $this->max_age]);
    }
}
