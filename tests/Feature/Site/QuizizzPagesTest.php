<?php

namespace Tests\Feature\Site;

use App\Enums\LinkStatus;
use App\Models\QuizizzCollection;
use App\Models\QuizizzLink;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class QuizizzPagesTest extends TestCase
{
    use RefreshDatabase;

    private function collection(string $title, LinkStatus $status, array $links): QuizizzCollection
    {
        $collection = QuizizzCollection::factory()->create(['title' => $title, 'status' => $status]);

        foreach ($links as $position => $link) {
            $collection->links()->attach($link, ['position' => $position + 1]);
        }

        return $collection;
    }

    public function test_only_published_collections_with_published_links_are_listed(): void
    {
        $good = QuizizzLink::factory()->published()->create(['title' => 'Pautan Elok']);
        $draft = QuizizzLink::factory()->create(['title' => 'Pautan Draf']);
        $broken = QuizizzLink::factory()->create(['title' => 'Pautan Rosak', 'status' => LinkStatus::Broken]);
        $archived = QuizizzLink::factory()->create(['title' => 'Pautan Arkib', 'status' => LinkStatus::Archived]);

        $this->collection('Koleksi Terbit', LinkStatus::Published, [$good->id, $draft->id, $broken->id, $archived->id]);
        $this->collection('Koleksi Draf', LinkStatus::Draft, [$good->id]);
        $this->collection('Koleksi Kosong', LinkStatus::Published, [$draft->id]);

        $this->get(route('quizizz.index'))
            ->assertOk()
            ->assertSee('Koleksi Terbit')
            ->assertSee('Pautan Elok')
            ->assertDontSee('Pautan Draf')
            ->assertDontSee('Pautan Rosak')
            ->assertDontSee('Pautan Arkib')
            ->assertDontSee('Koleksi Draf')
            ->assertDontSee('Koleksi Kosong');
    }

    public function test_links_open_in_a_new_tab_with_safe_attributes_and_an_honest_label(): void
    {
        $link = QuizizzLink::factory()->published()->create(['url' => 'https://quizizz.com/admin/quiz/abc123']);
        $this->collection('Koleksi', LinkStatus::Published, [$link->id]);

        $this->get(route('quizizz.index'))
            ->assertSee('href="https://quizizz.com/admin/quiz/abc123"', false)
            ->assertSee('target="_blank"', false)
            ->assertSee('rel="noopener noreferrer"', false)
            ->assertSee(__('public.quizizz.open'));
    }

    public function test_link_text_is_escaped(): void
    {
        $link = QuizizzLink::factory()->published()->create(['title' => '<img src=x onerror=alert(1)>']);
        $this->collection('Koleksi', LinkStatus::Published, [$link->id]);

        $this->get(route('quizizz.index'))
            ->assertDontSee('<img src=x onerror=alert(1)>', false)
            ->assertSee('&lt;img src=x onerror=alert(1)&gt;', false);
    }

    public function test_links_keep_the_curated_order(): void
    {
        $first = QuizizzLink::factory()->published()->create(['title' => 'Satu']);
        $second = QuizizzLink::factory()->published()->create(['title' => 'Dua']);
        $this->collection('Koleksi', LinkStatus::Published, [$second->id, $first->id]);

        $this->get(route('quizizz.index'))->assertSeeInOrder(['Dua', 'Satu']);
    }

    public function test_an_empty_state_is_shown_when_nothing_is_published(): void
    {
        $this->get(route('quizizz.index'))->assertOk()->assertSee(__('public.quizizz.empty_title'));
    }

    public function test_a_collection_page_is_public_only_when_published(): void
    {
        $link = QuizizzLink::factory()->published()->create(['title' => 'Pautan Dalam']);
        $published = $this->collection('Terbit', LinkStatus::Published, [$link->id]);
        $draft = $this->collection('Belum', LinkStatus::Draft, [$link->id]);

        $this->get(route('quizizz.show', $published))->assertOk()->assertSee('Pautan Dalam');
        $this->get(route('quizizz.show', $draft))->assertNotFound();
    }
}
