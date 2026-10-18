<footer class="site-footer">
    <div class="container site-footer__inner">
        <div class="site-footer__brand">
            <a href="{{ route('home') }}" aria-label="{{ __('public.nav.home') }}"><x-logo /></a>
            <p>{{ __('public.footer.tagline') }}</p>
        </div>

        <nav class="site-footer__nav" aria-label="{{ __('public.footer.nav_label') }}">
            <ul>
                <li><a href="{{ route('quizzes.index') }}">{{ __('public.nav.quizzes') }}</a></li>
                <li><a href="{{ route('quizizz.index') }}">{{ __('public.nav.quizizz') }}</a></li>
                <li><a href="{{ route('pages.about') }}">{{ __('public.footer.about') }}</a></li>
                <li><a href="{{ route('pages.privacy') }}">{{ __('public.footer.privacy') }}</a></li>
            </ul>
        </nav>

        <p class="site-footer__legal">{{ __('public.footer.copyright', ['year' => now()->year]) }}</p>
    </div>

    <div class="site-footer__word" aria-hidden="true">didik</div>
</footer>
