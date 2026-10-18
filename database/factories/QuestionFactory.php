<?php

namespace Database\Factories;

use App\Enums\QuestionType;
use App\Models\Question;
use App\Models\QuestionOption;
use Illuminate\Database\Eloquent\Factories\Factory;

/** @extends Factory<Question> */
class QuestionFactory extends Factory
{
    public function definition(): array
    {
        return [
            'type' => QuestionType::Single,
            'body' => rtrim(fake()->sentence(6), '.').'?',
            'explanation' => fake()->sentence(8),
            'points' => 1,
            'position' => 0,
        ];
    }

    /** Create $count options after the question; the option at $correct (zero based) is the right one. */
    public function withOptions(int $count = 3, int $correct = 0): static
    {
        return $this->afterCreating(function (Question $question) use ($count, $correct) {
            for ($i = 0; $i < $count; $i++) {
                QuestionOption::create([
                    'question_id' => $question->id,
                    'body' => 'Pilihan '.chr(65 + $i),
                    'is_correct' => $i === $correct,
                    'position' => $i,
                ]);
            }
        });
    }
}
