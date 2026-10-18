<?php

use App\Http\Controllers\Admin\AuthController;
use App\Http\Controllers\Admin\CategoryController;
use App\Http\Controllers\Admin\DashboardController;
use App\Http\Controllers\Admin\QuestionSetController;
use App\Http\Controllers\Admin\QuizController;
use App\Http\Controllers\Admin\QuizizzCollectionController;
use App\Http\Controllers\Admin\QuizizzLinkController;
use App\Http\Controllers\Admin\QuizStatsController;
use Illuminate\Support\Facades\Route;

/*
| Administration. Loaded under /admin with the `admin.` name prefix (see bootstrap/app.php).
| Every route except sign-in sits behind `auth` and `admin`, which is enforced on the server:
| hiding a link in the interface is never the protection.
*/

Route::middleware('guest')->group(function () {
    Route::get('log-masuk', [AuthController::class, 'create'])->name('login');
    Route::post('log-masuk', [AuthController::class, 'store'])->name('login.store');
});

Route::middleware(['auth', 'admin'])->group(function () {
    Route::post('log-keluar', [AuthController::class, 'destroy'])->name('logout');

    Route::get('/', DashboardController::class)->name('dashboard');

    Route::resource('kategori', CategoryController::class)
        ->parameters(['kategori' => 'category'])->names('categories')->except('show');

    Route::resource('kuiz', QuizController::class)
        ->parameters(['kuiz' => 'quiz'])->names('quizzes')->except('show');
    Route::post('kuiz/{quiz}/terbit', [QuizController::class, 'publish'])->name('quizzes.publish');
    Route::post('kuiz/{quiz}/draf', [QuizController::class, 'unpublish'])->name('quizzes.unpublish');
    Route::post('kuiz/{quiz}/arkib', [QuizController::class, 'archive'])->name('quizzes.archive');
    Route::post('kuiz/{quiz}/salin', [QuizController::class, 'duplicate'])->name('quizzes.duplicate');
    Route::get('kuiz/{quiz}/soalan', [QuestionSetController::class, 'edit'])->name('quizzes.questions.edit');
    Route::put('kuiz/{quiz}/soalan', [QuestionSetController::class, 'update'])->name('quizzes.questions.update');
    Route::get('kuiz/{quiz}/statistik', QuizStatsController::class)->name('quizzes.stats');

    Route::resource('pautan-quizizz', QuizizzLinkController::class)
        ->parameters(['pautan-quizizz' => 'link'])->names('links')->except('show');

    Route::resource('koleksi-quizizz', QuizizzCollectionController::class)
        ->parameters(['koleksi-quizizz' => 'collection'])->names('collections')->except('show');
});
