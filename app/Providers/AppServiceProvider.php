<?php

namespace App\Providers;

use App\Games\GameConceptRegistry;
use App\Games\QuestionAnswer;
use App\Games\RiverQuest;
use App\Games\StarCollector;
use Illuminate\Database\Eloquent\Model;
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
    }
}
