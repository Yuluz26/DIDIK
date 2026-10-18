@props(['title', 'description' => null])

<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="robots" content="noindex, nofollow">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{{ $title }} · {{ __('admin.nav.admin') }} DIDIK</title>
    <link rel="icon" href="{{ asset('favicon.svg') }}" type="image/svg+xml">
    @vite(['resources/css/admin.css', 'resources/js/admin.js'])
</head>
<body class="admin">
    <a class="skip-link" href="#utama">{{ __('public.skip') }}</a>

    <div class="admin-shell">
        <aside class="admin-side" aria-label="{{ __('admin.nav.label') }}">
            @include('admin.partials.nav')
        </aside>

        <div class="admin-main">
            <header class="admin-top">
                <button type="button" class="btn btn--icon admin-top__menu" data-dialog-open="admin-menu" aria-haspopup="dialog" aria-label="{{ __('public.nav.menu_open') }}">
                    <x-icon name="menu" />
                </button>
                <div class="admin-top__title">
                    <h1>{{ $title }}</h1>
                    @if ($description)
                        <p>{{ $description }}</p>
                    @endif
                </div>
                @isset($actions)
                    <div class="admin-top__actions">{{ $actions }}</div>
                @endisset
            </header>

            <main id="utama" tabindex="-1" class="admin-content">
                @if (session('status'))
                    <p class="alert alert--ok" role="status"><x-icon name="circle-check" /> {{ session('status') }}</p>
                @endif
                @if (session('warning'))
                    <p class="alert alert--warn" role="status"><x-icon name="triangle-alert" /> {{ session('warning') }}</p>
                @endif

                {{ $slot }}
            </main>
        </div>
    </div>

    <dialog class="dialog admin-menu" id="admin-menu" aria-label="{{ __('admin.nav.label') }}">
        <div class="menu-dialog__head">
            <h2 class="menu-dialog__title">{{ __('public.nav.menu_title') }}</h2>
            <button type="button" class="btn btn--icon" data-dialog-close aria-label="{{ __('public.nav.menu_close') }}"><x-icon name="x" /></button>
        </div>
        @include('admin.partials.nav', ['inDialog' => true])
    </dialog>
</body>
</html>
