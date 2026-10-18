<?php

namespace Tests\Feature\Site;

use App\Enums\Difficulty;
use App\Models\Category;
use App\Models\SchoolLevel;
use App\Models\Tag;
use Database\Seeders\ReferenceDataSeeder;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class PublicPagesTest extends TestCase
{
    use CreatesQuizzes, RefreshDatabase;

    public function test_the_homepage_renders_with_no_content_at_all(): void
    {
        $this->get('/')
            ->assertOk()
            ->assertSee(__('public.home.title'))
            ->assertDontSee(__('public.home.live.heading'))
            ->assertDontSee(__('public.home.quizizz.heading'));
    }

    public function test_the_homepage_offers_a_real_question_when_a_quiz_is_available(): void
    {
        $this->seed(ReferenceDataSeeder::class);
        $quiz = $this->publishedQuiz(3);

        $this->get('/')
            ->assertOk()
            ->assertSee(__('public.home.live.heading'))
            ->assertSee($quiz->title)
            ->assertSee('Matematik');
    }

    public function test_the_homepage_never_sends_the_answer_to_the_live_question(): void
    {
        $quiz = $this->publishedQuiz(1);
        $question = $quiz->questions()->first();

        $html = $this->get('/')->assertOk()->getContent();

        // The browser gets option ids and text so it can show them; nothing says which is right.
        // @js() renders JSON.parse('...') with quotes escaped as \u0022: read it as a JSON string, then as JSON.
        preg_match("/liveQuestion\\(JSON\\.parse\\('(.*?)'\\)\\)/s", $html, $match);
        $payload = json_decode(json_decode('"'.$match[1].'"', flags: JSON_THROW_ON_ERROR), true, flags: JSON_THROW_ON_ERROR);

        $this->assertSame($question->id, $payload['question']['id']);
        $this->assertCount(3, $payload['question']['options']);

        foreach ($payload['question']['options'] as $option) {
            $this->assertSame(['id', 'body'], array_keys($option));
        }

        $this->assertStringNotContainsString('is_correct', $html);
        $this->assertStringNotContainsString($question->explanation, $html);
    }

    public function test_the_live_question_endpoint_checks_on_the_server_and_refuses_hidden_quizzes(): void
    {
        $visible = $this->publishedQuiz(1)->questions()->first();
        $hidden = $this->publishedQuiz(1, ['status' => 'draft'])->questions()->first();

        $right = $visible->options()->where('is_correct', true)->value('id');
        $wrong = $visible->options()->where('is_correct', false)->value('id');

        $this->postJson(route('live.answer'), ['question_id' => $visible->id, 'option_id' => $right])
            ->assertOk()->assertJson(['correct' => true, 'correct_option_id' => $right]);
        $this->postJson(route('live.answer'), ['question_id' => $visible->id, 'option_id' => $wrong])
            ->assertOk()->assertJson(['correct' => false, 'correct_option_id' => $right]);

        $this->postJson(route('live.answer'), ['question_id' => $hidden->id, 'option_id' => $hidden->options()->value('id')])
            ->assertNotFound();
        // An option from another question is not an answer to this one.
        $this->postJson(route('live.answer'), ['question_id' => $visible->id, 'option_id' => $hidden->options()->value('id')])
            ->assertNotFound();
        $this->postJson(route('live.answer'), ['question_id' => 'abc'])->assertUnprocessable();
    }

    public function test_browse_lists_only_quizzes_the_public_may_see(): void
    {
        $shown = $this->publishedQuiz(1, ['title' => 'Kuiz Tersedia']);
        $this->publishedQuiz(1, ['title' => 'Kuiz Draf', 'status' => 'draft']);
        $this->publishedQuiz(1, ['title' => 'Kuiz Arkib', 'status' => 'archived']);
        $this->publishedQuiz(1, ['title' => 'Kuiz Akan Datang', 'available_from' => now()->addDay()]);
        $this->publishedQuiz(1, ['title' => 'Kuiz Tamat', 'available_until' => now()->subDay()]);

        $this->get(route('quizzes.index'))
            ->assertOk()
            ->assertSee($shown->title)
            ->assertDontSee('Kuiz Draf')
            ->assertDontSee('Kuiz Arkib')
            ->assertDontSee('Kuiz Akan Datang')
            ->assertDontSee('Kuiz Tamat');
    }

    public function test_browse_filters_by_subject_topic_level_difficulty_and_search(): void
    {
        $this->seed(ReferenceDataSeeder::class);
        $math = Category::where('slug', 'matematik')->first();
        $science = Category::where('slug', 'sains')->first();
        $topic = Category::factory()->topicOf($math)->create(['name' => 'Tambah']);
        $year1 = SchoolLevel::where('slug', 'tahun-1')->first();
        $year2 = SchoolLevel::where('slug', 'tahun-2')->first();

        $a = $this->publishedQuiz(1, ['title' => 'Alpha Tambah', 'category_id' => $topic->id, 'school_level_id' => $year1->id, 'difficulty' => Difficulty::Easy]);
        $b = $this->publishedQuiz(1, ['title' => 'Beta Sains', 'category_id' => $science->id, 'school_level_id' => $year2->id, 'difficulty' => Difficulty::Hard]);
        $a->syncTagNames('nombor kecil');

        $this->get(route('quizzes.index', ['subjek' => 'matematik']))->assertSee('Alpha Tambah')->assertDontSee('Beta Sains');
        $this->get(route('quizzes.index', ['subjek' => 'matematik', 'topik' => $topic->slug]))->assertSee('Alpha Tambah')->assertDontSee('Beta Sains');
        $this->get(route('quizzes.index', ['tahap' => 'tahun-2']))->assertSee('Beta Sains')->assertDontSee('Alpha Tambah');
        $this->get(route('quizzes.index', ['kesukaran' => 'mudah']))->assertSee('Alpha Tambah')->assertDontSee('Beta Sains');
        $this->get(route('quizzes.index', ['q' => 'Sains']))->assertSee('Beta Sains')->assertDontSee('Alpha Tambah');
        $this->get(route('quizzes.index', ['q' => 'nombor kecil']))->assertSee('Alpha Tambah')->assertDontSee('Beta Sains');

        $this->assertNotNull(Tag::where('name', 'nombor kecil')->first());
        $this->assertTrue($b->exists);
    }

    public function test_unknown_filter_values_are_ignored_rather_than_rejected(): void
    {
        $quiz = $this->publishedQuiz(1);

        $this->get(route('quizzes.index', ['subjek' => 'tiada', 'tahap' => 'tiada', 'kesukaran' => 'mustahil', 'topik' => 'x']))
            ->assertOk()
            ->assertSee($quiz->title);
    }

    public function test_the_search_term_is_escaped_in_the_page_and_wildcards_are_literal(): void
    {
        $this->publishedQuiz(1, ['title' => 'Biasa']);

        $this->get(route('quizzes.index', ['q' => '<script>alert(1)</script>']))
            ->assertOk()
            ->assertDontSee('<script>alert(1)</script>', false)
            ->assertSee('&lt;script&gt;alert(1)&lt;/script&gt;', false);

        // A lone percent sign must not match everything...
        $this->get(route('quizzes.index', ['q' => '%']))->assertDontSee('Biasa');
    }

    public function test_percent_and_underscore_in_a_search_match_themselves(): void
    {
        $this->publishedQuiz(1, ['title' => 'Diskaun 50% Betul']);
        $this->publishedQuiz(1, ['title' => 'Diskaun 500 Betul']);
        $this->publishedQuiz(1, ['title' => 'Ruang_Nama']);
        $this->publishedQuiz(1, ['title' => 'RuangXNama']);

        // ...and a percent sign in a title can be found, which a backslash escape cannot do on SQLite.
        $this->get(route('quizzes.index', ['q' => '50%']))->assertSee('Diskaun 50% Betul')->assertDontSee('Diskaun 500 Betul');
        $this->get(route('quizzes.index', ['q' => 'g_N']))->assertSee('Ruang_Nama')->assertDontSee('RuangXNama');
        $this->get(route('quizzes.index', ['q' => 'dis!']))->assertDontSee('Diskaun 50% Betul');
    }

    public function test_browse_shows_a_kind_empty_state(): void
    {
        $this->get(route('quizzes.index'))->assertOk()->assertSee(__('public.browse.nothing_title'));
        $this->publishedQuiz(1);
        $this->get(route('quizzes.index', ['q' => 'tiada padanan']))->assertOk()->assertSee(__('public.browse.empty_title'));
    }

    public function test_browse_paginates(): void
    {
        for ($i = 1; $i <= 14; $i++) {
            $this->publishedQuiz(1, ['title' => sprintf('Kuiz %02d', $i)]);
        }

        $this->get(route('quizzes.index'))->assertOk()->assertSee(__('public.pagination.next'));
        $this->get(route('quizzes.index', ['page' => 2]))->assertOk()->assertSee(__('public.pagination.previous'));
    }

    public function test_static_pages_render(): void
    {
        $this->get(route('pages.about'))->assertOk()->assertSee(__('public.about.title'))->assertSee('Misi Berlevel');
        $this->get(route('pages.privacy'))->assertOk()->assertSee(__('public.privacy.title'));
    }

    public function test_the_privacy_page_shows_a_contact_only_when_one_is_configured(): void
    {
        config(['didik.contact_email' => null]);
        $this->get(route('pages.privacy'))->assertDontSee('@');

        config(['didik.contact_email' => 'hai@didik.test']);
        $this->get(route('pages.privacy'))->assertSee('hai@didik.test');
    }

    public function test_errors_are_friendly_and_in_bahasa_melayu(): void
    {
        $this->get('/tiada-halaman-ini')
            ->assertNotFound()
            ->assertSee(__('public.errors.404_title'))
            ->assertSee(__('public.errors.home'));
    }

    public function test_the_page_declares_its_language_and_a_skip_link(): void
    {
        $this->get('/')
            ->assertSee('<html lang="ms">', false)
            ->assertSee('href="#utama"', false)
            ->assertSee('<main id="utama"', false);
    }
}
