<?php

namespace App\Http\Controllers\Site;

use App\Http\Controllers\Controller;
use App\Models\QuizizzCollection;
use Illuminate\Contracts\View\View;

class QuizizzController extends Controller
{
    public function index(): View
    {
        $collections = QuizizzCollection::published()
            ->with(['publishedLinks' => fn ($links) => $links->with(['category.parent', 'level', 'tags'])])
            ->orderBy('position')
            ->get()
            ->filter(fn ($collection) => $collection->publishedLinks->isNotEmpty());

        return view('pages.quizizz.index', ['collections' => $collections]);
    }

    public function show(QuizizzCollection $collection): View
    {
        abort_unless($collection->status->value === 'published', 404);

        $collection->load(['publishedLinks' => fn ($links) => $links->with(['category.parent', 'level', 'tags'])]);

        return view('pages.quizizz.show', ['collection' => $collection]);
    }
}
