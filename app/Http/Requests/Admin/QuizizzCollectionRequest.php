<?php

namespace App\Http\Requests\Admin;

use App\Enums\LinkStatus;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class QuizizzCollectionRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    /** @return array<string, mixed> */
    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:120'],
            'description' => ['nullable', 'string', 'max:600'],
            'status' => ['required', Rule::enum(LinkStatus::class)],
            'position' => ['nullable', 'integer', 'between:0,999'],
            'links' => ['nullable', 'array', 'max:200'],
            'links.*' => ['integer', 'distinct', Rule::exists('quizizz_links', 'id')->whereNull('deleted_at')],
        ];
    }
}
