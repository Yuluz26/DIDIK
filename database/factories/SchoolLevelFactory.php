<?php

namespace Database\Factories;

use App\Models\SchoolLevel;
use Illuminate\Database\Eloquent\Factories\Factory;

/** @extends Factory<SchoolLevel> */
class SchoolLevelFactory extends Factory
{
    public function definition(): array
    {
        $year = fake()->unique()->numberBetween(1, 60);

        return [
            'name' => "Tahun {$year}",
            'slug' => "tahun-{$year}",
            'min_age' => 7,
            'max_age' => 7,
            'position' => $year,
        ];
    }
}
