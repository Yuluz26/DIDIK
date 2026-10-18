@props(['word' => true])

<span {{ $attributes->class('logo') }}>
    <span class="logo__stone">
        <svg class="logo__mark" viewBox="0 0 48 48" aria-hidden="true" focusable="false">
            <g transform="rotate(26 10 20)"><ellipse class="m-fur" cx="10" cy="20" rx="7" ry="4" /></g>
            <g transform="rotate(-26 38 20)"><ellipse class="m-fur" cx="38" cy="20" rx="7" ry="4" /></g>
            <ellipse class="m-fur" cx="24" cy="23" rx="12.5" ry="10" />
            <ellipse class="m-fur" cx="24" cy="31" rx="7" ry="7" />
            <ellipse class="m-belly" cx="24" cy="35" rx="4.8" ry="2.8" />
            <ellipse class="m-ink" cx="18.5" cy="22" rx="2.3" ry="2.8" />
            <ellipse class="m-ink" cx="29.5" cy="22" rx="2.3" ry="2.8" />
            <ellipse class="m-ink" cx="24" cy="32" rx="1.9" ry="1.4" />
        </svg>
    </span>
    @if ($word)
        <span class="logo__word">didik</span>
    @endif
</span>
