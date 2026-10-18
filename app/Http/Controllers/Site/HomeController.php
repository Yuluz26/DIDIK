<?php

namespace App\Http\Controllers\Site;

use App\Http\Controllers\Controller;
use App\Models\QuizizzCollection;
use App\Services\Catalog;
use App\Services\LiveQuestion;
use Illuminate\Contracts\View\View;

class HomeController extends Controller
{
    public function __invoke(Catalog $catalog, LiveQuestion $live): View
    {
        $collection = QuizizzCollection::published()
            ->whereHas('publishedLinks')
            ->orderBy('position')
            ->first();

        return view('pages.home', [
            'live' => $live->today(),
            'subjects' => $catalog->subjects(),
            'levels' => $catalog->levels(),
            'demos' => $catalog->conceptDemos(),
            'collection' => $collection,
            'links' => $collection?->publishedLinks()->with(['category.parent', 'level'])->limit(4)->get(),
        ]);
    }
}
