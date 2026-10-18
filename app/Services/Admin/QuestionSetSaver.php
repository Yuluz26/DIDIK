<?php

namespace App\Services\Admin;

use App\Enums\QuestionType;
use App\Models\Question;
use App\Models\QuestionOption;
use App\Models\Quiz;
use Illuminate\Support\Facades\DB;

/**
 * Saves a whole quiz's questions in one transaction, in the order given. Existing rows keep
 * their ids, so attempts that already reference them stay valid; removed ones are soft-deleted.
 * Ids that do not belong to this quiz are ignored and treated as new, so a tampered form cannot
 * reach into another quiz.
 */
class QuestionSetSaver
{
    /**
     * @param  list<array<string, mixed>>  $items  validated questions, in display order
     */
    public function save(Quiz $quiz, array $items): void
    {
        DB::transaction(function () use ($quiz, $items) {
            $existing = $quiz->questions()->with('options')->get()->keyBy('id');
            $kept = [];

            foreach (array_values($items) as $position => $item) {
                $question = isset($item['id']) ? $existing->get((int) $item['id']) : null;

                $attributes = [
                    'type' => $item['type'],
                    'body' => trim($item['body']),
                    'explanation' => filled($item['explanation'] ?? null) ? trim($item['explanation']) : null,
                    'points' => (int) $item['points'],
                    'position' => $position + 1,
                ];

                if ($question) {
                    $question->update($attributes);
                } else {
                    $question = $quiz->questions()->create($attributes);
                    $question->setRelation('options', collect());
                }

                $kept[] = $question->id;
                $this->syncOptions($question, $item);
            }

            $quiz->questions()->whereNotIn('id', $kept)->get()->each->delete();
        });
    }

    /** @param  array<string, mixed>  $item */
    private function syncOptions(Question $question, array $item): void
    {
        $type = QuestionType::from($item['type']);
        $correct = (int) $item['correct'];

        $desired = $type === QuestionType::TrueFalse
            ? [
                ['id' => null, 'body' => __('enums.true_false.true'), 'correct' => $correct === 0],
                ['id' => null, 'body' => __('enums.true_false.false'), 'correct' => $correct === 1],
            ]
            : collect($item['options'])->values()->map(fn (array $option, int $index) => [
                'id' => $option['id'] ?? null,
                'body' => trim($option['body']),
                'correct' => $index === $correct,
            ])->all();

        $current = $question->options()->get();
        $byId = $current->keyBy('id');

        // True/false reuses the first two rows whatever their ids, so a type change loses nothing.
        $reuse = $current->values();

        // The database allows one correct option per question, so clear the flag before setting it.
        $question->options()->update(['is_correct' => false]);

        $kept = [];

        foreach ($desired as $position => $option) {
            $row = $type === QuestionType::TrueFalse
                ? $reuse->get($position)
                : (isset($option['id']) ? $byId->get((int) $option['id']) : null);

            $attributes = ['body' => $option['body'], 'is_correct' => $option['correct'], 'position' => $position + 1];

            if ($row instanceof QuestionOption) {
                $row->update($attributes);
            } else {
                $row = $question->options()->create($attributes);
            }

            $kept[] = $row->id;
        }

        $question->options()->whereNotIn('id', $kept)->get()->each->delete();
    }
}
