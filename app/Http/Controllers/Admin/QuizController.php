<?php

namespace App\Http\Controllers\Admin;

use App\Enums\Difficulty;
use App\Enums\FeedbackMode;
use App\Enums\QuizStatus;
use App\Games\GameConceptRegistry;
use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\QuizRequest;
use App\Models\Category;
use App\Models\Quiz;
use App\Models\SchoolLevel;
use App\Services\Admin\QuizWorkflow;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class QuizController extends Controller
{
    public function __construct(private readonly QuizWorkflow $workflow) {}

    public function index(Request $request): View
    {
        $search = trim($request->string('q')->limit(80)->toString());
        $status = QuizStatus::tryFrom($request->string('status')->toString());

        $quizzes = Quiz::query()
            ->with(['category.parent', 'level'])
            ->withCount(['questions', 'attempts'])
            ->when($status, fn ($q) => $q->where('status', $status))
            ->when($search !== '', function ($q) use ($search) {
                $like = '%'.addcslashes($search, '\\%_').'%';
                $q->where(fn ($w) => $w->where('title', 'like', $like)->orWhere('summary', 'like', $like));
            })
            ->orderByDesc('updated_at')
            ->paginate(20)
            ->withQueryString();

        return view('admin.quizzes.index', [
            'quizzes' => $quizzes,
            'search' => $search,
            'status' => $status,
        ]);
    }

    public function create(): View
    {
        return view('admin.quizzes.form', $this->formData(new Quiz([
            'language' => 'ms',
            'difficulty' => Difficulty::Medium,
            'status' => QuizStatus::Draft,
            'game_concept' => GameConceptRegistry::DEFAULT,
            'feedback_mode' => FeedbackMode::Instant,
            'shuffle_questions' => false,
            'shuffle_options' => false,
        ])));
    }

    public function store(QuizRequest $request): RedirectResponse
    {
        // A new quiz has no questions, so it always starts as a draft.
        $quiz = DB::transaction(function () use ($request) {
            $quiz = Quiz::create([
                ...$request->quizAttributes(),
                'status' => QuizStatus::Draft,
                'created_by' => $request->user()->id,
            ]);
            $quiz->syncTagNames($request->validated('tags'));

            return $quiz;
        });

        return redirect()->route('admin.quizzes.questions.edit', $quiz)->with('status', __('quizzes.created_next'));
    }

    public function edit(Quiz $quiz): View
    {
        return view('admin.quizzes.form', $this->formData($quiz->load('tags')->loadCount(['questions', 'attempts'])));
    }

    public function update(QuizRequest $request, Quiz $quiz): RedirectResponse
    {
        DB::transaction(function () use ($request, $quiz) {
            $quiz->update($request->quizAttributes());
            $quiz->syncTagNames($request->validated('tags'));

            $this->applyStatus($quiz, QuizStatus::from($request->validated('status', $quiz->status->value)));
        });

        return redirect()->route('admin.quizzes.edit', $quiz)->with('status', __('admin.common.saved'));
    }

    public function destroy(Quiz $quiz): RedirectResponse
    {
        $quiz->delete();

        return redirect()->route('admin.quizzes.index')->with('status', __('admin.common.deleted'));
    }

    public function publish(Quiz $quiz): RedirectResponse
    {
        $this->workflow->publish($quiz);

        return back()->with('status', __('quizzes.published_now'));
    }

    public function unpublish(Quiz $quiz): RedirectResponse
    {
        $this->workflow->unpublish($quiz);

        return back()->with('status', __('quizzes.unpublished_now'));
    }

    public function archive(Quiz $quiz): RedirectResponse
    {
        $this->workflow->archive($quiz);

        return back()->with('status', __('quizzes.archived_now'));
    }

    public function duplicate(Quiz $quiz): RedirectResponse
    {
        $copy = $this->workflow->duplicate($quiz);

        return redirect()->route('admin.quizzes.edit', $copy)->with('status', __('quizzes.duplicated'));
    }

    private function applyStatus(Quiz $quiz, QuizStatus $status): void
    {
        if ($status === $quiz->status) {
            return;
        }

        match ($status) {
            QuizStatus::Published => $this->workflow->publish($quiz),
            QuizStatus::Archived => $this->workflow->archive($quiz),
            QuizStatus::Draft => $this->workflow->unpublish($quiz),
        };
    }

    /** @return array<string, mixed> */
    private function formData(Quiz $quiz): array
    {
        return [
            'quiz' => $quiz,
            'subjects' => Category::subjects()->with('children')->get(),
            'levels' => SchoolLevel::orderBy('position')->get(),
            'concepts' => app(GameConceptRegistry::class)->all(),
        ];
    }
}
