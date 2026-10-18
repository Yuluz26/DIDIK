<?php

namespace App\Services;

use App\Enums\Difficulty;
use App\Games\GameConcept;
use App\Games\GameConceptRegistry;
use App\Models\Category;
use App\Models\Quiz;
use App\Models\SchoolLevel;
use App\Support\Like;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Http\Request;
use Illuminate\Support\Collection;

/** Read-side queries for the public site. Only ever returns available (published, in-window) quizzes. */
class Catalog
{
    public const PER_PAGE = 12;

    public function __construct(private readonly GameConceptRegistry $concepts) {}

    /** @return Collection<int, SchoolLevel> */
    public function levels(): Collection
    {
        return SchoolLevel::orderBy('position')->get();
    }

    /**
     * Subjects with their topics loaded and a `quiz_total` attribute: available quizzes in the
     * subject itself and in any of its topics.
     *
     * @return Collection<int, Category>
     */
    public function subjects(): Collection
    {
        $perCategory = Quiz::available()
            ->whereNotNull('category_id')
            ->selectRaw('category_id, count(*) as total')
            ->groupBy('category_id')
            ->pluck('total', 'category_id');

        return Category::subjects()->with('children')->get()->each(
            fn (Category $subject) => $subject->setAttribute(
                'quiz_total',
                (int) $perCategory->only($subject->withDescendantIds())->sum(),
            ),
        );
    }

    /**
     * The browse page: filters come straight from the query string and anything that does not
     * match a real subject, level or difficulty is ignored rather than rejected.
     *
     * @return array{quizzes: LengthAwarePaginator, subject: ?Category, topic: ?Category, level: ?SchoolLevel, difficulty: ?Difficulty, search: string}
     */
    public function browse(Request $request): array
    {
        $subject = $this->findBySlug(Category::subjects(), $request->string('subjek')->toString());
        $topic = $subject
            ? $subject->children->firstWhere('slug', $request->string('topik')->toString())
            : null;
        $level = SchoolLevel::where('slug', $request->string('tahap')->toString())->first();
        $difficulty = Difficulty::tryFrom($request->string('kesukaran')->toString());
        $search = trim($request->string('q')->limit(80)->toString());

        $query = Quiz::available()
            ->with(['category.parent', 'level'])
            ->withCount('questions')
            ->when($topic, fn ($q) => $q->where('category_id', $topic->id))
            ->when($subject && ! $topic, fn ($q) => $q->whereIn('category_id', $subject->withDescendantIds()))
            ->when($level, fn ($q) => $q->where('school_level_id', $level->id))
            ->when($difficulty, fn ($q) => $q->where('difficulty', $difficulty))
            ->when($search !== '', function ($q) use ($search) {
                $like = Like::contains($search);

                $q->where(fn ($w) => $w
                    ->whereRaw(Like::clause('title'), [$like])
                    ->orWhereRaw(Like::clause('summary'), [$like])
                    ->orWhereHas('tags', fn ($t) => $t->whereRaw(Like::clause('name'), [$like])));
            })
            ->orderByDesc('published_at')
            ->orderBy('title');

        return [
            'quizzes' => $query->paginate(self::PER_PAGE)->withQueryString(),
            'subject' => $subject,
            'topic' => $topic,
            'level' => $level,
            'difficulty' => $difficulty,
            'search' => $search,
        ];
    }

    /**
     * One available quiz per game concept, so the homepage can offer a real quiz to try each way of playing.
     *
     * @return list<array{concept: GameConcept, quiz: ?Quiz}>
     */
    public function conceptDemos(): array
    {
        $demos = [];

        foreach ($this->concepts->all() as $concept) {
            $demos[] = [
                'concept' => $concept,
                'quiz' => Quiz::available()->where('game_concept', $concept->key())->orderBy('id')->first(),
            ];
        }

        return $demos;
    }

    private function findBySlug($query, string $slug): ?Category
    {
        return $slug === '' ? null : $query->with('children')->where('slug', $slug)->first();
    }
}
