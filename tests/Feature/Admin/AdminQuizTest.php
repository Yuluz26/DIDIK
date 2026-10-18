<?php

namespace Tests\Feature\Admin;

use App\Enums\QuizStatus;
use App\Models\Category;
use App\Models\Quiz;
use App\Models\SchoolLevel;
use App\Models\User;
use Database\Seeders\ReferenceDataSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Str;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class AdminQuizTest extends TestCase
{
    use CreatesQuizzes, RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        $this->seed(ReferenceDataSeeder::class);
        $this->actingAs(User::factory()->admin()->create());
    }

    /** @return array<string, mixed> */
    private function payload(array $overrides = []): array
    {
        return array_merge([
            'title' => 'Tambah Hingga 20',
            'summary' => 'Latihan tambah.',
            'language' => 'ms',
            'category_id' => Category::where('slug', 'matematik')->value('id'),
            'school_level_id' => SchoolLevel::where('slug', 'tahun-2')->value('id'),
            'difficulty' => 'mudah',
            'game_concept' => 'qa',
            'game_settings' => ['progress' => 'bar'],
            'attempts_allowed' => '',
            'feedback_mode' => 'instant',
            'shuffle_questions' => '0',
            'shuffle_options' => '1',
            'tags' => 'tambah, nombor, Tambah',
        ], $overrides);
    }

    public function test_a_quiz_is_created_as_a_draft_and_the_admin_goes_straight_to_its_questions(): void
    {
        $response = $this->post(route('admin.quizzes.store'), $this->payload());

        $quiz = Quiz::firstOrFail();
        $response->assertRedirect(route('admin.quizzes.questions.edit', $quiz));

        $this->assertSame(QuizStatus::Draft, $quiz->status);
        $this->assertSame('tambah-hingga-20', $quiz->slug);
        $this->assertSame(['progress' => 'bar'], $quiz->game_settings);
        $this->assertNull($quiz->attempts_allowed);
        $this->assertTrue($quiz->shuffle_options);
        $this->assertFalse($quiz->shuffle_questions);
        $this->assertNotNull($quiz->created_by);
        $this->assertEqualsCanonicalizing(['tambah', 'nombor'], $quiz->tags->pluck('name')->all());
    }

    public function test_the_form_cannot_publish_a_quiz_on_creation(): void
    {
        $this->post(route('admin.quizzes.store'), $this->payload(['status' => 'published']));

        $this->assertSame(QuizStatus::Draft, Quiz::firstOrFail()->status);
    }

    public function test_required_fields_are_validated_with_friendly_messages(): void
    {
        $this->post(route('admin.quizzes.store'), ['game_concept' => 'qa'])
            ->assertSessionHasErrors(['title', 'language', 'difficulty', 'feedback_mode']);

        $this->assertSame(0, Quiz::count());

        $this->from(route('admin.quizzes.create'))
            ->post(route('admin.quizzes.store'), $this->payload(['title' => '']))
            ->assertSessionHasErrors(['title' => 'Tajuk wajib diisi.']);
    }

    public function test_concept_settings_are_validated_for_the_chosen_concept_only(): void
    {
        $this->post(route('admin.quizzes.store'), $this->payload(['game_concept' => 'quest', 'game_settings' => ['level_size' => 99]]))
            ->assertSessionHasErrors('game_settings.level_size');

        $this->post(route('admin.quizzes.store'), $this->payload(['game_concept' => 'qa', 'game_settings' => ['progress' => 'spiral']]))
            ->assertSessionHasErrors('game_settings.progress');

        $this->post(route('admin.quizzes.store'), $this->payload(['game_concept' => 'unknown']))
            ->assertSessionHasErrors('game_concept');

        $this->assertSame(0, Quiz::count());
    }

    public function test_settings_that_belong_to_other_concepts_are_discarded(): void
    {
        $this->post(route('admin.quizzes.store'), $this->payload([
            'game_concept' => 'quest',
            'game_settings' => ['level_size' => '4', 'progress' => 'bar', 'show_streak' => '1', 'junk' => 'x'],
        ]));

        $this->assertSame(['level_size' => 4], Quiz::firstOrFail()->game_settings);
    }

    public function test_the_availability_window_must_end_after_it_starts(): void
    {
        $quiz = $this->publishedQuiz(1);

        $this->put(route('admin.quizzes.update', $quiz), $this->payload([
            'status' => 'published',
            'available_from' => '2026-12-01T10:00',
            'available_until' => '2026-11-01T10:00',
        ]))->assertSessionHasErrors('available_until');
    }

    public function test_an_admin_can_edit_a_quiz(): void
    {
        $quiz = $this->publishedQuiz(2);

        $this->put(route('admin.quizzes.update', $quiz), $this->payload([
            'title' => 'Judul Baharu',
            'status' => 'published',
            'game_concept' => 'stars',
            'game_settings' => ['show_streak' => '0'],
            'attempts_allowed' => '2',
            'feedback_mode' => 'end',
        ]))->assertRedirect(route('admin.quizzes.edit', $quiz));

        $quiz->refresh();
        $this->assertSame('Judul Baharu', $quiz->title);
        $this->assertSame('stars', $quiz->game_concept);
        $this->assertSame(['show_streak' => false], $quiz->game_settings);
        $this->assertSame(2, $quiz->attempts_allowed);
        $this->assertSame('end', $quiz->feedback_mode->value);
        // The address does not change when the title does: shared links keep working.
        $this->assertNotSame('judul-baharu', $quiz->slug);
    }

    public function test_switching_the_game_concept_never_touches_questions_or_scoring(): void
    {
        $quiz = $this->publishedQuiz(3);
        $before = $quiz->questions()->with('options')->get()->toArray();

        foreach (['stars', 'quest', 'qa'] as $concept) {
            $this->put(route('admin.quizzes.update', $quiz), $this->payload([
                'status' => 'published',
                'game_concept' => $concept,
                'game_settings' => ['level_size' => '3', 'show_streak' => '1', 'progress' => 'dots'],
            ]))->assertSessionHasNoErrors();
        }

        $this->assertEquals($before, $quiz->questions()->with('options')->get()->toArray());
    }

    public function test_a_quiz_cannot_be_published_until_every_question_is_complete(): void
    {
        $quiz = Quiz::factory()->create();

        $this->put(route('admin.quizzes.update', $quiz), $this->payload(['title' => 'Tidak Boleh', 'status' => 'published']))
            ->assertSessionHasErrors(['status' => __('quizzes.problem_no_questions')]);

        // Nothing was half-saved: the title edit rolled back with the refused publish.
        $quiz->refresh();
        $this->assertSame(QuizStatus::Draft, $quiz->status);
        $this->assertNotSame('Tidak Boleh', $quiz->title);
    }

    public function test_publishing_names_the_questions_that_are_not_ready(): void
    {
        $quiz = $this->publishedQuiz(2);
        $quiz->update(['status' => QuizStatus::Draft]);
        $quiz->questions()->orderBy('position')->first()->options()->where('is_correct', true)->update(['is_correct' => false]);

        $this->post(route('admin.quizzes.publish', $quiz))
            ->assertSessionHasErrors(['status' => __('quizzes.problem_correct', ['number' => 1])]);

        $this->assertSame(QuizStatus::Draft, $quiz->fresh()->status);
    }

    public function test_publish_unpublish_and_archive(): void
    {
        $quiz = $this->publishedQuiz(2);
        $quiz->update(['status' => QuizStatus::Draft, 'published_at' => null]);

        $this->post(route('admin.quizzes.publish', $quiz))->assertSessionHas('status');
        $quiz->refresh();
        $this->assertSame(QuizStatus::Published, $quiz->status);
        $this->assertNotNull($quiz->published_at);
        $this->get(route('quizzes.show', $quiz->slug))->assertOk();

        $this->post(route('admin.quizzes.unpublish', $quiz));
        $this->assertSame(QuizStatus::Draft, $quiz->fresh()->status);
        $this->get(route('quizzes.show', $quiz->slug))->assertNotFound();

        $this->post(route('admin.quizzes.archive', $quiz));
        $this->assertSame(QuizStatus::Archived, $quiz->fresh()->status);
    }

    public function test_duplicating_makes_a_draft_copy_with_questions_and_tags(): void
    {
        $quiz = $this->publishedQuiz(2);
        $quiz->syncTagNames('a, b');

        $this->post(route('admin.quizzes.duplicate', $quiz));

        $copy = Quiz::where('id', '!=', $quiz->id)->firstOrFail();
        $this->assertSame(QuizStatus::Draft, $copy->status);
        $this->assertNull($copy->published_at);
        $this->assertNotSame($quiz->slug, $copy->slug);
        $this->assertSame(__('quizzes.copy_title', ['title' => $quiz->title]), $copy->title);
        $this->assertSame(2, $copy->questions()->count());
        $this->assertSame(6, $copy->questions()->withCount('options')->get()->sum('options_count'));
        $this->assertSame(2, $copy->questions()->get()->filter(fn ($q) => $q->options()->where('is_correct', true)->count() === 1)->count());
        $this->assertEqualsCanonicalizing(['a', 'b'], $copy->tags->pluck('name')->all());
        // The original is untouched and shares no rows with the copy.
        $this->assertSame(2, $quiz->questions()->count());
    }

    public function test_deleting_hides_a_quiz_but_keeps_its_attempts(): void
    {
        $quiz = $this->publishedQuiz(1);
        $quiz->attempts()->create([
            'uuid' => (string) Str::uuid(), 'session_hash' => str_repeat('a', 64),
            'layout' => ['questions' => [], 'options' => []], 'started_at' => now(),
        ]);

        $this->delete(route('admin.quizzes.destroy', $quiz))->assertRedirect(route('admin.quizzes.index'));

        $this->assertSoftDeleted($quiz);
        $this->assertDatabaseCount('attempts', 1);
        $this->get(route('quizzes.show', $quiz->slug))->assertNotFound();
        $this->get(route('admin.quizzes.index'))->assertDontSee($quiz->title);
    }

    public function test_the_list_can_be_searched_and_filtered_by_status(): void
    {
        Quiz::factory()->create(['title' => 'Kuiz Draf Satu']);
        $this->publishedQuiz(1, ['title' => 'Kuiz Terbit Dua']);

        $this->get(route('admin.quizzes.index'))->assertSee('Kuiz Draf Satu')->assertSee('Kuiz Terbit Dua');
        $this->get(route('admin.quizzes.index', ['status' => 'draft']))->assertSee('Kuiz Draf Satu')->assertDontSee('Kuiz Terbit Dua');
        $this->get(route('admin.quizzes.index', ['q' => 'Terbit']))->assertSee('Kuiz Terbit Dua')->assertDontSee('Kuiz Draf Satu');
        $this->get(route('admin.quizzes.index', ['q' => '%']))->assertDontSee('Kuiz Terbit Dua');
    }

    public function test_the_edit_form_renders_for_every_concept_and_shows_current_settings(): void
    {
        foreach (['qa' => ['progress' => 'bar'], 'stars' => ['show_streak' => false], 'quest' => ['level_size' => 7]] as $concept => $settings) {
            $quiz = $this->publishedQuiz(1, ['game_concept' => $concept, 'game_settings' => $settings]);

            $this->get(route('admin.quizzes.edit', $quiz))
                ->assertOk()
                ->assertSee($quiz->title)
                ->assertSee('name="game_concept"', false);
        }

        $this->get(route('admin.quizzes.create'))->assertOk();
    }

    public function test_the_statistics_page_renders_with_and_without_attempts(): void
    {
        $quiz = $this->publishedQuiz(2);

        $this->get(route('admin.quizzes.stats', $quiz))->assertOk()->assertSee(__('admin.stats.no_attempts'));
    }
}
