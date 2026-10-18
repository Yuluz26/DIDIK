<?php

namespace App\Services\QuizEngine\Exceptions;

/** The visitor has already used every attempt the quiz allows. */
class AttemptsExhausted extends QuizEngineException {}
