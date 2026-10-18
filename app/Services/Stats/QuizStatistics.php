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

    /** How far back "hardest questions" looks, counted in answers. */
    public const RECENT_ANSWERS = 50000;

    public function __construct(private readonly int $recentAnswers = self::RECENT_ANSWERS) {}

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
     * Health is decided by one aggregate query over questions and options, not by loading every
     * quiz with all its questions and options (about 20,000 models for a few hundred quizzes). Only
     * the handful that are listed are loaded in full, to name their problems. The rule is the same
     * as Quiz::publishingProblems(); a test keeps the two in step.
     *
     * @return array{broken: Collection<int, array{quiz: Quiz, problems: list<string>}>, ready: Collection<int, Quiz>}
     */
    public function attention(int $limit = 5): array
    {
        $health = $this->questionHealth();
        $broken = collect();
        $ready = collect();

        $quizzes = Quiz::query()
            ->whereIn('status', [QuizStatus::Published, QuizStatus::Draft])
            ->orderByDesc('updated_at')
            ->lazy(200);

        foreach ($quizzes as $quiz) {
            $row = $health->get($quiz->id);
            $hasProblems = $row === null || (int) $row->broken > 0;   // no questions at all, or one that cannot be answered

            if ($quiz->status === QuizStatus::Published && $hasProblems && $broken->count() < $limit) {
                $broken->push(['quiz' => $quiz, 'problems' => $quiz->publishingProblems()]);
            } elseif ($quiz->status === QuizStatus::Draft && ! $hasProblems && $ready->count() < $limit) {
                $ready->push($quiz);
            }

            if ($broken->count() >= $limit && $ready->count() >= $limit) {
                break;
            }
        }

        return ['broken' => $broken->values(), 'ready' => $ready->values()];
    }

    /**
     * Per quiz: how many live questions it has and how many of them cannot be answered properly
     * (fewer than two live options, or not exactly one marked correct). Quizzes without questions
     * have no row.
     *
     * @return Collection<int, object{quiz_id: int, questions: int, broken: int}>
     */
    private function questionHealth(): Collection
    {
        $options = DB::table('question_options')
            ->whereNull('deleted_at')
            ->groupBy('question_id')
            ->select('question_id', DB::raw('count(*) as option_count'), DB::raw('sum(is_correct) as correct_count'));

        return DB::table('questions')
            ->leftJoinSub($options, 'o', 'o.question_id', '=', 'questions.id')
            ->whereNull('questions.deleted_at')
            ->groupBy('questions.quiz_id')
            ->select(
                'questions.quiz_id',
                DB::raw('count(*) as questions'),
                DB::raw('sum(case when coalesce(o.option_count, 0) < 2 or coalesce(o.correct_count, 0) <> 1 then 1 else 0 end) as broken'),
            )
            ->get()
            ->keyBy('quiz_id');
    }

    /**
     * The questions children get wrong most often, among the most recent answers.
     *
     * Counting every answer ever given is a scan of the biggest table (seven seconds for a million
     * and a half rows), and old answers say little about a question that has been reworded since.
     * Looking at the latest answers only (RECENT_ANSWERS rows), read through the primary key, keeps the cost the
     * same however long the site has been running.
     *
     * @return Collection<int, object{id: int, body: string, quiz_id: int, title: string, answers: int, correct: int, percent: float}>
     */
    public function hardestQuestions(int $limit = 5): Collection
    {
        // The window is taken first, as its own small table, so the join starts from it and not from every question.
        $recent = DB::table('attempt_answers')
            ->orderByDesc('id')
            ->limit($this->recentAnswers)
            ->select('question_id', 'is_correct');

        return DB::query()
            ->fromSub($recent, 'answers')
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
