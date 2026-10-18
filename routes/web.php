<?php

use App\Http\Controllers\Site\AttemptController;
use App\Http\Controllers\Site\HomeController;
use App\Http\Controllers\Site\LiveQuestionController;
use App\Http\Controllers\Site\PageController;
use App\Http\Controllers\Site\QuizController;
use App\Http\Controllers\Site\QuizizzController;
use App\Http\Controllers\Site\ResultController;
use Illuminate\Support\Facades\Route;

/*
| Public site. URLs are in Bahasa Melayu; route names are in English.
| `publicQuiz` only resolves quizzes that are published and inside their availability window
| (see AppServiceProvider), so drafts and archived quizzes are a plain 404.
*/

Route::get('/', HomeController::class)->name('home');

Route::get('/kuiz', [QuizController::class, 'index'])->name('quizzes.index');
Route::get('/kuiz/{publicQuiz}', [QuizController::class, 'show'])->name('quizzes.show');
Route::get('/kuiz/{publicQuiz}/main', [QuizController::class, 'play'])->name('quizzes.play');

Route::post('/kuiz/{publicQuiz}/percubaan', [AttemptController::class, 'start'])
    ->middleware('throttle:attempts')
    ->name('attempts.start');
Route::post('/percubaan/{attempt}/jawapan', [AttemptController::class, 'answer'])
    ->middleware('throttle:answers')
    ->name('attempts.answer');
Route::get('/keputusan/{attempt}', ResultController::class)->name('results.show');

Route::post('/soalan-pantas', LiveQuestionController::class)
    ->middleware('throttle:answers')
    ->name('live.answer');

Route::get('/pautan-quizizz', [QuizizzController::class, 'index'])->name('quizizz.index');
Route::get('/pautan-quizizz/{collection:slug}', [QuizizzController::class, 'show'])->name('quizizz.show');

Route::get('/tentang', [PageController::class, 'about'])->name('pages.about');
Route::get('/privasi', [PageController::class, 'privacy'])->name('pages.privacy');
