<?php

namespace App\Console\Commands;

use App\Enums\UserRole;
use App\Models\User;
use Illuminate\Console\Attributes\Description;
use Illuminate\Console\Attributes\Signature;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Validator;

use function Laravel\Prompts\password;
use function Laravel\Prompts\text;

/**
 * Admin accounts are made here, on purpose, and never by a seeder: a seeded password would
 * exist in every environment, including production.
 */
#[Signature('didik:admin {--name= : Display name} {--email= : Login email} {--password= : Password (omit to be asked)}')]
#[Description('Create an administrator, or reset the password and role of an existing user')]
class CreateAdmin extends Command
{
    public function handle(): int
    {
        $name = $this->option('name') ?: text('Nama', required: true);
        $email = $this->option('email') ?: text('Emel', required: true);
        $secret = $this->option('password') ?: password('Kata laluan (sekurang-kurangnya 12 aksara)', required: true);

        $validator = Validator::make(
            ['name' => $name, 'email' => $email, 'password' => $secret],
            ['name' => 'required|string|max:120', 'email' => 'required|email|max:190', 'password' => 'required|string|min:12|max:200'],
        );

        if ($validator->fails()) {
            foreach ($validator->errors()->all() as $message) {
                $this->components->error($message);
            }

            return self::FAILURE;
        }

        $user = User::firstOrNew(['email' => $email]);
        $existing = $user->exists;

        $user->fill(['name' => $name, 'password' => $secret]);
        $user->role = UserRole::Admin;
        $user->email_verified_at ??= now();
        $user->save();

        $this->components->info($existing ? "Pentadbir {$email} dikemas kini." : "Pentadbir {$email} dicipta.");

        return self::SUCCESS;
    }
}
