<?php

namespace App\Games;

/**
 * A game concept is a presentation of a quiz: it picks the Blade views and the
 * settings that shape them. It never touches questions, answers or scoring.
 *
 * To add a concept: extend this class, register it in AppServiceProvider and add a
 * resources/views/games/{key} folder with a `player` view and its lang entries.
 */
abstract class GameConcept
{
    abstract public function key(): string;

    /**
     * Setting definitions, keyed by setting name. Supported types:
     *  - select:  ['type' => 'select', 'options' => [...], 'default' => ...]
     *  - boolean: ['type' => 'boolean', 'default' => ...]
     *  - integer: ['type' => 'integer', 'min' => n, 'max' => n, 'default' => ...]
     *
     * @return array<string, array<string, mixed>>
     */
    abstract public function fields(): array;

    public function name(): string
    {
        return __("games.{$this->key()}.name");
    }

    public function description(): string
    {
        return __("games.{$this->key()}.description");
    }

    public function view(): string
    {
        return "games.{$this->key()}.player";
    }

    /** @return array<string, mixed> */
    public function defaults(): array
    {
        return array_map(fn (array $field) => $field['default'], $this->fields());
    }

    /**
     * Laravel validation rules for the settings, keyed "{prefix}.{name}".
     *
     * @return array<string, array<int, string>>
     */
    public function rules(string $prefix = 'game_settings'): array
    {
        $rules = [];

        foreach ($this->fields() as $name => $field) {
            $rules["{$prefix}.{$name}"] = match ($field['type']) {
                'select' => ['nullable', 'in:'.implode(',', $field['options'])],
                'boolean' => ['nullable', 'boolean'],
                'integer' => ['nullable', 'integer', "min:{$field['min']}", "max:{$field['max']}"],
            };
        }

        return $rules;
    }

    /**
     * Reduce arbitrary input to valid settings: unknown keys are dropped, invalid or
     * missing values fall back to the default. Safe to run on anything stored in the database.
     *
     * @param  array<string, mixed>  $input
     * @return array<string, mixed>
     */
    public function normalize(array $input): array
    {
        $settings = [];

        foreach ($this->fields() as $name => $field) {
            $value = $input[$name] ?? null;

            $settings[$name] = match ($field['type']) {
                'select' => in_array($value, $field['options'], true) ? $value : $field['default'],
                'boolean' => $value === null ? $field['default'] : filter_var($value, FILTER_VALIDATE_BOOLEAN),
                'integer' => is_numeric($value)
                    ? max($field['min'], min($field['max'], (int) $value))
                    : $field['default'],
            };
        }

        return $settings;
    }
}
