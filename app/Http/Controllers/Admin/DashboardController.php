<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Quiz;
use App\Services\Stats\QuizStatistics;
use Illuminate\Contracts\View\View;

class DashboardController extends Controller
{
    public function __invoke(QuizStatistics $stats): View
    {
        return view('admin.dashboard', [
            'overview' => $stats->overview(),
            'attention' => $stats->attention(),
            'hardest' => $stats->hardestQuestions(),
            'hasQuizzes' => Quiz::exists(),
            'minAnswers' => QuizStatistics::MIN_ANSWERS,
        ]);
    }
}
