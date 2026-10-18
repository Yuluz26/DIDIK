<?php

namespace Tests\Feature\Admin;

use App\Enums\CategoryTheme;
use App\Enums\CategoryType;
use App\Models\Category;
use App\Models\Quiz;
use App\Models\QuizizzLink;
use App\Models\User;
use Database\Seeders\ReferenceDataSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AdminCategoryTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        $this->seed(ReferenceDataSeeder::class);
        $this->actingAs(User::factory()->admin()->create());
    }

    private function subject(string $slug): Category
    {
        return Category::where('slug', $slug)->firstOrFail();
    }

    /** @param  array<string, mixed>  $overrides */
    private function subjectPayload(array $overrides = []): array
    {
        return array_merge(['type' => 'subject', 'name' => 'Seni Visual', 'theme' => 'lilac', 'icon' => 'sparkles', 'position' => 9], $overrides);
    }

    public function test_the_list_shows_every_subject_with_its_topics_and_quiz_counts(): void
    {
        $maths = $this->subject('matematik');
        $topic = Category::factory()->topicOf($maths)->create(['name' => 'Pecahan']);
        Quiz::factory()->count(2)->create(['category_id' => $topic->id]);

        $this->get(route('admin.categories.index'))
            ->assertOk()
            ->assertSeeInOrder(['Matematik', 'Pecahan'])
            ->assertSee('Sains');
    }

    public function test_a_subject_is_created_with_its_own_colour_and_icon(): void
    {
        $this->post(route('admin.categories.store'), $this->subjectPayload())->assertRedirect(route('admin.categories.index'));

        $subject = Category::where('name', 'Seni Visual')->firstOrFail();

        $this->assertSame(CategoryType::Subject, $subject->type);
        $this->assertSame(CategoryTheme::Lilac, $subject->theme);
        $this->assertSame('sparkles', $subject->icon);
        $this->assertSame('seni-visual', $subject->slug);
        $this->assertNull($subject->parent_id);
    }

    public function test_a_topic_takes_its_colour_and_icon_from_its_subject_whatever_the_form_says(): void
    {
        $maths = $this->subject('matematik');

        $this->post(route('admin.categories.store'), [
            'type' => 'topic', 'parent_id' => $maths->id, 'name' => 'Pecahan',
            'theme' => 'peach', 'icon' => 'heart',   // ignored
        ])->assertSessionHasNoErrors();

        $topic = Category::where('name', 'Pecahan')->firstOrFail();

        $this->assertSame(CategoryType::Topic, $topic->type);
        $this->assertSame($maths->id, $topic->parent_id);
        $this->assertSame($maths->theme, $topic->theme);
        $this->assertSame($maths->icon, $topic->icon);
    }

    public function test_a_topic_needs_a_real_subject_as_its_parent(): void
    {
        $maths = $this->subject('matematik');
        $topic = Category::factory()->topicOf($maths)->create();

        $base = ['type' => 'topic', 'name' => 'Terlepas'];

        $this->post(route('admin.categories.store'), $base)->assertSessionHasErrors('parent_id');
        $this->post(route('admin.categories.store'), $base + ['parent_id' => 9999])->assertSessionHasErrors('parent_id');
        $this->post(route('admin.categories.store'), $base + ['parent_id' => $topic->id])->assertSessionHasErrors('parent_id');   // topics do not nest

        $this->assertDatabaseMissing('categories', ['name' => 'Terlepas']);
    }

    public function test_a_subject_cannot_be_given_a_parent(): void
    {
        $this->post(route('admin.categories.store'), $this->subjectPayload(['parent_id' => $this->subject('sains')->id]))
            ->assertSessionHasErrors('parent_id');
    }

    public function test_colours_and_icons_are_limited_to_the_known_set(): void
    {
        $this->post(route('admin.categories.store'), $this->subjectPayload(['theme' => 'neon']))->assertSessionHasErrors('theme');
        $this->post(route('admin.categories.store'), $this->subjectPayload(['icon' => '../../etc/passwd']))->assertSessionHasErrors('icon');
        $this->post(route('admin.categories.store'), $this->subjectPayload(['icon' => 'tidak-wujud']))->assertSessionHasErrors('icon');
        $this->post(route('admin.categories.store'), $this->subjectPayload(['name' => '']))->assertSessionHasErrors('name');
        $this->post(route('admin.categories.store'), $this->subjectPayload(['position' => 1000]))->assertSessionHasErrors('position');
    }

    public function test_editing_keeps_the_slug_so_public_addresses_do_not_change(): void
    {
        $maths = $this->subject('matematik');

        $this->put(route('admin.categories.update', $maths), $this->subjectPayload(['name' => 'Matematik Asas', 'theme' => 'butter', 'icon' => 'calculator']))
            ->assertRedirect(route('admin.categories.index'));

        $maths->refresh();
        $this->assertSame('Matematik Asas', $maths->name);
        $this->assertSame('matematik', $maths->slug);
        $this->assertSame(CategoryTheme::Butter, $maths->theme);
    }

    public function test_the_kind_of_category_cannot_be_changed_after_it_is_created(): void
    {
        $maths = $this->subject('matematik');
        $topic = Category::factory()->topicOf($maths)->create();

        // A form claiming this topic is a subject with its own colour changes neither the kind nor the look.
        $this->put(route('admin.categories.update', $topic), [
            'type' => 'subject', 'parent_id' => $maths->id, 'name' => 'Cubaan', 'theme' => 'peach', 'icon' => 'heart',
        ])->assertSessionHasNoErrors();

        $topic->refresh();
        $this->assertSame('Cubaan', $topic->name);
        $this->assertSame(CategoryType::Topic, $topic->type);
        $this->assertSame($maths->id, $topic->parent_id);
        $this->assertSame($maths->theme, $topic->theme);
        $this->assertSame($maths->icon, $topic->icon);
    }

    public function test_a_topic_edit_still_needs_its_subject(): void
    {
        $topic = Category::factory()->topicOf($this->subject('matematik'))->create(['name' => 'Asal']);

        $this->put(route('admin.categories.update', $topic), ['name' => 'Tanpa induk'])->assertSessionHasErrors('parent_id');

        $this->assertSame('Asal', $topic->fresh()->name);
    }

    public function test_changing_a_subjects_colour_and_icon_reaches_its_topics(): void
    {
        $maths = $this->subject('matematik');
        $topic = Category::factory()->topicOf($maths)->create();

        $this->put(route('admin.categories.update', $maths), $this->subjectPayload(['name' => 'Matematik', 'theme' => 'peach', 'icon' => 'heart']))
            ->assertSessionHasNoErrors();

        $topic->refresh();
        $this->assertSame(CategoryTheme::Peach, $topic->theme);
        $this->assertSame('heart', $topic->icon);
    }

    public function test_a_topic_can_move_to_another_subject_and_follows_its_look(): void
    {
        $maths = $this->subject('matematik');
        $science = $this->subject('sains');
        $topic = Category::factory()->topicOf($maths)->create();

        $this->put(route('admin.categories.update', $topic), ['type' => 'topic', 'parent_id' => $science->id, 'name' => $topic->name])
            ->assertSessionHasNoErrors();

        $topic->refresh();
        $this->assertSame($science->id, $topic->parent_id);
        $this->assertSame($science->theme, $topic->theme);
        $this->assertSame($science->icon, $topic->icon);
    }

    public function test_the_create_and_edit_forms_render(): void
    {
        $maths = $this->subject('matematik');

        $this->get(route('admin.categories.create'))->assertOk();
        $this->get(route('admin.categories.create', ['jenis' => 'topik', 'subjek' => $maths->id]))->assertOk()->assertSee('Matematik');
        $this->get(route('admin.categories.edit', $maths))->assertOk()->assertSee('Matematik');
    }

    public function test_a_category_that_is_still_used_cannot_be_deleted(): void
    {
        $maths = $this->subject('matematik');
        $sains = $this->subject('sains');
        $usedByQuiz = Category::factory()->topicOf($maths)->create(['name' => 'Dipakai kuiz']);
        $usedByLink = Category::factory()->topicOf($maths)->create(['name' => 'Dipakai pautan']);
        Quiz::factory()->create(['category_id' => $usedByQuiz->id]);
        QuizizzLink::factory()->create(['category_id' => $usedByLink->id]);
        Category::factory()->topicOf($sains)->create();

        foreach ([$usedByQuiz, $usedByLink, $sains] as $category) {
            $this->delete(route('admin.categories.destroy', $category))
                ->assertRedirect(route('admin.categories.index'))
                ->assertSessionHas('warning');

            $this->assertModelExists($category);
        }
    }

    public function test_an_unused_category_can_be_deleted(): void
    {
        $topic = Category::factory()->topicOf($this->subject('sains'))->create();

        $this->delete(route('admin.categories.destroy', $topic))
            ->assertRedirect(route('admin.categories.index'))
            ->assertSessionHas('status');

        $this->assertModelMissing($topic);
    }
}
