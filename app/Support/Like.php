<?php

namespace App\Support;

use Illuminate\Support\Facades\DB;

/**
 * LIKE patterns for text typed into a search box. A "%" or "_" the visitor types must match
 * itself rather than act as a wildcard, and that has to behave the same on MySQL and SQLite:
 * a backslash is an escape only in MySQL, so an explicit ESCAPE character is used instead.
 */
final class Like
{
    private const ESCAPE = '!';

    /** "%term%", with any wildcard inside the term made literal. */
    public static function contains(string $term): string
    {
        $e = self::ESCAPE;

        return '%'.str_replace([$e, '%', '_'], [$e.$e, $e.'%', $e.'_'], $term).'%';
    }

    /** SQL matching a column against a pattern from contains(); bind the pattern to the placeholder. */
    public static function clause(string $column): string
    {
        return DB::getQueryGrammar()->wrap($column)." like ? escape '".self::ESCAPE."'";
    }
}
