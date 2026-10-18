<?php

namespace App\Services\QuizEngine\Exceptions;

use RuntimeException;

/**
 * Base class for every expected failure in the quiz engine. Controllers translate these
 * into friendly responses; they are never shown to a visitor as a stack trace.
 */
class QuizEngineException extends RuntimeException {}
