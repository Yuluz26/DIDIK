<x-layouts.public :title="__('admin.login.title')" :noindex="true" :minimal="true" body-class="page-login">
    <div class="login">
        <div class="login__panel surface">
            <x-mascot mood="wave" size="md" />
            <h1 class="login__title">{{ __('admin.login.title') }}</h1>

            <form method="post" action="{{ route('admin.login.store') }}" class="login__form" novalidate>
                @csrf

                @if ($errors->any())
                    <p class="alert alert--danger" role="alert" tabindex="-1" x-data x-init="$el.focus()">
                        <x-icon name="circle-alert" /> {{ $errors->first() }}
                    </p>
                @endif

                <div class="field">
                    <label class="field__label" for="email">{{ __('validation.attributes.email') }}</label>
                    <input class="field__control" id="email" name="email" type="email" value="{{ old('email') }}" required autocomplete="username" autofocus>
                </div>

                <div class="field">
                    <label class="field__label" for="password">{{ __('validation.attributes.password') }}</label>
                    <input class="field__control" id="password" name="password" type="password" required autocomplete="current-password">
                </div>

                <x-button variant="primary" type="submit" class="btn--block">{{ __('admin.login.submit') }}</x-button>
            </form>
        </div>
    </div>
</x-layouts.public>
