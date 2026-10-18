<?php

namespace Database\Factories;

use App\Enums\LinkStatus;
use App\Models\QuizizzCollection;
use Illuminate\Database\Eloquent\Factories\Factory;

/** @extends Factory<QuizizzCollection> */
class QuizizzCollectionFactory extends Factory
{
    public function definition(): array
    {
        return [
            'title' => fake()->unique()->sentence(3),
            'description' => fake()->sentence(8),
            'status' => LinkStatus::Draft,
            'position' => 0,
        ];
    }

    public function published(): static
    {
        return $this->state(fn () => ['status' => LinkStatus::Published]);
    }
}
