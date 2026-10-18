<?php

namespace App\Http\Controllers\Admin;

use App\Enums\CategoryTheme;
use App\Enums\CategoryType;
use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\CategoryRequest;
use App\Models\Category;
use App\Models\Quiz;
use App\Models\QuizizzLink;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;

class CategoryController extends Controller
{
    public function index(): View
    {
        $subjects = Category::subjects()->with('children')->get();

        $counts = Quiz::query()
            ->whereNotNull('category_id')
            ->selectRaw('category_id, count(*) as total')
            ->groupBy('category_id')
            ->pluck('total', 'category_id');

        return view('admin.categories.index', ['subjects' => $subjects, 'counts' => $counts]);
    }

    public function create(Request $request): View
    {
        $isTopic = $request->query('jenis') === 'topik';

        return view('admin.categories.form', $this->formData(new Category([
            'type' => $isTopic ? CategoryType::Topic : CategoryType::Subject,
            'parent_id' => $isTopic ? $request->integer('subjek') ?: null : null,
            'theme' => CategoryTheme::Mint,
            'icon' => 'shapes',
            'position' => 0,
        ])));
    }

    public function store(CategoryRequest $request): RedirectResponse
    {
        Category::create($this->attributes($request->validated()));

        return redirect()->route('admin.categories.index')->with('status', __('admin.common.created'));
    }

    public function edit(Category $category): View
    {
        return view('admin.categories.form', $this->formData($category));
    }

    public function update(CategoryRequest $request, Category $category): RedirectResponse
    {
        $category->update($this->attributes($request->validated(), $category));

        return redirect()->route('admin.categories.index')->with('status', __('admin.common.saved'));
    }

    public function destroy(Category $category): RedirectResponse
    {
        $uses = Quiz::where('category_id', $category->id)->count() + QuizizzLink::where('category_id', $category->id)->count();

        if ($uses > 0 || $category->children()->exists()) {
            return redirect()->route('admin.categories.index')
                ->with('warning', __('categories.in_use', ['name' => $category->name]));
        }

        $category->delete();

        return redirect()->route('admin.categories.index')->with('status', __('admin.common.deleted'));
    }

    /** @return array<string, mixed> */
    private function formData(Category $category): array
    {
        return [
            'category' => $category,
            'subjects' => Category::subjects()->get(),
            'themes' => CategoryTheme::cases(),
            'icons' => Category::ICONS,
        ];
    }

    /**
     * @param  array<string, mixed>  $data
     * @return array<string, mixed>
     */
    private function attributes(array $data, ?Category $existing = null): array
    {
        $data['position'] = $data['position'] ?? 0;

        if ($data['type'] === CategoryType::Topic->value) {
            // A topic mirrors its subject so listings and pickers stay consistent.
            $parent = Category::findOrFail($data['parent_id']);
            $data['theme'] = $parent->theme->value;
            $data['icon'] = $parent->icon;
        }

        // The kind of category never changes after it is created.
        if ($existing) {
            $data['type'] = $existing->type->value;
        }

        return $data;
    }
}
