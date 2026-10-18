@props([
    'title' => null,
    'description' => null,
    'bodyClass' => null,
    'noindex' => false,
    'minimal' => false,
])

<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ $title ? $title.' · DIDIK' : 'DIDIK' }}</title>
    @if ($description)
        <meta name="description" content="{{ $description }}">
    @endif
    @if ($noindex)
        <meta name="robots" content="noindex">
    @endif
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <meta name="theme-color" content="#e8f0eb">
    <meta property="og:site_name" content="DIDIK">
    <meta property="og:title" content="{{ $title ?: 'DIDIK' }}">
    <meta property="og:locale" content="ms_MY">
    @if ($description)
        <meta property="og:description" content="{{ $description }}">
    @endif
    <link rel="icon" href="{{ asset('favicon.svg') }}" type="image/svg+xml">
    @vite(['resources/css/public.css', 'resources/js/public.js'])
    {{ $head ?? '' }}
</head>
<body @class([$bodyClass])>
    <a class="skip-link" href="#utama">{{ __('public.skip') }}</a>

    @unless ($minimal)
        <x-site-header />
    @endunless

    <main id="utama" tabindex="-1">
        {{ $slot }}
    </main>

    @unless ($minimal)
        <x-site-footer />
    @endunless
</body>
</html>
