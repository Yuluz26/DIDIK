{{--
    Didi, the mouse-deer (kancil). One drawing; the mood changes only eyes, brows, mouth, head tilt
    and arms. Wide ears set out to the sides and a long face with a small nose keep it a deer,
    not a dog or a fox. Decorative unless a label is given (use a label only where Didi carries
    information the surrounding text does not).
--}}
@props(['mood' => 'happy', 'size' => 'md', 'label' => null])

<svg
    {{ $attributes->class(['mascot', "mascot--{$size}", "mascot--{$mood}"]) }}
    viewBox="0 0 200 222"
    width="200"
    height="222"
    focusable="false"
    @if ($label) role="img" aria-label="{{ $label }}" @else aria-hidden="true" @endif
>
    {{-- Arms sit behind the body so the shoulders overlap them. --}}
    @switch($mood)
        @case('cheer')
            <path class="m-arm" d="M64 174 Q30 156 36 116" />
            <path class="m-arm" d="M136 174 Q170 156 164 116" />
            @break
        @case('wave')
            <path class="m-arm" d="M136 174 Q170 156 166 120" />
            <path class="m-line" d="M178 108 q7 5 5 14M186 100 q10 7 8 20" opacity=".55" />
            @break
    @endswitch

    {{-- Shoulders, chest and the coat's pale spots --}}
    <ellipse class="m-fur" cx="100" cy="186" rx="54" ry="34" />
    <ellipse class="m-belly" cx="100" cy="192" rx="24" ry="26" />
    <circle class="m-belly" cx="64" cy="180" r="4.5" />
    <circle class="m-belly" cx="136" cy="180" r="4.5" />
    <circle class="m-belly" cx="76" cy="170" r="3.5" />
    <circle class="m-belly" cx="124" cy="170" r="3.5" />

    {{-- Scarf in the brand green --}}
    <path class="m-scarf" d="M62 154 Q100 174 138 154 L142 169 Q100 190 58 169 Z" />
    <path class="m-scarf" d="M108 174 L126 196 L110 192 Z" />

    {{-- Head, tilted a little when Didi is being gentle --}}
    <g @if ($mood === 'hint') transform="rotate(-5 100 130)" @elseif ($mood === 'sleep') transform="rotate(6 100 130)" @elseif ($mood === 'think') transform="rotate(4 100 130)" @endif>
        {{-- Wide ears out to the sides, behind the head --}}
        <g transform="rotate(26 42 82)">
            <ellipse class="m-fur" cx="42" cy="82" rx="28" ry="16" />
            <ellipse class="m-ear" cx="44" cy="82" rx="18" ry="9" />
        </g>
        <g transform="rotate(-26 158 82)">
            <ellipse class="m-fur" cx="158" cy="82" rx="28" ry="16" />
            <ellipse class="m-ear" cx="156" cy="82" rx="18" ry="9" />
        </g>

        {{-- Rounded head with a long, narrow face --}}
        <ellipse class="m-fur" cx="100" cy="96" rx="50" ry="40" />
        <ellipse class="m-fur" cx="100" cy="126" rx="29" ry="28" />
        <ellipse class="m-belly" cx="100" cy="143" rx="20" ry="11" />
        <circle class="m-cheek" cx="63" cy="113" r="7.5" />
        <circle class="m-cheek" cx="137" cy="113" r="7.5" />
        <ellipse class="m-ink" cx="100" cy="131" rx="7.5" ry="5.5" />

        @switch($mood)
            @case('cheer')
                {{-- Eyes squeezed into happy arcs, mouth wide open --}}
                <path class="m-line" d="M63 98 Q74 85 85 98M115 98 Q126 85 137 98" />
                <path class="m-ink" d="M89 140 Q100 158 111 140 Z" />
                <ellipse class="m-ear" cx="100" cy="150" rx="7" ry="4" />
                @break

            @case('think')
                <ellipse class="m-ink" cx="74" cy="96" rx="9.5" ry="11.5" />
                <ellipse class="m-ink" cx="126" cy="96" rx="9.5" ry="11.5" />
                <circle class="m-white" cx="78" cy="91" r="3.6" />
                <circle class="m-white" cx="130" cy="91" r="3.6" />
                <path class="m-line" d="M61 78 Q72 71 86 77" />
                <ellipse class="m-line" cx="108" cy="145" rx="3.4" ry="4.2" />
                @break

            @case('hint')
                {{-- Gentle and encouraging: inner brows lifted, a small smile --}}
                <ellipse class="m-ink" cx="74" cy="97" rx="9.5" ry="11.5" />
                <ellipse class="m-ink" cx="126" cy="97" rx="9.5" ry="11.5" />
                <circle class="m-white" cx="77" cy="92" r="3.5" />
                <circle class="m-white" cx="129" cy="92" r="3.5" />
                <circle class="m-white" cx="71" cy="102" r="1.7" />
                <circle class="m-white" cx="123" cy="102" r="1.7" />
                <path class="m-line" d="M62 82 L86 73M138 82 L114 73" />
                <path class="m-line" d="M92 145 Q100 150 108 145" />
                @break

            @case('sleep')
                <path class="m-line" d="M63 98 Q74 107 85 98M115 98 Q126 107 137 98" />
                <path class="m-line" d="M94 145 Q100 148 106 145" />
                @break

            @default
                {{-- happy, wave --}}
                <ellipse class="m-ink" cx="74" cy="96" rx="9.5" ry="11.5" />
                <ellipse class="m-ink" cx="126" cy="96" rx="9.5" ry="11.5" />
                <circle class="m-white" cx="77.5" cy="91" r="3.6" />
                <circle class="m-white" cx="129.5" cy="91" r="3.6" />
                <circle class="m-white" cx="71" cy="101" r="1.8" />
                <circle class="m-white" cx="123" cy="101" r="1.8" />
                <path class="m-line" d="M91 143 Q100 152 109 143" />
        @endswitch
    </g>
</svg>
