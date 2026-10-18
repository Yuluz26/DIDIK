<?php

namespace App\Http\Requests\Admin;

use App\Enums\CategoryTheme;
use App\Enums\CategoryType;
use App\Models\Category;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class CategoryRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, mixed> */
    public function rules(): array
    {
        $isTopic = $this->input('type') === CategoryType::Topic->value;

        return [
            'type' => ['required', Rule::enum(CategoryType::class)],
            // A topic always sits under a subject; a subject has no parent.
            'parent_id' => $isTopic
                ? ['required', 'integer', Rule::exists('categories', 'id')->where('type', CategoryType::Subject->value)]
                : ['prohibited'],
            'name' => ['required', 'string', 'max:80'],
            // Topics take their colour and icon from their subject, so only subjects set them.
            'theme' => $isTopic ? ['nullable'] : ['required', Rule::enum(CategoryTheme::class)],
            'icon' => $isTopic ? ['nullable'] : ['required', Rule::in(Category::ICONS)],
            'position' => ['nullable', 'integer', 'between:0,999'],
        ];
    }
}
