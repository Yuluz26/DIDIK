<?php

namespace App\Games;

use InvalidArgumentException;

class GameConceptRegistry
{
    public const DEFAULT = 'qa';

    /** @var array<string, GameConcept> */
    private array $concepts = [];

    public function __construct(GameConcept ...$concepts)
    {
        foreach ($concepts as $concept) {
            $this->concepts[$concept->key()] = $concept;
        }

        if (! isset($this->concepts[self::DEFAULT])) {
            throw new InvalidArgumentException('The default game concept "'.self::DEFAULT.'" must be registered.');
        }
    }

    /** @return array<string, GameConcept> */
    public function all(): array
    {
        return $this->concepts;
    }

    /** @return list<string> */
    public function keys(): array
    {
        return array_keys($this->concepts);
    }

    public function has(?string $key): bool
    {
        return $key !== null && isset($this->concepts[$key]);
    }

    public function get(string $key): GameConcept
    {
        return $this->concepts[$key] ?? throw new InvalidArgumentException("Unknown game concept [{$key}].");
    }

    /** Unknown or removed keys fall back to the default so existing quizzes keep working. */
    public function resolve(?string $key): GameConcept
    {
        return $this->has($key) ? $this->concepts[$key] : $this->concepts[self::DEFAULT];
    }
}
