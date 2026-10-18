@props(['name', 'label' => null])
{{ \App\Support\Svg::icon($name, $attributes->get('class'), $label, (string) $attributes->except('class')) }}
