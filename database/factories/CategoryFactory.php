<?php

namespace Database\Factories;

use App\Enums\CategoryTheme;
use App\Enums\CategoryType;
use App\Models\Category;
use Illuminate\Database\Eloquent\Factories\Factory;

/** @extends Factory<Category> */
class CategoryFactory extends Factory
{
    public function definition(): array
    {
        return [
            'parent_id' => null,
            'type' => CategoryType::Subject,
            'name' => fake()->unique()->words(2, true),
            'theme' => fake()->randomElement(CategoryTheme::cases()),
            'icon' => 'shapes',
            'position' => 0,
        ];
    }

    public function topicOf(Category $subject): static
    {
        return $this->state(fn () => [
            'parent_id' => $subject->id,
            'type' => CategoryType::Topic,
            'theme' => $subject->theme,
            'icon' => $subject->icon,
        ]);
    }
}
