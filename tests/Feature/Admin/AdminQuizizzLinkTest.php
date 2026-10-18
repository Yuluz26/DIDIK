<?php

namespace Tests\Feature\Admin;

use App\Enums\LinkStatus;
use App\Models\Category;
use App\Models\QuizizzLink;
use App\Models\SchoolLevel;
use App\Models\User;
use Database\Seeders\ReferenceDataSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\TestCase;

class AdminQuizizzLinkTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        Storage::fake('public');
        $this->seed(ReferenceDataSeeder::class);
        $this->actingAs(User::factory()->admin()->create());
    }

    /** @param  array<string, mixed>  $overrides */
    private function payload(array $overrides = []): array
    {
        return array_merge([
            'title' => 'Tambah Hingga 20',
            'url' => 'https://quizizz.com/admin/quiz/abc123',
            'description' => 'Latihan tambah untuk Tahun 2.',
            'category_id' => Category::where('slug', 'matematik')->value('id'),
            'school_level_id' => SchoolLevel::where('slug', 'tahun-2')->value('id'),
            'status' => 'published',
            'tags' => 'tambah, nombor, Tambah',
        ], $overrides);
    }

    public function test_a_link_is_stored_with_its_subject_level_status_and_unique_tags(): void
    {
        $this->post(route('admin.links.store'), $this->payload())->assertRedirect(route('admin.links.index'));

        $link = QuizizzLink::with('tags')->firstOrFail();

        $this->assertSame('Tambah Hingga 20', $link->title);
        $this->assertSame('https://quizizz.com/admin/quiz/abc123', $link->url);
        $this->assertSame(LinkStatus::Published, $link->status);
        $this->assertSame('matematik', $link->category->slug);
        $this->assertSame(['nombor', 'tambah'], $link->tags->pluck('name')->map('strtolower')->all());
    }

    public function test_the_address_is_trimmed_before_it_is_stored(): void
    {
        $this->post(route('admin.links.store'), $this->payload(['url' => "  https://quizizz.com/admin/quiz/x  \n"]));

        $this->assertSame('https://quizizz.com/admin/quiz/x', QuizizzLink::firstOrFail()->url);
    }

    public function test_the_platforms_new_name_is_accepted_too(): void
    {
        $this->post(route('admin.links.store'), $this->payload(['url' => 'https://wayground.com/admin/quiz/abc']))
            ->assertSessionHasNoErrors();

        $this->assertSame(1, QuizizzLink::count());
    }

    /** @return array<string, array{string}> */
    public static function addressesThatMustBeRefused(): array
    {
        return [
            'another site' => ['https://example.com/quizizz.com'],
            'plain http' => ['http://quizizz.com/x'],
            'script' => ['javascript:alert(1)'],
            'credentials' => ['https://abc@quizizz.com/x'],
            'lookalike' => ['https://quizizz.com.example.com/x'],
        ];
    }

    #[DataProvider('addressesThatMustBeRefused')]
    public function test_addresses_outside_quizizz_are_refused_with_a_clear_message(string $url): void
    {
        $this->from(route('admin.links.create'))
            ->post(route('admin.links.store'), $this->payload(['url' => $url]))
            ->assertRedirect(route('admin.links.create'))
            ->assertSessionHasErrors('url');

        $this->assertStringContainsString('quizizz.com', session('errors')->first('url'));
        $this->assertSame(0, QuizizzLink::count());
    }

    public function test_required_fields_and_the_status_are_validated(): void
    {
        $this->post(route('admin.links.store'), ['status' => 'terbuka'])
            ->assertSessionHasErrors(['title', 'url', 'status']);

        $this->post(route('admin.links.store'), $this->payload(['category_id' => 9999]))
            ->assertSessionHasErrors('category_id');
    }

    public function test_every_status_can_be_chosen(): void
    {
        foreach (LinkStatus::cases() as $status) {
            $this->post(route('admin.links.store'), $this->payload(['title' => 'Pautan '.$status->value, 'status' => $status->value]))
                ->assertSessionHasNoErrors();
        }

        $this->assertSame(count(LinkStatus::cases()), QuizizzLink::count());
    }

    public function test_a_thumbnail_is_stored_under_a_random_name_and_never_the_uploaded_one(): void
    {
        $this->post(route('admin.links.store'), $this->payload([
            'thumbnail' => UploadedFile::fake()->image('../../evil name.php.jpg', 300, 200),
        ]))->assertSessionHasNoErrors();

        $path = QuizizzLink::firstOrFail()->thumbnail_path;

        $this->assertMatchesRegularExpression('~^quizizz-thumbnails/[0-9a-f]{32}\.(jpe?g|png|webp)$~', $path);
        Storage::disk('public')->assertExists($path);
    }

    public function test_replacing_the_thumbnail_removes_the_old_file(): void
    {
        $this->post(route('admin.links.store'), $this->payload(['thumbnail' => UploadedFile::fake()->image('a.jpg', 200, 200)]));
        $link = QuizizzLink::firstOrFail();
        $old = $link->thumbnail_path;

        $this->put(route('admin.links.update', $link), $this->payload(['thumbnail' => UploadedFile::fake()->image('b.png', 200, 200)]))
            ->assertSessionHasNoErrors();

        $new = $link->fresh()->thumbnail_path;
        $this->assertNotSame($old, $new);
        Storage::disk('public')->assertMissing($old);
        Storage::disk('public')->assertExists($new);
    }

    public function test_saving_without_a_new_file_keeps_the_current_thumbnail(): void
    {
        $this->post(route('admin.links.store'), $this->payload(['thumbnail' => UploadedFile::fake()->image('a.jpg', 200, 200)]));
        $link = QuizizzLink::firstOrFail();
        $path = $link->thumbnail_path;

        $this->put(route('admin.links.update', $link), $this->payload(['title' => 'Tajuk baharu']))->assertSessionHasNoErrors();

        $this->assertSame($path, $link->fresh()->thumbnail_path);
        Storage::disk('public')->assertExists($path);
    }

    public function test_the_thumbnail_can_be_removed(): void
    {
        $this->post(route('admin.links.store'), $this->payload(['thumbnail' => UploadedFile::fake()->image('a.jpg', 200, 200)]));
        $link = QuizizzLink::firstOrFail();
        $path = $link->thumbnail_path;

        $this->put(route('admin.links.update', $link), $this->payload(['remove_thumbnail' => '1']))->assertSessionHasNoErrors();

        $this->assertNull($link->fresh()->thumbnail_path);
        Storage::disk('public')->assertMissing($path);
    }

    /** @return array<string, array{callable(): UploadedFile}> */
    public static function filesThatMustBeRefused(): array
    {
        return [
            'svg, which can carry script' => [fn () => UploadedFile::fake()->createWithContent('logo.svg', '<svg xmlns="http://www.w3.org/2000/svg" onload="alert(1)"/>')],
            'php renamed to jpg' => [fn () => UploadedFile::fake()->createWithContent('shell.jpg', '<?php echo 1;')],
            'a document' => [fn () => UploadedFile::fake()->create('notes.pdf', 100, 'application/pdf')],
            'larger than 2 MB' => [fn () => UploadedFile::fake()->image('big.jpg', 300, 300)->size(2100)],
            'too small to be a picture' => [fn () => UploadedFile::fake()->image('tiny.png', 20, 20)],
            'absurdly wide' => [fn () => UploadedFile::fake()->image('wide.png', 4100, 100)],
        ];
    }

    /** @param  callable(): UploadedFile  $file */
    #[DataProvider('filesThatMustBeRefused')]
    public function test_unsuitable_thumbnails_are_refused_and_nothing_is_stored(callable $file): void
    {
        $this->post(route('admin.links.store'), $this->payload(['thumbnail' => $file()]))
            ->assertSessionHasErrors('thumbnail');

        $this->assertSame(0, QuizizzLink::count());
        $this->assertSame([], Storage::disk('public')->allFiles());
    }

    public function test_deleting_a_link_hides_it_and_removes_its_picture(): void
    {
        $this->post(route('admin.links.store'), $this->payload(['thumbnail' => UploadedFile::fake()->image('a.jpg', 200, 200)]));
        $link = QuizizzLink::firstOrFail();
        $path = $link->thumbnail_path;

        $this->delete(route('admin.links.destroy', $link))->assertRedirect(route('admin.links.index'));

        $this->assertSoftDeleted($link);
        Storage::disk('public')->assertMissing($path);
    }

    public function test_the_list_can_be_searched_by_title_address_and_tag_and_filtered_by_status(): void
    {
        $this->post(route('admin.links.store'), $this->payload(['title' => 'Pecahan Mudah', 'url' => 'https://quizizz.com/admin/quiz/pecahan', 'tags' => 'pecahan', 'status' => 'draft']));
        $this->post(route('admin.links.store'), $this->payload(['title' => 'Sains Haiwan', 'url' => 'https://quizizz.com/admin/quiz/haiwan', 'tags' => 'vertebrata', 'status' => 'published']));

        $this->get(route('admin.links.index', ['q' => 'pecahan']))->assertSee('Pecahan Mudah')->assertDontSee('Sains Haiwan');
        $this->get(route('admin.links.index', ['q' => 'vertebrata']))->assertSee('Sains Haiwan')->assertDontSee('Pecahan Mudah');
        $this->get(route('admin.links.index', ['q' => 'quiz/haiwan']))->assertSee('Sains Haiwan')->assertDontSee('Pecahan Mudah');
        $this->get(route('admin.links.index', ['status' => 'draft']))->assertSee('Pecahan Mudah')->assertDontSee('Sains Haiwan');
    }

    public function test_search_treats_percent_and_underscore_literally(): void
    {
        QuizizzLink::factory()->create(['title' => 'Diskaun 100% betul']);
        QuizizzLink::factory()->create(['title' => 'Diskaun 1000 betul']);

        $this->get(route('admin.links.index', ['q' => '100%']))
            ->assertSee('Diskaun 100% betul')
            ->assertDontSee('Diskaun 1000 betul');
    }

    public function test_the_forms_render_and_name_the_accepted_domains(): void
    {
        $link = QuizizzLink::factory()->create();

        $this->get(route('admin.links.create'))->assertOk()->assertSee('wayground.com');
        $this->get(route('admin.links.edit', $link))->assertOk()->assertSee($link->url, false);
    }
}
