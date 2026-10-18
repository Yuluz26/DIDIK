<?php

namespace Database\Seeders;

use App\Enums\CategoryTheme;
use App\Enums\CategoryType;
use App\Models\Category;
use App\Models\SchoolLevel;
use Illuminate\Database\Seeder;

/**
 * Reference data the product cannot run without: Malaysian school levels and the core
 * subjects. Safe to run in every environment, including production, and idempotent.
 */
class ReferenceDataSeeder extends Seeder
{
    public function run(): void
    {
        $levels = [
            ['Prasekolah', 'prasekolah', 5, 6],
            ['Tahun 1', 'tahun-1', 7, 7],
            ['Tahun 2', 'tahun-2', 8, 8],
            ['Tahun 3', 'tahun-3', 9, 9],
            ['Tahun 4', 'tahun-4', 10, 10],
            ['Tahun 5', 'tahun-5', 11, 11],
            ['Tahun 6', 'tahun-6', 12, 12],
        ];

        foreach ($levels as $position => [$name, $slug, $min, $max]) {
            SchoolLevel::updateOrCreate(
                ['slug' => $slug],
                ['name' => $name, 'min_age' => $min, 'max_age' => $max, 'position' => $position + 1],
            );
        }

        $subjects = [
            ['Bahasa Melayu', 'bahasa-melayu', CategoryTheme::Peach, 'book'],
            ['Matematik', 'matematik', CategoryTheme::Sky, 'calculator'],
            ['Sains', 'sains', CategoryTheme::Butter, 'flask'],
            ['Bahasa Inggeris', 'bahasa-inggeris', CategoryTheme::Lilac, 'languages'],
        ];

        foreach ($subjects as $position => [$name, $slug, $theme, $icon]) {
            Category::updateOrCreate(
                ['slug' => $slug],
                [
                    'type' => CategoryType::Subject,
                    'name' => $name,
                    'theme' => $theme,
                    'icon' => $icon,
                    'position' => $position + 1,
                ],
            );
        }
    }
}
