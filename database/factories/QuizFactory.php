<?php

namespace Database\Factories;

use App\Enums\Difficulty;
use App\Enums\QuizStatus;
use App\Models\Quiz;
use Illuminate\Database\Eloquent\Factories\Factory;

/** @extends Factory<Quiz> */
class QuizFactory extends Factory
{
    public function definition(): array
    {
        return [
            'title' => fake()->unique()->sentence(3),
            'summary' => fake()->sentence(10),
            'difficulty' => Difficulty::Medium,
            'status' => QuizStatus::Draft,
            'game_concept' => 'qa',
        ];
    }

    public function published(): static
    {
        return $this->state(fn () => ['status' => QuizStatus::Published, 'published_at' => now()]);
    }

    public function archived(): static
    {
        return $this->state(fn () => ['status' => QuizStatus::Archived]);
    }

    public function concept(string $key, array $settings = []): static
    {
        return $this->state(fn () => ['game_concept' => $key, 'game_settings' => $settings]);
    }
}
