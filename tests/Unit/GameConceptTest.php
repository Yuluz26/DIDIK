<?php

namespace Tests\Unit;

use App\Games\GameConceptRegistry;
use App\Games\QuestionAnswer;
use App\Games\RiverQuest;
use App\Games\StarCollector;
use InvalidArgumentException;
use PHPUnit\Framework\TestCase;

class GameConceptTest extends TestCase
{
    private function registry(): GameConceptRegistry
    {
        return new GameConceptRegistry(new QuestionAnswer, new StarCollector, new RiverQuest);
    }

    public function test_unknown_keys_fall_back_to_the_default_concept(): void
    {
        $this->assertSame('qa', $this->registry()->resolve('removed-concept')->key());
        $this->assertSame('qa', $this->registry()->resolve(null)->key());
    }

    public function test_get_is_strict_about_unknown_keys(): void
    {
        $this->expectException(InvalidArgumentException::class);

        $this->registry()->get('nope');
    }

    public function test_the_default_concept_must_be_registered(): void
    {
        $this->expectException(InvalidArgumentException::class);

        new GameConceptRegistry(new RiverQuest);
    }

    public function test_settings_are_clamped_and_unknown_keys_dropped(): void
    {
        $quest = new RiverQuest;

        $this->assertSame(['level_size' => 10], $quest->normalize(['level_size' => 99, 'junk' => 'x']));
        $this->assertSame(['level_size' => 3], $quest->normalize(['level_size' => 1]));
        $this->assertSame(['level_size' => 5], $quest->normalize(['level_size' => 'abc']));
        $this->assertSame(['level_size' => 5], $quest->normalize([]));
    }

    public function test_select_and_boolean_settings_fall_back_to_defaults_when_invalid(): void
    {
        $this->assertSame(['progress' => 'dots'], (new QuestionAnswer)->normalize(['progress' => 'spiral']));
        $this->assertSame(['progress' => 'bar'], (new QuestionAnswer)->normalize(['progress' => 'bar']));
        $this->assertSame(['show_streak' => false], (new StarCollector)->normalize(['show_streak' => 'false']));
        $this->assertSame(['show_streak' => true], (new StarCollector)->normalize([]));
    }

    public function test_every_concept_exposes_a_view_and_validation_rules_for_each_setting(): void
    {
        foreach ($this->registry()->all() as $concept) {
            $this->assertSame("games.{$concept->key()}.player", $concept->view());
            $this->assertCount(count($concept->fields()), $concept->rules());
            $this->assertSame(array_keys($concept->fields()), array_keys($concept->defaults()));
        }
    }
}
