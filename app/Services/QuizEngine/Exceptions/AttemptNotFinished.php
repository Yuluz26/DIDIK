<?php

namespace App\Services\QuizEngine\Exceptions;

/** A result or review was requested before the attempt was completed. */
class AttemptNotFinished extends QuizEngineException {}
