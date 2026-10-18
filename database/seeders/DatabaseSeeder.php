<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed the application's database.
     *
     * Reference data (school levels, core subjects) is needed everywhere. Demo content is
     * only added for local development and tests, never in production or staging.
     * The admin account is created with `php artisan didik:admin`, not here.
     */
    public function run(): void
    {
        $this->call(ReferenceDataSeeder::class);

        if (app()->environment(['local', 'testing'])) {
            $this->call(DemoContentSeeder::class);
        }
    }
}
