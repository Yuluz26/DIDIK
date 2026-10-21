<?php

namespace App\Providers;

use App\Games\GameConceptRegistry;
use App\Games\QuestionAnswer;
use App\Games\RiverQuest;
use App\Games\StarCollector;
use App\Models\Quiz;
use App\Support\ClientKey;
use App\Support\PrivateSessionHandler;
use App\Support\SessionFingerprint;
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Http\Request;
use Illuminate\Pagination\Paginator;
use Illuminate\Support\Facades\Blade;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Session;
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

        // Sessions are stored without the visitor's IP address and browser string (see the class).
        Session::extend('database', fn ($app) => new PrivateSessionHandler(
            DB::connection(config('session.connection')),
            config('session.table'),
            config('session.lifetime'),
            $app,
        ));

        // The site is served over HTTPS in production; links and redirects must say so even when TLS
        // ends at a proxy that does not forward the scheme.
        if (str_starts_with((string) config('app.url'), 'https://')) {
            URL::forceScheme('https');
        }

        $this->limitRequests();
    }

    /**
     * Each limit is counted twice: per visitor (their session) and per network address. The address
     * alone punishes a classroom or a family behind one router (thirty children answering at once would
     * use up a per-address limit in seconds); the session alone is dodged by dropping the cookie.
     */
    private function limitRequests(): void
    {
        $visitor = fn (Request $request) => 'visitor:'.SessionFingerprint::for($request);
        $network = fn (Request $request) => 'network:'.ClientKey::address($request);

        RateLimiter::for('web', fn (Request $request) => Limit::perMinute(600)->by($network($request)));
        RateLimiter::for('attempts', fn (Request $request) => [
            Limit::perMinute(20)->by($visitor($request)),
            Limit::perMinute(300)->by($network($request)),
        ]);
        RateLimiter::for('answers', fn (Request $request) => [
            Limit::perMinute(90)->by($visitor($request)),
            Limit::perMinute(1200)->by($network($request)),
        ]);
        RateLimiter::for('login', fn (Request $request) => Limit::perMinute(20)->by($network($request)));
    }
}
