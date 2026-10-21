<?php

use Illuminate\Support\Facades\Schedule;

/*
| Scheduled work. The host runs `php artisan schedule:run` every minute (one cron entry).
| The retention rule on the privacy page is carried out here: nothing about a child's play is kept
| longer than DIDIK_RETENTION_DAYS.
*/
Schedule::command('didik:prune')->dailyAt('03:30')->withoutOverlapping();
