<?php

namespace App\Http\Requests\Admin;

use App\Enums\LinkStatus;
use App\Rules\QuizizzUrl;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class QuizizzLinkRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, mixed> */
    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:160'],
            'url' => ['required', 'string', 'max:500', new QuizizzUrl],
            'description' => ['nullable', 'string', 'max:600'],
            'category_id' => ['nullable', 'integer', 'exists:categories,id'],
            'school_level_id' => ['nullable', 'integer', 'exists:school_levels,id'],
            'status' => ['required', Rule::enum(LinkStatus::class)],
            'tags' => ['nullable', 'string', 'max:300'],
            // Re-encoded images only: no SVG, so nothing in the file can carry script.
            'thumbnail' => ['nullable', 'file', 'mimes:jpg,jpeg,png,webp', 'max:2048', 'dimensions:min_width=64,min_height=64,max_width=4000,max_height=4000'],
            'remove_thumbnail' => ['boolean'],
        ];
    }

    /** @return array<string, mixed> */
    public function linkAttributes(): array
    {
        $data = $this->validated();
        $data['url'] = trim($data['url']);

        unset($data['tags'], $data['thumbnail'], $data['remove_thumbnail']);

        return $data;
    }
}
