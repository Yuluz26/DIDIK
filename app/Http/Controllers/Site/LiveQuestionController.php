<?php

namespace App\Http\Controllers\Site;

use App\Http\Controllers\Controller;
use App\Services\LiveQuestion;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class LiveQuestionController extends Controller
{
    public function __invoke(Request $request, LiveQuestion $live): JsonResponse
    {
        $data = $request->validate([
            'question_id' => ['required', 'integer'],
            'option_id' => ['required', 'integer'],
        ]);

        $result = $live->check((int) $data['question_id'], (int) $data['option_id']);

        abort_if($result === null, 404);

        return response()->json($result);
    }
}
