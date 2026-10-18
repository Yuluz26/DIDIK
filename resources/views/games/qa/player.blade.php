{{-- Soalan & Jawapan: calm, one question at a time. Progress as dots or a bar. --}}
@include('games.partials.bar')

<div class="player__progress container" x-show="showQuestion" x-cloak>
    @if (($settings['progress'] ?? 'dots') === 'bar')
        <div class="bar" role="presentation"><div class="bar__fill" :style="progressStyle"></div></div>
    @else
        <ol class="dots" role="presentation">
            <template x-for="(question, i) in questions" :key="question.id">
                <li class="dots__dot" :class="dotClass(i)"></li>
            </template>
        </ol>
    @endif
</div>

@include('games.partials.stage')
