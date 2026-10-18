<?php

namespace Tests\Feature\Admin;

use App\Models\QuizizzCollection;
use App\Models\QuizizzLink;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AdminQuizizzCollectionTest extends TestCase
{
    use RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        $this->actingAs(User::factory()->admin()->create());
    }

    /** @param  array<string, mixed>  $overrides */
    private function payload(array $overrides = []): array
    {
        return array_merge(['title' => 'Latihan Cuti Sekolah', 'description' => 'Pilihan untuk cuti.', 'status' => 'published', 'position' => 1], $overrides);
    }

    /** @return list<string> titles of a collection's links in curated order */
    private function titles(QuizizzCollection $collection): array
    {
        return $collection->links()->get()->pluck('title')->all();
    }

    public function test_a_collection_keeps_its_links_in_the_order_the_admin_chose(): void
    {
        [$a, $b, $c] = QuizizzLink::factory()->count(3)->sequence(['title' => 'A'], ['title' => 'B'], ['title' => 'C'])->create();

        $this->post(route('admin.collections.store'), $this->payload(['links' => [$c->id, $a->id, $b->id]]))
            ->assertRedirect(route('admin.collections.index'));

        $collection = QuizizzCollection::firstOrFail();

        $this->assertSame('latihan-cuti-sekolah', $collection->slug);
        $this->assertSame(['C', 'A', 'B'], $this->titles($collection));
    }

    public function test_updating_reorders_and_removes_links_without_deleting_them(): void
    {
        [$a, $b, $c] = QuizizzLink::factory()->count(3)->sequence(['title' => 'A'], ['title' => 'B'], ['title' => 'C'])->create();
        $collection = QuizizzCollection::factory()->create();
        $collection->links()->sync([$a->id => ['position' => 1], $b->id => ['position' => 2], $c->id => ['position' => 3]]);

        $this->put(route('admin.collections.update', $collection), $this->payload(['links' => [$b->id, $c->id]]))
            ->assertSessionHasNoErrors();

        $this->assertSame(['B', 'C'], $this->titles($collection));
        $this->assertSame(3, QuizizzLink::count(), 'removing a link from a collection keeps the link');
    }

    public function test_a_collection_can_be_saved_without_links(): void
    {
        $this->post(route('admin.collections.store'), $this->payload())->assertSessionHasNoErrors();

        $this->assertSame([], $this->titles(QuizizzCollection::firstOrFail()));
    }

    public function test_the_same_link_cannot_be_listed_twice(): void
    {
        $link = QuizizzLink::factory()->create();

        $this->post(route('admin.collections.store'), $this->payload(['links' => [$link->id, $link->id]]))
            ->assertSessionHasErrors('links.1');

        $this->assertSame(0, QuizizzCollection::count());
    }

    public function test_unknown_and_deleted_links_are_refused(): void
    {
        $gone = QuizizzLink::factory()->create();
        $gone->delete();

        $this->post(route('admin.collections.store'), $this->payload(['links' => [9999]]))->assertSessionHasErrors('links.0');
        $this->post(route('admin.collections.store'), $this->payload(['links' => [$gone->id]]))->assertSessionHasErrors('links.0');
        $this->assertSame(0, QuizizzCollection::count());
    }

    public function test_the_fields_are_validated(): void
    {
        $this->post(route('admin.collections.store'), ['status' => 'terbuka', 'position' => 1000])
            ->assertSessionHasErrors(['title', 'status', 'position']);
    }

    public function test_two_collections_with_the_same_title_get_different_slugs(): void
    {
        $this->post(route('admin.collections.store'), $this->payload());
        $this->post(route('admin.collections.store'), $this->payload());

        $this->assertSame(['latihan-cuti-sekolah', 'latihan-cuti-sekolah-2'], QuizizzCollection::orderBy('id')->pluck('slug')->all());
    }

    public function test_deleting_a_collection_keeps_its_links(): void
    {
        $link = QuizizzLink::factory()->create();
        $collection = QuizizzCollection::factory()->create();
        $collection->links()->sync([$link->id => ['position' => 1]]);

        $this->delete(route('admin.collections.destroy', $collection))->assertRedirect(route('admin.collections.index'));

        $this->assertModelMissing($collection);
        $this->assertNotSoftDeleted($link);
        $this->assertDatabaseCount('quizizz_collection_link', 0);
    }

    public function test_a_deleted_link_disappears_from_the_collection_view_but_the_page_still_renders(): void
    {
        [$keep, $drop] = QuizizzLink::factory()->count(2)->sequence(['title' => 'Kekal'], ['title' => 'Dibuang'])->create();
        $collection = QuizizzCollection::factory()->create();
        $collection->links()->sync([$keep->id => ['position' => 1], $drop->id => ['position' => 2]]);

        $drop->delete();

        $this->assertSame(['Kekal'], $this->titles($collection));
        $this->get(route('admin.collections.edit', $collection))->assertOk()->assertSee('Kekal');
        $this->get(route('admin.collections.index'))->assertOk();
    }

    public function test_the_list_and_forms_render(): void
    {
        $collection = QuizizzCollection::factory()->create(['title' => 'Koleksi Ujian']);

        $this->get(route('admin.collections.index'))->assertOk()->assertSee('Koleksi Ujian');
        $this->get(route('admin.collections.create'))->assertOk();
        $this->get(route('admin.collections.edit', $collection))->assertOk()->assertSee('Koleksi Ujian');
    }
}
