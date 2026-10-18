<?php

namespace App\Http\Controllers\Site;

use App\Http\Controllers\Controller;
use App\Models\Quiz;
use App\Services\Catalog;
use App\Services\QuizEngine\AttemptService;
use App\Support\SessionFingerprint;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class QuizController extends Controller
{
    public function index(Request $request, Catalog $catalog): View
    {
        return view('pages.quizzes.index', [
            ...$catalog->browse($request),
            'subjects' => $catalog->subjects(),
            'levels' => $catalog->levels(),
        ]);
    }

    public function show(Request $request, Quiz $publicQuiz, AttemptService $engine): View
    {
        $quiz = $publicQuiz->load(['category.parent', 'level', 'tags'])->loadCount('questions');
        $hash = SessionFingerprint::for($request);

        return view('pages.quizzes.show', [
            'quiz' => $quiz,
            'concept' => $quiz->concept(),
            'remaining' => $engine->attemptsRemaining($quiz, $hash),
            'resumable' => $engine->resumable($quiz, $hash) !== null,
            'lastResult' => $engine->lastFinished($quiz, $hash),
        ]);
    }

    public function play(Request $request, Quiz $publicQuiz, AttemptService $engine): View|RedirectResponse
    {
        $quiz = $publicQuiz;
        $hash = SessionFingerprint::for($request);

        // Out of attempts and nothing to resume: the introduction explains it, the player cannot.
        if ($engine->attemptsRemaining($quiz, $hash) === 0 && $engine->resumable($quiz, $hash) === null) {
            return redirect()->route('quizzes.show', $quiz->slug);
        }

        $concept = $quiz->concept();

        return view('pages.quizzes.play', [
            'quiz' => $quiz,
            'concept' => $concept,
            'settings' => $concept->normalize($quiz->game_settings ?? []),
        ]);
    }
}
