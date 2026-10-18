<x-layouts.public :title="__('public.result.private_title')" :noindex="true">
    <div class="container error-page">
        <x-mascot mood="hint" size="lg" />
        <h1 class="page-title">{{ __('public.result.private_title') }}</h1>
        <p>{{ __('public.result.private_text') }}</p>
        <x-button variant="primary" :href="route('quizzes.index')">{{ __('public.result.others') }}</x-button>
    </div>
</x-layouts.public>
