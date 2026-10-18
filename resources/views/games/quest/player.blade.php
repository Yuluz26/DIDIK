{{--
    Misi Berlevel (Seberang Sungai): questions grouped into levels. Each answer is a hop to the
    next stone; the end of a level is a bank to rest on. Wrong answers still move Didi on, because
    the point is to cross the river, not to be stopped by it.
--}}
@include('games.partials.bar')

<div class="player__progress container" x-show="showQuestion || isCheckpoint" x-cloak>
    <p class="path__caption"><span x-text="levelText"></span> · <span x-text="levelPositionText"></span></p>

    <div class="path" :style="pathStyle">
        <ol class="path__cells" role="presentation">
            <li class="path__cell"><span class="path__bank"><x-icon name="house" /></span></li>
            <template x-for="i in stones" :key="levelNumber + '-' + i">
                <li class="path__cell">
                    <span class="path__stone" :class="stoneClass(i)">
                        <x-icon name="check" x-show="stoneIsRight(i)" x-cloak />
                        <x-icon name="lightbulb" x-show="stoneIsWrong(i)" x-cloak />
                    </span>
                </li>
            </template>
            <li class="path__cell"><span class="path__bank"><x-icon name="flag" /></span></li>
        </ol>
        <div class="path__rider">
            <x-mascot mood="happy" size="sm" />
        </div>
    </div>
</div>

@include('games.partials.stage')
