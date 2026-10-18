@php
    $links = [
        ['route' => 'quizzes.index', 'match' => 'quizzes.*', 'label' => __('public.nav.quizzes')],
        ['route' => 'quizizz.index', 'match' => 'quizizz.*', 'label' => __('public.nav.quizizz')],
        ['route' => 'pages.about', 'match' => 'pages.about', 'label' => __('public.nav.parents')],
    ];
@endphp

<header class="site-header">
    <div class="container site-header__inner">
        <a class="site-header__logo" href="{{ route('home') }}" aria-label="{{ __('public.nav.home') }}">
            <x-logo />
        </a>

        <nav class="site-nav" aria-label="{{ __('public.nav.label') }}">
            <ul class="site-nav__list">
                @foreach ($links as $link)
                    <li>
                        <a href="{{ route($link['route']) }}" @if (request()->routeIs($link['match'])) aria-current="page" @endif>
                            {{ $link['label'] }}
                        </a>
                    </li>
                @endforeach
            </ul>
        </nav>

        <x-button variant="primary" size="sm" :href="route('quizzes.index')" class="site-header__cta">
            {{ __('public.nav.play') }}
        </x-button>

        <button
            type="button"
            class="btn btn--icon site-header__menu"
            data-dialog-open="menu"
            aria-haspopup="dialog"
            aria-label="{{ __('public.nav.menu_open') }}"
        >
            <x-icon name="menu" />
        </button>
    </div>

    <dialog class="dialog menu-dialog" id="menu" aria-labelledby="menu-title">
        <div class="menu-dialog__head">
            <h2 id="menu-title" class="menu-dialog__title">{{ __('public.nav.menu_title') }}</h2>
            <button type="button" class="btn btn--icon" data-dialog-close aria-label="{{ __('public.nav.menu_close') }}">
                <x-icon name="x" />
            </button>
        </div>
        <ul class="menu-dialog__list">
            @foreach ($links as $link)
                <li>
                    <a class="btn" href="{{ route($link['route']) }}" @if (request()->routeIs($link['match'])) aria-current="page" @endif>
                        {{ $link['label'] }}
                    </a>
                </li>
            @endforeach
            <li>
                <a class="btn btn--primary" href="{{ route('quizzes.index') }}">
                    {{ __('public.nav.play') }}
                    <x-icon name="arrow-right" />
                </a>
            </li>
        </ul>
    </dialog>
</header>
