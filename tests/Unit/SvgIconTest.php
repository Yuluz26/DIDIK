<?php

namespace Tests\Unit;

use App\Support\Svg;
use InvalidArgumentException;
use Tests\TestCase;

class SvgIconTest extends TestCase
{
    public function test_the_root_loses_its_size_and_gets_the_icon_class(): void
    {
        $html = (string) Svg::icon('check', 'extra');

        $this->assertStringStartsWith('<svg class="icon extra"', $html);
        $this->assertStringNotContainsString('width="24"', $html);
        $this->assertStringNotContainsString('lucide', $html);
        $this->assertStringContainsString('aria-hidden="true"', $html);
        $this->assertStringContainsString('viewBox="0 0 24 24"', $html);
    }

    public function test_shapes_inside_keep_their_own_dimensions(): void
    {
        // A <rect> without width and height draws nothing; this icon is made of rects.
        $html = (string) Svg::icon('layout-dashboard');

        $this->assertStringContainsString('<rect width="7" height="9"', $html);
    }

    public function test_a_label_makes_the_icon_meaningful(): void
    {
        $html = (string) Svg::icon('star', null, 'Bintang');

        $this->assertStringContainsString('role="img"', $html);
        $this->assertStringContainsString('aria-label="Bintang"', $html);
        $this->assertStringNotContainsString('aria-hidden', $html);
    }

    public function test_extra_attributes_are_added_to_the_root_only(): void
    {
        $html = (string) Svg::icon('check', null, null, 'x-show="open"');

        $this->assertSame(1, substr_count($html, 'x-show="open"'));
    }

    public function test_names_cannot_escape_the_icon_folder(): void
    {
        $this->expectException(InvalidArgumentException::class);

        Svg::icon('../../.env');
    }

    public function test_an_unknown_icon_is_loud_in_development_and_quiet_in_production(): void
    {
        try {
            Svg::icon('no-such-icon');
            $this->fail('A missing icon should throw outside production.');
        } catch (InvalidArgumentException) {
            $this->addToAssertionCount(1);
        }

        $this->app['env'] = 'production';

        $this->assertStringContainsString('<svg', (string) Svg::icon('no-such-icon'));
    }
}
