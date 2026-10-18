@php
    $items = [
        ['route' => 'admin.dashboard', 'match' => 'admin.dashboard', 'icon' => 'layout-dashboard', 'label' => __('admin.nav.dashboard')],
        ['route' => 'admin.quizzes.index', 'match' => 'admin.quizzes.*', 'icon' => 'list-checks', 'label' => __('admin.nav.quizzes')],
        ['route' => 'admin.categories.index', 'match' => 'admin.categories.*', 'icon' => 'folder', 'label' => __('admin.nav.categories')],
        ['route' => 'admin.links.index', 'match' => 'admin.links.*', 'icon' => 'link', 'label' => __('admin.nav.links')],
        ['route' => 'admin.collections.index', 'match' => 'admin.collections.*', 'icon' => 'layers', 'label' => __('admin.nav.collections')],
    ];
@endphp

@unless ($inDialog ?? false)
    <a class="admin-brand" href="{{ route('admin.dashboard') }}">
        <x-logo />
        <span class="admin-brand__tag">{{ __('admin.nav.admin') }}</span>
    </a>
@endunless

<nav class="admin-nav" aria-label="{{ __('admin.nav.label') }}">
    <ul>
        @foreach ($items as $item)
            <li>
                <a href="{{ route($item['route']) }}" @if (request()->routeIs($item['match'])) aria-current="page" @endif>
                    <x-icon :name="$item['icon']" />
                    {{ $item['label'] }}
                </a>
            </li>
        @endforeach
    </ul>
</nav>

<div class="admin-side__foot">
    <a class="admin-nav__plain" href="{{ route('home') }}" target="_blank" rel="noopener">
        <x-icon name="external-link" /> {{ __('admin.nav.view_site') }}
    </a>
    <p class="admin-side__user">{{ auth()->user()->name }}</p>
    <form method="post" action="{{ route('admin.logout') }}">
        @csrf
        <button type="submit" class="btn btn--sm btn--block"><x-icon name="log-out" /> {{ __('admin.nav.logout') }}</button>
    </form>
</div>
