<?php

namespace Tests\Feature\Admin;

use App\Enums\UserRole;
use App\Models\User;
use Illuminate\Database\Eloquent\MassAssignmentException;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Facades\Route;
use Tests\TestCase;

class AdminAccessTest extends TestCase
{
    use RefreshDatabase;

    /** @return list<array{string, string}> method and URI of every admin route except sign-in */
    private function protectedRoutes(): array
    {
        $routes = [];

        foreach (Route::getRoutes() as $route) {
            $name = $route->getName();

            if (! str_starts_with((string) $name, 'admin.') || in_array($name, ['admin.login', 'admin.login.store'], true)) {
                continue;
            }

            $uri = '/'.preg_replace('/\{[^}]+\}/', '1', $route->uri());
            $routes[] = [collect($route->methods())->first(fn ($m) => ! in_array($m, ['HEAD'], true)), $uri];
        }

        return $routes;
    }

    public function test_there_are_admin_routes_to_protect(): void
    {
        // Guards the guard: if routing changes and this finds nothing, the tests below prove nothing.
        $this->assertGreaterThan(25, count($this->protectedRoutes()));
    }

    public function test_guests_are_sent_to_sign_in_from_every_admin_route(): void
    {
        foreach ($this->protectedRoutes() as [$method, $uri]) {
            $this->call($method, $uri)->assertRedirect(route('admin.login'));
        }
    }

    public function test_a_signed_in_user_without_the_admin_role_is_refused_everywhere(): void
    {
        $user = User::factory()->create();   // role is null: no privileges

        foreach ($this->protectedRoutes() as [$method, $uri]) {
            $this->actingAs($user)->call($method, $uri)->assertForbidden();
        }
    }

    public function test_an_admin_reaches_the_dashboard(): void
    {
        $this->actingAs(User::factory()->admin()->create())
            ->get(route('admin.dashboard'))
            ->assertOk()
            ->assertSee(__('admin.dashboard.title'));
    }

    public function test_admin_pages_are_not_indexed(): void
    {
        $robots = '<meta name="robots" content="noindex'; // sign-in says "noindex", the admin shell "noindex, nofollow"

        $this->get(route('admin.login'))->assertOk()->assertSee($robots, false);

        $this->actingAs(User::factory()->admin()->create())
            ->get(route('admin.dashboard'))
            ->assertSee($robots, false);
    }

    public function test_an_admin_can_sign_in_and_out(): void
    {
        $admin = User::factory()->admin()->create(['email' => 'yul@didik.test', 'password' => Hash::make('rahsia-panjang-123')]);

        $this->post(route('admin.login.store'), ['email' => 'yul@didik.test', 'password' => 'rahsia-panjang-123'])
            ->assertRedirect(route('admin.dashboard'));
        $this->assertAuthenticatedAs($admin);

        $this->post(route('admin.logout'))->assertRedirect(route('admin.login'));
        $this->assertGuest();
    }

    public function test_the_wrong_password_gets_one_generic_message(): void
    {
        User::factory()->admin()->create(['email' => 'yul@didik.test', 'password' => Hash::make('rahsia-panjang-123')]);

        $this->from(route('admin.login'))
            ->post(route('admin.login.store'), ['email' => 'yul@didik.test', 'password' => 'salah'])
            ->assertRedirect(route('admin.login'))
            ->assertSessionHasErrors(['email' => __('auth.failed')]);

        // An address that does not exist gets exactly the same answer.
        $this->from(route('admin.login'))
            ->post(route('admin.login.store'), ['email' => 'tiada@didik.test', 'password' => 'apa-apa'])
            ->assertSessionHasErrors(['email' => __('auth.failed')]);

        $this->assertGuest();
    }

    public function test_a_user_without_the_admin_role_cannot_sign_in_even_with_the_right_password(): void
    {
        User::factory()->create(['email' => 'biasa@didik.test', 'password' => Hash::make('rahsia-panjang-123')]);

        $this->post(route('admin.login.store'), ['email' => 'biasa@didik.test', 'password' => 'rahsia-panjang-123'])
            ->assertSessionHasErrors('email');

        $this->assertGuest();
    }

    public function test_sign_in_is_rate_limited_per_address_and_email(): void
    {
        RateLimiter::clear('yul@didik.test|127.0.0.1');
        User::factory()->admin()->create(['email' => 'yul@didik.test', 'password' => Hash::make('rahsia-panjang-123')]);

        for ($i = 0; $i < 5; $i++) {
            $this->post(route('admin.login.store'), ['email' => 'yul@didik.test', 'password' => 'salah']);
        }

        // Even the right password is refused while locked out. A browser gets the form back with
        // the message; a JSON client gets the 429 itself.
        $this->post(route('admin.login.store'), ['email' => 'yul@didik.test', 'password' => 'rahsia-panjang-123'])
            ->assertSessionHasErrors('email');
        $this->postJson(route('admin.login.store'), ['email' => 'yul@didik.test', 'password' => 'rahsia-panjang-123'])
            ->assertStatus(429);
        $this->assertGuest();
    }

    public function test_a_signed_in_admin_is_sent_away_from_the_sign_in_page(): void
    {
        $this->actingAs(User::factory()->admin()->create())
            ->get(route('admin.login'))
            ->assertRedirect(route('admin.dashboard'));
    }

    public function test_the_role_cannot_be_set_by_mass_assignment(): void
    {
        // Outside production the model is strict and refuses loudly...
        try {
            new User(['name' => 'X', 'email' => 'x@didik.test', 'password' => 'abc', 'role' => 'admin']);
            $this->fail('Mass assigning the role should have been refused.');
        } catch (MassAssignmentException) {
            $this->addToAssertionCount(1);
        }

        // ...and in production the attribute is dropped silently. Either way nobody becomes admin.
        Model::preventSilentlyDiscardingAttributes(false);

        try {
            $user = new User(['name' => 'X', 'email' => 'x@didik.test', 'password' => 'abc', 'role' => 'admin']);

            $this->assertNull($user->role);
            $this->assertFalse($user->isAdmin());
        } finally {
            Model::preventSilentlyDiscardingAttributes();
        }
    }

    public function test_the_admin_command_creates_and_updates_an_administrator(): void
    {
        $this->artisan('didik:admin', ['--name' => 'Yul', '--email' => 'yul@didik.test', '--password' => 'sangat-rahsia-123'])
            ->assertSuccessful();

        $user = User::where('email', 'yul@didik.test')->firstOrFail();
        $this->assertSame(UserRole::Admin, $user->role);
        $this->assertTrue(Hash::check('sangat-rahsia-123', $user->password));

        // Running it again resets the password and keeps one account.
        $this->artisan('didik:admin', ['--name' => 'Yul', '--email' => 'yul@didik.test', '--password' => 'kata-laluan-baharu-1'])
            ->assertSuccessful();
        $this->assertSame(1, User::count());
        $this->assertTrue(Hash::check('kata-laluan-baharu-1', $user->fresh()->password));
    }

    public function test_the_admin_command_refuses_a_short_password(): void
    {
        $this->artisan('didik:admin', ['--name' => 'Yul', '--email' => 'yul@didik.test', '--password' => 'pendek'])
            ->assertFailed();

        $this->assertSame(0, User::count());
    }

    public function test_no_seeder_creates_an_account(): void
    {
        $this->seed();

        $this->assertSame(0, User::count());
    }
}
