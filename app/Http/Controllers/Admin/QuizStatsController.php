<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Quiz;
use App\Services\Stats\QuizStatistics;
use Illuminate\Contracts\View\View;

class QuizStatsController extends Controller
{
    public function __invoke(Quiz $quiz, QuizStatistics $stats): View
    {
        return view('admin.quizzes.stats', [
            'quiz' => $quiz,
            'stats' => $stats->forQuiz($quiz),
            'minAnswers' => QuizStatistics::MIN_ANSWERS,
        ]);
    }
}
