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
        // The notice quotes the settings the site really runs with, so it cannot drift from them.
        $facts = [
            ':days' => (string) config('didik.retention_days'),
            ':hours' => (string) round(config('session.lifetime') / 60),
            ':cookie' => (string) config('session.cookie'),
        ];

        $fill = fn (string $text) => strtr($text, $facts);

        return view('pages.privacy', [
            'email' => config('didik.contact_email'),
            'sections' => collect(__('public.privacy.sections'))
                ->map(fn (array $section) => ['heading' => $section['heading'], 'items' => array_map($fill, $section['items'])])
                ->all(),
            'english' => array_map($fill, __('public.privacy.english.items')),
        ]);
    }
}
