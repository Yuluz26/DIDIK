<?php

namespace App\Http\Controllers\Site;

use App\Http\Controllers\Controller;
use App\Models\Attempt;
use App\Services\QuizEngine\AttemptService;
use App\Support\SessionFingerprint;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;

class ResultController extends Controller
{
    public function __invoke(Request $request, Attempt $attempt, AttemptService $engine): View|RedirectResponse|Response
    {
        // Only the device that played can read the review: it contains every right answer.
        if (! SessionFingerprint::matches($attempt->session_hash, $request)) {
            return response()->view('pages.results.private', [], 404);
        }

        $quiz = $attempt->quiz()->withTrashed()->with(['category.parent', 'level'])->firstOrFail();

        if (! $attempt->isCompleted()) {
            return $quiz->isAvailable()
                ? redirect()->route('quizzes.play', $quiz->slug)
                : response()->view('pages.results.private', [], 404);
        }

        $hash = SessionFingerprint::for($request);

        return view('pages.results.show', [
            'attempt' => $attempt,
            'quiz' => $quiz,
            'review' => $engine->review($attempt),
            'remaining' => $quiz->isAvailable() ? $engine->attemptsRemaining($quiz, $hash) : 0,
            'canReplay' => $quiz->isAvailable() && $engine->attemptsRemaining($quiz, $hash) !== 0,
        ]);
    }
}
