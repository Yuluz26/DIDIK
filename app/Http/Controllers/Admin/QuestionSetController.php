<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\QuestionSetRequest;
use App\Models\Quiz;
use App\Services\Admin\QuestionSetSaver;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;

class QuestionSetController extends Controller
{
    public function edit(Quiz $quiz): View
    {
        $quiz->load('questions.options');

        // The editor works on plain data: the correct option is an index into the option list.
        $questions = $quiz->questions->map(fn ($question) => [
            'id' => $question->id,
            'type' => $question->type->value,
            'body' => $question->body,
            'explanation' => $question->explanation ?? '',
            'points' => $question->points,
            'correct' => max(0, $question->options->search(fn ($option) => $option->is_correct)),
            'options' => $question->options->map(fn ($option) => ['id' => $option->id, 'body' => $option->body])->values()->all(),
        ])->values()->all();

        return view('admin.questions.edit', [
            'quiz' => $quiz,
            'questions' => $questions,
            'maxQuestions' => QuestionSetRequest::MAX_QUESTIONS,
        ]);
    }

    public function update(QuestionSetRequest $request, Quiz $quiz, QuestionSetSaver $saver): RedirectResponse
    {
        $saver->save($quiz, $request->questions());

        return redirect()->route('admin.quizzes.questions.edit', $quiz)->with('status', __('editor.saved'));
    }
}
