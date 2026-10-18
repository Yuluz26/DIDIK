<?php

namespace App\Http\Controllers\Site;

use App\Enums\FeedbackMode;
use App\Http\Controllers\Controller;
use App\Models\Attempt;
use App\Models\Quiz;
use App\Services\QuizEngine\AttemptService;
use App\Services\QuizEngine\Exceptions\AlreadyAnswered;
use App\Services\QuizEngine\Exceptions\AttemptClosed;
use App\Services\QuizEngine\Exceptions\AttemptsExhausted;
use App\Services\QuizEngine\Exceptions\InvalidAnswer;
use App\Services\QuizEngine\Exceptions\QuizUnavailable;
use App\Support\SessionFingerprint;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

/** JSON endpoints the quiz player talks to. */
class AttemptController extends Controller
{
    public function __construct(private readonly AttemptService $engine) {}

    public function start(Request $request, Quiz $publicQuiz): JsonResponse
    {
        try {
            $attempt = $this->engine->startOrResume(
                $publicQuiz,
                SessionFingerprint::for($request),
                restart: $request->boolean('restart'),
            );
        } catch (AttemptsExhausted) {
            return response()->json(['code' => 'exhausted', 'message' => __('public.player.exhausted_title')], 403);
        } catch (QuizUnavailable) {
            return response()->json(['code' => 'unavailable', 'message' => __('public.player.unavailable_title')], 404);
        }

        $state = $this->engine->playerState($attempt);

        return response()->json([
            ...$state,
            // An empty PHP array would encode as [], which the player would then treat as a list.
            'answers' => (object) $state['answers'],
            'urls' => [
                'answer' => route('attempts.answer', $attempt),
                'result' => route('results.show', $attempt),
            ],
        ]);
    }

    public function answer(Request $request, Attempt $attempt): JsonResponse
    {
        abort_unless(SessionFingerprint::matches($attempt->session_hash, $request), 404);

        $attempt->loadMissing('quiz');

        $data = $request->validate([
            'question_id' => ['required', 'integer'],
            'option_id' => ['required', 'integer'],
        ]);

        try {
            $result = $this->engine->answer($attempt, (int) $data['question_id'], (int) $data['option_id']);
        } catch (InvalidAnswer) {
            return response()->json(['code' => 'invalid'], 422);
        } catch (AlreadyAnswered) {
            return response()->json(['code' => 'answered'], 409);
        } catch (AttemptClosed) {
            return response()->json(['code' => 'closed', 'result_url' => route('results.show', $attempt)], 409);
        }

        $payload = [
            'recorded' => true,
            'answered' => $result->answered,
            'total' => $result->total,
            'finished' => $result->finished,
            'result_url' => $result->finished ? route('results.show', $attempt) : null,
        ];

        // In "feedback at the end" mode nothing about correctness leaves the server until the review.
        if ($attempt->quiz->feedback_mode === FeedbackMode::Instant) {
            $payload += [
                'correct' => $result->correct,
                'correct_option_id' => $result->correctOptionId,
                'explanation' => $result->explanation,
                'score' => $result->score,
            ];
        }

        return response()->json($payload);
    }
}
