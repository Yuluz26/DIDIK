<?php

namespace Database\Factories;

use App\Enums\LinkStatus;
use App\Models\QuizizzLink;
use Illuminate\Database\Eloquent\Factories\Factory;

/** @extends Factory<QuizizzLink> */
class QuizizzLinkFactory extends Factory
{
    public function definition(): array
    {
        return [
            'title' => fake()->unique()->sentence(3),
            'url' => 'https://quizizz.com/admin/quiz/'.fake()->unique()->bothify('????????????'),
            'description' => fake()->sentence(8),
            'status' => LinkStatus::Draft,
        ];
    }

    public function published(): static
    {
        return $this->state(fn () => ['status' => LinkStatus::Published]);
    }
}
