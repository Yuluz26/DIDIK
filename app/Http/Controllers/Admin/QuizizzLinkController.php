<?php

namespace App\Http\Controllers\Admin;

use App\Enums\LinkStatus;
use App\Http\Controllers\Controller;
use App\Http\Requests\Admin\QuizizzLinkRequest;
use App\Models\Category;
use App\Models\QuizizzLink;
use App\Models\SchoolLevel;
use Illuminate\Contracts\View\View;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;

class QuizizzLinkController extends Controller
{
    private const DISK = 'public';

    private const FOLDER = 'quizizz-thumbnails';

    public function index(Request $request): View
    {
        $search = trim($request->string('q')->limit(80)->toString());
        $status = LinkStatus::tryFrom($request->string('status')->toString());

        $links = QuizizzLink::query()
            ->with(['category.parent', 'level'])
            ->when($status, fn ($q) => $q->where('status', $status))
            ->when($search !== '', function ($q) use ($search) {
                $like = '%'.addcslashes($search, '\\%_').'%';
                $q->where(fn ($w) => $w
                    ->where('title', 'like', $like)
                    ->orWhere('description', 'like', $like)
                    ->orWhere('url', 'like', $like)
                    ->orWhereHas('tags', fn ($t) => $t->where('name', 'like', $like)));
            })
            ->orderByDesc('updated_at')
            ->paginate(20)
            ->withQueryString();

        return view('admin.links.index', ['links' => $links, 'search' => $search, 'status' => $status]);
    }

    public function create(): View
    {
        return view('admin.links.form', $this->formData(new QuizizzLink(['status' => LinkStatus::Draft])));
    }

    public function store(QuizizzLinkRequest $request): RedirectResponse
    {
        DB::transaction(function () use ($request) {
            $link = QuizizzLink::create($request->linkAttributes());
            $link->syncTagNames($request->validated('tags'));
            $this->storeThumbnail($link, $request->file('thumbnail'));
        });

        return redirect()->route('admin.links.index')->with('status', __('admin.common.created'));
    }

    public function edit(QuizizzLink $link): View
    {
        return view('admin.links.form', $this->formData($link->load('tags')));
    }

    public function update(QuizizzLinkRequest $request, QuizizzLink $link): RedirectResponse
    {
        DB::transaction(function () use ($request, $link) {
            $link->update($request->linkAttributes());
            $link->syncTagNames($request->validated('tags'));

            if ($request->boolean('remove_thumbnail')) {
                $this->deleteThumbnail($link);
            }

            $this->storeThumbnail($link, $request->file('thumbnail'));
        });

        return redirect()->route('admin.links.index')->with('status', __('admin.common.saved'));
    }

    public function destroy(QuizizzLink $link): RedirectResponse
    {
        $this->deleteThumbnail($link);
        $link->delete();

        return redirect()->route('admin.links.index')->with('status', __('admin.common.deleted'));
    }

    /** Keeps a random file name, so what the admin uploaded never decides a path on disk. */
    private function storeThumbnail(QuizizzLink $link, ?UploadedFile $file): void
    {
        if (! $file) {
            return;
        }

        $this->deleteThumbnail($link);

        $link->update(['thumbnail_path' => $file->storePubliclyAs(
            self::FOLDER,
            bin2hex(random_bytes(16)).'.'.$file->guessExtension(),
            self::DISK,
        )]);
    }

    private function deleteThumbnail(QuizizzLink $link): void
    {
        if ($link->thumbnail_path) {
            Storage::disk(self::DISK)->delete($link->thumbnail_path);
            $link->update(['thumbnail_path' => null]);
        }
    }

    /** @return array<string, mixed> */
    private function formData(QuizizzLink $link): array
    {
        return [
            'link' => $link,
            'subjects' => Category::subjects()->with('children')->get(),
            'levels' => SchoolLevel::orderBy('position')->get(),
        ];
    }
}
