<?php

namespace App\Services\Stats;

use App\Enums\QuizStatus;
use App\Models\Attempt;
use App\Models\Quiz;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/**
 * Numbers for the admin dashboard and the per-quiz statistics page. Everything here is
 * aggregate: attempts are anonymous, so there is no individual child to look at.
 */
class QuizStatistics
{
    /** A question needs this many answers before it is called "hard": fewer would be noise. */
    public const MIN_ANSWERS = 5;

    /**
     * @return array{published: int, drafts: int, started_week: int, completed_week: int, average_percent: ?float}
     */
    public function overview(): array
    {
        $since = now()->subDays(7);

        $average = Attempt::query()
            ->whereNotNull('completed_at')
            ->where('completed_at', '>=', $since)
            ->where('max_score', '>', 0)
            ->selectRaw('avg(score * 100.0 / max_score) as percent')
            ->value('percent');

        return [
            'published' => Quiz::where('status', QuizStatus::Published)->count(),
            'drafts' => Quiz::where('status', QuizStatus::Draft)->count(),
            'started_week' => Attempt::where('started_at', '>=', $since)->count(),
            'completed_week' => Attempt::where('completed_at', '>=', $since)->count(),
            'average_percent' => $average === null ? null : round((float) $average, 1),
        ];
    }

    /**
     * Published quizzes that cannot be played properly (for example every question was deleted
     * after publishing), and drafts that are complete and could go live.
     *
     * @return array{broken: Collection<int, array{quiz: Quiz, problems: list<string>}>, ready: Collection<int, Quiz>}
     */
    public function attention(int $limit = 5): array
    {
        $quizzes = Quiz::query()
            ->whereIn('status', [QuizStatus::Published, QuizStatus::Draft])
            ->with('questions.options')
            ->orderByDesc('updated_at')
            ->limit(200)
            ->get();

        $broken = collect();
        $ready = collect();

        foreach ($quizzes as $quiz) {
            $problems = $quiz->publishingProblems();

            if ($quiz->status === QuizStatus::Published && $problems !== []) {
                $broken->push(['quiz' => $quiz, 'problems' => $problems]);
            }

            if ($quiz->status === QuizStatus::Draft && $problems === []) {
                $ready->push($quiz);
            }
        }

        return ['broken' => $broken->take($limit)->values(), 'ready' => $ready->take($limit)->values()];
    }

    /** @return Collection<int, object{id: int, body: string, quiz_id: int, title: string, answers: int, correct: int, percent: float}> */
    public function hardestQuestions(int $limit = 5): Collection
    {
        return DB::table('attempt_answers as answers')
            ->join('questions', 'questions.id', '=', 'answers.question_id')
            ->join('quizzes', 'quizzes.id', '=', 'questions.quiz_id')
            ->whereNull('questions.deleted_at')
            ->groupBy('questions.id', 'questions.body', 'quizzes.id', 'quizzes.title')
            ->havingRaw('count(*) >= ?', [self::MIN_ANSWERS])
            ->orderByRaw('sum(answers.is_correct) * 1.0 / count(*) asc')
            ->limit($limit)
            ->get([
                'questions.id as id',
                'questions.body as body',
                'quizzes.id as quiz_id',
                'quizzes.title as title',
                DB::raw('count(*) as answers'),
                DB::raw('sum(answers.is_correct) as correct'),
            ])
            ->map(function ($row) {
                $row->answers = (int) $row->answers;
                $row->correct = (int) $row->correct;
                $row->percent = round($row->correct * 100 / $row->answers, 1);

                return $row;
            });
    }

    /**
     * @return array{started: int, completed: int, completion_percent: ?float, average_percent: ?float, questions: Collection<int, array<string, mixed>>}
     */
    public function forQuiz(Quiz $quiz): array
    {
        $started = $quiz->attempts()->count();
        $completed = $quiz->attempts()->whereNotNull('completed_at')->count();

        $average = $quiz->attempts()
            ->whereNotNull('completed_at')
            ->where('max_score', '>', 0)
            ->selectRaw('avg(score * 100.0 / max_score) as percent')
            ->value('percent');

        $perQuestion = DB::table('attempt_answers as answers')
            ->join('attempts', 'attempts.id', '=', 'answers.attempt_id')
            ->where('attempts.quiz_id', $quiz->id)
            ->groupBy('answers.question_id')
            ->get([
                'answers.question_id as question_id',
                DB::raw('count(*) as answers'),
                DB::raw('sum(answers.is_correct) as correct'),
            ])
            ->keyBy('question_id');

        $questions = $quiz->questions()->get()->values()->map(function ($question, int $index) use ($perQuestion) {
            $row = $perQuestion->get($question->id);
            $answers = (int) ($row->answers ?? 0);
            $correct = (int) ($row->correct ?? 0);

            return [
                'number' => $index + 1,
                'body' => $question->body,
                'answers' => $answers,
                'correct' => $correct,
                'percent' => $answers > 0 ? round($correct * 100 / $answers, 1) : null,
                'enough' => $answers >= self::MIN_ANSWERS,
            ];
        });

        return [
            'started' => $started,
            'completed' => $completed,
            'completion_percent' => $started > 0 ? round($completed * 100 / $started, 1) : null,
            'average_percent' => $average === null ? null : round((float) $average, 1),
            'questions' => $questions,
        ];
    }
}
