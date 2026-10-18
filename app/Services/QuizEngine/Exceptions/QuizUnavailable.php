<?php

namespace App\Services\QuizEngine\Exceptions;

/** The quiz is not published, not inside its availability window, or has no playable question. */
class QuizUnavailable extends QuizEngineException {}
