<?php

namespace App\Enums\Concerns;

use Illuminate\Support\Str;

/**
 * Gives a backed enum a translated label from lang/{locale}/enums.php,
 * keyed by the snake-cased enum name and the case value.
 */
trait HasLabel
{
    public function label(): string
    {
        return __('enums.'.Str::snake(class_basename(static::class)).'.'.$this->value);
    }

    /** @return array<string, string> value => label */
    public static function options(): array
    {
        $options = [];

        foreach (self::cases() as $case) {
            $options[$case->value] = $case->label();
        }

        return $options;
    }
}
