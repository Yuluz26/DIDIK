{{-- The top bar of the player: a way out, what is being played, where the child is. --}}
<header class="player__bar">
    <div class="container player__bar-inner">
        <button type="button" class="btn btn--quiet player__quit" data-dialog-open="quit" aria-haspopup="dialog">
            <x-icon name="arrow-left" />
            {{ __('public.player.quit') }}
        </button>
        <p class="player__title">{{ $quiz->title }}</p>
        <p class="player__position" x-show="showQuestion" x-cloak x-text="positionText"></p>
    </div>
</header>
