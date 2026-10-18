<?php

namespace App\Http\Controllers\Admin;

use App\Enums\LinkStatus;
use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\QuizizzCollectionRequest;
use App\Models\QuizizzCollection;
use App\Models\QuizizzLink;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\DB;

class QuizizzCollectionController extends Controller
{
    public function index(): View
    {
        $collections = QuizizzCollection::query()
            ->withCount('links')
            ->orderBy('position')
            ->orderBy('title')
            ->get();

        return view('admin.collections.index', ['collections' => $collections]);
    }

    public function create(): View
    {
        return view('admin.collections.form', $this->formData(new QuizizzCollection(['status' => LinkStatus::Draft, 'position' => 0])));
    }

    public function store(QuizizzCollectionRequest $request): RedirectResponse
    {
        DB::transaction(function () use ($request) {
            $collection = QuizizzCollection::create($this->attributes($request));
            $this->syncLinks($collection, $request->validated('links', []));
        });

        return redirect()->route('admin.collections.index')->with('status', __('admin.common.created'));
    }

    public function edit(QuizizzCollection $collection): View
    {
        return view('admin.collections.form', $this->formData($collection->load('links')));
    }

    public function update(QuizizzCollectionRequest $request, QuizizzCollection $collection): RedirectResponse
    {
        DB::transaction(function () use ($request, $collection) {
            $collection->update($this->attributes($request));
            $this->syncLinks($collection, $request->validated('links', []));
        });

        return redirect()->route('admin.collections.index')->with('status', __('admin.common.saved'));
    }

    public function destroy(QuizizzCollection $collection): RedirectResponse
    {
        // Only the grouping goes; the links themselves stay in the library.
        $collection->delete();

        return redirect()->route('admin.collections.index')->with('status', __('admin.common.deleted'));
    }

    /** @return array<string, mixed> */
    private function attributes(QuizizzCollectionRequest $request): array
    {
        $data = $request->validated();
        $data['position'] = $data['position'] ?? 0;

        unset($data['links']);

        return $data;
    }

    /** @param  list<int|string>  $ids  in display order */
    private function syncLinks(QuizizzCollection $collection, array $ids): void
    {
        $collection->links()->sync(
            collect($ids)->values()->mapWithKeys(fn ($id, int $position) => [(int) $id => ['position' => $position + 1]])->all(),
        );
    }

    /** @return array<string, mixed> */
    private function formData(QuizizzCollection $collection): array
    {
        return [
            'collection' => $collection,
            'allLinks' => QuizizzLink::orderBy('title')->get(['id', 'title', 'status']),
        ];
    }
}
