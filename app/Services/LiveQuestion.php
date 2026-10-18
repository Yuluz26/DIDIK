<?php

namespace App\Services;

use App\Enums\QuestionType;
use App\Models\Question;
use App\Models\Quiz;
use Carbon\CarbonInterface;
use Illuminate\Support\Facades\Cache;

/**
 * The homepage's "try one question". Picks one real single-answer question from an available
 * quiz, the same one all day, and checks answers on the server like the quizzes do.
 *
 * The check endpoint is open to anyone, so it answers for the featured questions only (today's, and
 * yesterday's for a child who loaded the page just before midnight). Answering for any question id
 * would let it be used to read the correct answers out of the whole question bank, and out of quizzes
 * that hold their feedback back until the end.
 */
class LiveQuestion
{
    private const MAX_OPTION_LENGTH = 30;

    private const MAX_BODY_LENGTH = 140;

    private const CACHE_PREFIX = 'live-question:';

    /** @return array{question_id: int, body: string, options: list<array{id: int, body: string}>, quiz: Quiz}|null */
    public function today(): ?array
    {
        $question = $this->featured(now());

        if (! $question) {
            return null;
        }

        return [
            'question_id' => $question->id,
            'body' => $question->body,
            'options' => $question->options->map(fn ($option) => ['id' => $option->id, 'body' => $option->body])->all(),
            'quiz' => $question->quiz,
        ];
    }

    /** @return array{correct: bool, correct_option_id: int, explanation: ?string}|null null when this is not a featured, publicly available question */
    public function check(int $questionId, int $optionId): ?array
    {
        $featured = array_filter([$this->featuredId(now()), $this->featuredId(now()->subDay())]);

        if (! in_array($questionId, $featured, true)) {
            return null;
        }

        $question = $this->available($questionId);
        $option = $question?->options->firstWhere('id', $optionId);
        $correct = $question?->options->firstWhere('is_correct', true);

        if (! $option || ! $correct) {
            return null;
        }

        return [
            'correct' => $option->is_correct,
            'correct_option_id' => $correct->id,
            'explanation' => $question->explanation,
        ];
    }

    /** The featured question for a day, as long as it is still available and still fits the stones. */
    private function featured(CarbonInterface $day): ?Question
    {
        $id = $this->featuredId($day);
        $question = $id ? $this->available($id) : null;

        if ($id && (! $question || ! $this->fitsTheStones($question))) {
            // It was edited or taken down since it was picked: choose again rather than show a broken one.
            Cache::forget($this->key($day));
            $question = ($id = $this->featuredId($day)) ? $this->available($id) : null;
        }

        return $question;
    }

    /** Chosen once per day and remembered, so it does not change as content is added during the day. */
    private function featuredId(CarbonInterface $day): ?int
    {
        return Cache::remember($this->key($day), now()->addDays(2), fn () => $this->choose($day)?->id);
    }

    private function choose(CarbonInterface $day): ?Question
    {
        $ids = Question::query()
            ->where('type', QuestionType::Single)
            ->whereHas('quiz', fn ($quiz) => $quiz->available())
            ->pluck('id')
            ->sortBy(fn (int $id) => crc32($day->toDateString().'|'.$id))
            ->take(12);

        foreach ($ids as $id) {
            $question = $this->available($id);

            if ($question && $this->fitsTheStones($question)) {
                return $question;
            }
        }

        return null;
    }

    private function available(int $id): ?Question
    {
        return Question::with(['options', 'quiz'])
            ->where('type', QuestionType::Single)
            ->whereHas('quiz', fn ($quiz) => $quiz->available())
            ->find($id);
    }

    private function key(CarbonInterface $day): string
    {
        return self::CACHE_PREFIX.$day->toDateString();
    }

    private function fitsTheStones(Question $question): bool
    {
        $options = $question->options;

        return $options->count() >= 2
            && $options->count() <= 4
            && $options->where('is_correct', true)->count() === 1
            && mb_strlen($question->body) <= self::MAX_BODY_LENGTH
            && $options->every(fn ($option) => mb_strlen($option->body) <= self::MAX_OPTION_LENGTH);
    }
}
