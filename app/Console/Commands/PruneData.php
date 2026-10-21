<?php

namespace App\Console\Commands;

use App\Models\Attempt;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Support\Facades\DB;

/**
 * The retention rule behind the privacy page: quiz attempts (and the answers inside them) are kept
 * for DIDIK_RETENTION_DAYS and then deleted, and expired sessions are cleared out too. Runs daily
 * from the scheduler (see routes/console.php), so the host needs the usual
 * `* * * * * php artisan schedule:run` cron entry.
 */
#[Signature('didik:prune {--days= : Keep attempts this many days (default: DIDIK_RETENTION_DAYS)} {--dry-run : Only count what would be deleted}')]
#[Description('Delete quiz attempts older than the retention period, and expired sessions')]
class PruneData extends Command
{
    /** Attempts are removed in small batches: each takes its answers with it, so one huge delete would lock for long. */
    private const BATCH = 1000;

    public function handle(): int
    {
        $days = (int) ($this->option('days') ?: config('didik.retention_days'));

        if ($days < 1) {
            $this->components->error('Tempoh simpanan mestilah sekurang-kurangnya 1 hari.');

            return self::FAILURE;
        }

        $dry = (bool) $this->option('dry-run');
        $cutoff = now()->subDays($days);

        $attempts = $this->pruneAttempts(Attempt::query()->where('started_at', '<', $cutoff), $dry);
        $sessions = $this->pruneSessions($dry);

        $verb = $dry ? 'akan dipadam' : 'dipadam';
        $this->components->info("Percubaan lebih {$days} hari {$verb}: {$attempts}. Sesi tamat tempoh {$verb}: {$sessions}.");

        return self::SUCCESS;
    }

    /** @param  Builder<Attempt>  $old */
    private function pruneAttempts(Builder $old, bool $dry): int
    {
        if ($dry) {
            return $old->count();
        }

        $deleted = 0;

        do {
            $ids = (clone $old)->orderBy('id')->limit(self::BATCH)->pluck('id');

            // The answers go with their attempt (cascading foreign key).
            Attempt::whereIn('id', $ids)->delete();
            $deleted += $ids->count();
        } while ($ids->count() === self::BATCH);

        return $deleted;
    }

    private function pruneSessions(bool $dry): int
    {
        if (config('session.driver') !== 'database') {
            return 0;
        }

        $expired = DB::table(config('session.table'))
            ->where('last_activity', '<', now()->subMinutes((int) config('session.lifetime'))->getTimestamp());

        return $dry ? $expired->count() : $expired->delete();
    }
}
