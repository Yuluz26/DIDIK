<?php

namespace App\Providers;

use App\Games\GameConceptRegistry;
use App\Games\QuestionAnswer;
use App\Games\RiverQuest;
use App\Games\StarCollector;
use App\Models\Quiz;
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Http\Request;
use Illuminate\Pagination\Paginator;
use Illuminate\Support\Facades\Blade;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     */
    public function register(): void
    {
        $this->app->singleton(GameConceptRegistry::class, fn () => new GameConceptRegistry(
            new QuestionAnswer,
            new StarCollector,
            new RiverQuest,
        ));
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        // Fail loudly in development and tests on N+1 queries, silently dropped attributes
        // and reads of attributes that were never loaded. Production stays forgiving.
        Model::shouldBeStrict(! $this->app->isProduction());

        Paginator::defaultView('pagination.didik');

        // Data for an Alpine component, written as a plain object literal inside the attribute. Alpine's
        // CSP build has no JSON in scope, so the usual @js() (which emits JSON.parse(...)) cannot be used.
        Blade::directive('literal', fn (string $expression) => "<?php echo e(json_encode({$expression}, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_THROW_ON_ERROR)); ?>");

        // Admin URLs read in Bahasa Melayu: /admin/kuiz/baharu, /admin/kuiz/1/sunting.
        Route::resourceVerbs(['create' => 'baharu', 'edit' => 'sunting']);

        // The public face of a quiz: only published quizzes inside their availability window.
        Route::bind('publicQuiz', fn (string $slug) => Quiz::available()->where('slug', $slug)->firstOrFail());

        RateLimiter::for('attempts', fn (Request $request) => Limit::perMinute(30)->by($request->ip()));
        RateLimiter::for('answers', fn (Request $request) => Limit::perMinute(120)->by($request->ip()));
    }
}
