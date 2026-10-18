@props(['on' => false])

{{-- A star is drawn from the icon set; the outline carries the contrast, the fill is decoration. --}}
<x-icon name="star" {{ $attributes->class(['star', 'star--on' => $on]) }} />
