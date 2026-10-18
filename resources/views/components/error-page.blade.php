@props(['mood' => 'hint', 'title', 'text'])

<x-layouts.public :title="$title" :noindex="true">
    <div class="container error-page">
        <x-mascot :mood="$mood" size="lg" />
        <h1 class="page-title">{{ $title }}</h1>
        <p>{{ $text }}</p>
        <x-button variant="primary" :href="url('/')">{{ __('public.errors.home') }}</x-button>
    </div>
</x-layouts.public>
