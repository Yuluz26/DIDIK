{{--
    A small, static picture of one game concept, drawn with the same classes the player uses.
    Decorative: the concept's name and description sit next to it as text.
--}}
@props(['concept'])

@switch($concept)
    @case('qa')
        <p class="way__caption">{{ __('public.player.question_of', ['current' => 3, 'total' => 5]) }}</p>
        <p class="way__question">7 + 2 = ?</p>
        <div class="way__answers">
            <span class="answer" data-state="idle"><span class="answer__letter">A</span><span>8</span><span></span></span>
            <span class="answer" data-state="correct">
                <span class="answer__letter">B</span><span>9</span>
                <span class="answer__badge"><x-icon name="check" /> {{ __('public.player.badge_right') }}</span>
            </span>
        </div>
        <ol class="dots">
            <li class="dots__dot is-done"></li>
            <li class="dots__dot is-done"></li>
            <li class="dots__dot is-current"></li>
            <li class="dots__dot"></li>
            <li class="dots__dot"></li>
        </ol>
        @break

    @case('stars')
        <p class="way__caption">{{ __('public.player.stars.collected', ['count' => 3]) }}</p>
        <ol class="slots">
            @foreach ([1, 1, 1, 0, 0] as $lit)
                <li @class(['slot', 'is-lit' => $lit])><x-star :on="(bool) $lit" /></li>
            @endforeach
        </ol>
        @break

    @default
        <p class="way__caption">{{ __('public.player.quest.level', ['level' => 1]) }} · {{ __('public.player.quest.position', ['current' => 3, 'total' => 5]) }}</p>
        <div class="path" style="--count: 7; --step: 3">
            <ol class="path__cells">
                <li class="path__cell"><span class="path__bank"><x-icon name="house" /></span></li>
                @foreach (range(1, 5) as $n)
                    <li class="path__cell">
                        <span @class(['path__stone', 'is-right' => $n < 3, 'is-current' => $n === 3])>
                            @if ($n < 3)<x-icon name="check" />@endif
                        </span>
                    </li>
                @endforeach
                <li class="path__cell"><span class="path__bank"><x-icon name="flag" /></span></li>
            </ol>
            <div class="path__rider"><x-mascot mood="happy" size="sm" /></div>
        </div>
@endswitch
