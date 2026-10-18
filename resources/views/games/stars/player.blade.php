{{-- Kutip Bintang: each right answer lights a star slot. In "feedback at the end" mode the slots only fill in. --}}
@include('games.partials.bar')

<div class="player__progress container" x-show="showQuestion" x-cloak>
    <div class="stars-strip">
        <ol class="slots" role="presentation">
            <template x-for="(question, i) in questions" :key="question.id">
                <li class="slot" :class="slotClass(i)">
                    <x-icon name="star" x-bind:class="starClass(i)" />
                </li>
            </template>
        </ol>
        <p class="stars-strip__text" x-text="starsText"></p>
        <p class="stars-strip__streak" x-show="showStreak" x-cloak x-text="streakText"></p>
    </div>
</div>

@include('games.partials.stage')
