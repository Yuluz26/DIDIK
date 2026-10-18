<?php

namespace App\Http\Controllers\Site;

use App\Games\GameConceptRegistry;
use App\Http\Controllers\Controller;
use Illuminate\Contracts\View\View;

class PageController extends Controller
{
    public function about(GameConceptRegistry $concepts): View
    {
        return view('pages.about', ['concepts' => $concepts->all()]);
    }

    public function privacy(): View
    {
        return view('pages.privacy', ['email' => config('didik.contact_email')]);
    }
}
