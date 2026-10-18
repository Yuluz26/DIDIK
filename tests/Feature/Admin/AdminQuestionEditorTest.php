<?php

namespace Tests\Feature\Admin;

use App\Enums\QuestionType;
use App\Models\Question;
use App\Models\QuestionOption;
use App\Models\Quiz;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Str;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\Concerns\CreatesQuizzes;
use Tests\TestCase;

class AdminQuestionEditorTest extends TestCase
{
    use CreatesQuizzes, RefreshDatabase;

    protected function setUp(): void
    {
        parent::setUp();

        $this->actingAs(User::factory()->admin()->create());
    }

    /** @param  array<string, mixed>  $overrides */
    private function question(array $overrides = []): array
    {
        return array_merge([
            'type' => 'single',
            'body' => 'Berapakah 2 + 2?',
            'explanation' => 'Dua tambah dua ialah empat.',
            'points' => 1,
            'correct' => 1,
            'options' => [['body' => '3'], ['body' => '4'], ['body' => '5']],
        ], $overrides);
    }

    private function trueFalse(array $overrides = []): array
    {
        return $this->question(array_merge(['type' => 'truefalse', 'body' => 'Kucing ialah haiwan.', 'correct' => 0, 'options' => null], $overrides));
    }

    /** @param  list<array<string, mixed>>  $questions */
    private function save(Quiz $quiz, array $questions)
    {
        return $this->put(route('admin.quizzes.questions.update', $quiz), ['questions' => $questions]);
    }

    /** The rows as the editor would post them back after loading the quiz. */
    private function loaded(Quiz $quiz): array
    {
        return $quiz->questions()->with('options')->get()->map(fn (Question $q) => [
            'id' => $q->id,
            'type' => $q->type->value,
            'body' => $q->body,
            'explanation' => $q->explanation,
            'points' => $q->points,
            'correct' => max(0, $q->options->search(fn ($o) => $o->is_correct)),
            'options' => $q->options->map(fn ($o) => ['id' => $o->id, 'body' => $o->body])->values()->all(),
        ])->values()->all();
    }

    public function test_new_questions_are_saved_in_the_order_given_with_exactly_one_correct_option(): void
    {
        $quiz = Quiz::factory()->create();

        $this->save($quiz, [
            $this->question(['body' => 'Soalan pertama?', 'correct' => 2]),
            $this->question(['body' => 'Soalan kedua?', 'correct' => 0]),
        ])->assertRedirect(route('admin.quizzes.questions.edit', $quiz))->assertSessionHas('status', __('editor.saved'));

        $questions = $quiz->questions()->with('options')->get();

        $this->assertSame(['Soalan pertama?', 'Soalan kedua?'], $questions->pluck('body')->all());
        $this->assertSame([1, 2], $questions->pluck('position')->all());

        foreach ($questions as $question) {
            $this->assertSame(1, $question->options->where('is_correct', true)->count());
        }

        $this->assertSame('5', $questions[0]->options->firstWhere('is_correct', true)->body);
        $this->assertSame('3', $questions[1]->options->firstWhere('is_correct', true)->body);
        $this->assertSame(['3', '4', '5'], $questions[0]->options->pluck('body')->all());
    }

    public function test_saving_again_keeps_every_id_so_attempts_stay_valid(): void
    {
        $quiz = $this->publishedQuiz(2);
        $idsBefore = $quiz->questions()->pluck('id')->all();
        $optionIdsBefore = $quiz->questions()->with('options')->get()->flatMap->options->pluck('id')->sort()->values()->all();

        $questions = $this->loaded($quiz);
        $questions[0]['body'] = 'Soalan yang disunting?';
        $this->save($quiz, $questions)->assertSessionHasNoErrors();

        $this->assertSame($idsBefore, $quiz->questions()->pluck('id')->all());
        $this->assertSame(
            $optionIdsBefore,
            $quiz->questions()->with('options')->get()->flatMap->options->pluck('id')->sort()->values()->all(),
        );
        $this->assertSame('Soalan yang disunting?', $quiz->questions()->first()->body);
        $this->assertDatabaseCount('questions', 2);
    }

    public function test_reordering_changes_positions_but_not_ids(): void
    {
        $quiz = $this->publishedQuiz(3);
        $questions = $this->loaded($quiz);
        [$first, $second, $third] = array_column($questions, 'id');

        $this->save($quiz, [$questions[2], $questions[0], $questions[1]])->assertSessionHasNoErrors();

        $this->assertSame([$third, $first, $second], $quiz->questions()->pluck('id')->all());
        $this->assertSame([1, 2, 3], $quiz->questions()->pluck('position')->all());
    }

    public function test_removing_a_question_hides_it_but_keeps_what_children_answered(): void
    {
        $quiz = $this->publishedQuiz(2);
        $questions = $this->loaded($quiz);
        $attempt = $quiz->attempts()->create([
            'uuid' => (string) Str::uuid(), 'session_hash' => str_repeat('a', 64),
            'layout' => ['questions' => [], 'options' => []], 'started_at' => now(),
        ]);
        $attempt->answers()->create([
            'question_id' => $questions[1]['id'], 'option_id' => $questions[1]['options'][0]['id'],
            'is_correct' => true, 'points_awarded' => 1, 'answered_at' => now(),
        ]);

        $this->save($quiz, [$questions[0]])->assertSessionHasNoErrors();

        $this->assertSame([$questions[0]['id']], $quiz->questions()->pluck('id')->all());
        $this->assertSoftDeleted('questions', ['id' => $questions[1]['id']]);
        $this->assertDatabaseCount('attempt_answers', 1);
    }

    public function test_an_empty_list_removes_every_question(): void
    {
        $quiz = $this->publishedQuiz(2);

        $this->put(route('admin.quizzes.questions.update', $quiz), [])->assertSessionHasNoErrors();

        $this->assertSame(0, $quiz->questions()->count());
        $this->assertDatabaseCount('questions', 2);   // soft deleted, not erased
    }

    public function test_a_true_false_question_gets_two_fixed_options(): void
    {
        $quiz = Quiz::factory()->create();

        $this->save($quiz, [
            $this->trueFalse(['correct' => 0]),
            $this->trueFalse(['body' => 'Ikan boleh terbang.', 'correct' => 1]),
        ])->assertSessionHasNoErrors();

        $questions = $quiz->questions()->with('options')->get();

        $this->assertSame(QuestionType::TrueFalse, $questions[0]->type);
        $this->assertSame([__('enums.true_false.true'), __('enums.true_false.false')], $questions[0]->options->pluck('body')->all());
        $this->assertSame([true, false], $questions[0]->options->pluck('is_correct')->all());
        $this->assertSame([false, true], $questions[1]->options->pluck('is_correct')->all());
    }

    public function test_switching_a_question_to_true_false_and_back_loses_nothing_it_should_keep(): void
    {
        $quiz = $this->publishedQuiz(1);
        $original = $this->loaded($quiz)[0];

        // Multiple choice -> true/false: two rows are reused, the third is removed.
        $this->save($quiz, [array_merge($original, ['type' => 'truefalse', 'correct' => 1, 'options' => null])])
            ->assertSessionHasNoErrors();

        $question = $quiz->questions()->with('options')->first();
        $this->assertSame($original['id'], $question->id);
        $this->assertSame(2, $question->options->count());
        $this->assertSame([false, true], $question->options->pluck('is_correct')->all());
        $this->assertSame(
            [$original['options'][0]['id'], $original['options'][1]['id']],
            $question->options->pluck('id')->all(),
        );

        // True/false -> multiple choice again with fresh options.
        $this->save($quiz, [$this->question(['id' => $original['id'], 'correct' => 2])])->assertSessionHasNoErrors();

        $question = $quiz->questions()->with('options')->first();
        $this->assertSame(QuestionType::Single, $question->type);
        $this->assertSame(3, $question->options->count());
        $this->assertSame(1, $question->options->where('is_correct', true)->count());
        $this->assertSame('5', $question->options->firstWhere('is_correct', true)->body);
    }

    public function test_the_correct_answer_can_move_to_another_option_without_breaking_the_one_correct_rule(): void
    {
        $quiz = $this->publishedQuiz(1);
        $question = $this->loaded($quiz)[0];

        foreach ([2, 1, 0] as $correct) {
            $this->save($quiz, [array_merge($question, ['correct' => $correct])])->assertSessionHasNoErrors();

            $options = $quiz->questions()->first()->options()->get();
            $this->assertSame(1, $options->where('is_correct', true)->count());
            $this->assertTrue($options[$correct]->is_correct);
        }
    }

    public function test_ids_from_another_quiz_are_ignored_and_that_quiz_is_left_alone(): void
    {
        $mine = Quiz::factory()->create();
        $other = $this->publishedQuiz(1, ['title' => 'Kuiz Lain']);
        $foreign = $this->loaded($other)[0];

        $this->save($mine, [array_merge($foreign, ['body' => 'Cubaan merampas soalan?'])])->assertSessionHasNoErrors();

        // The foreign question is untouched, and mine got a brand new question and brand new options.
        $this->assertNotSame('Cubaan merampas soalan?', Question::find($foreign['id'])->body);
        $this->assertSame(1, $other->questions()->count());

        $created = $mine->questions()->with('options')->firstOrFail();
        $this->assertNotSame($foreign['id'], $created->id);
        $this->assertEmpty(array_intersect($created->options->pluck('id')->all(), array_column($foreign['options'], 'id')));
    }

    public function test_an_option_id_from_another_question_is_ignored(): void
    {
        $quiz = $this->publishedQuiz(2);
        $questions = $this->loaded($quiz);
        $stolen = $questions[1]['options'][0];
        $second = $questions[1];

        $questions[0]['options'][0] = ['id' => $stolen['id'], 'body' => 'Dirampas'];
        $this->save($quiz, $questions)->assertSessionHasNoErrors();

        // The option still belongs to the second question with its own text.
        $this->assertSame($second['options'][0]['body'], QuestionOption::find($stolen['id'])->body);
        $this->assertSame($second['id'], QuestionOption::find($stolen['id'])->question_id);
    }

    public function test_html_in_a_question_is_stored_as_text_and_never_rendered_as_markup(): void
    {
        $quiz = Quiz::factory()->create();
        $payload = '<script>alert(1)</script><img src=x onerror=alert(2)>';

        $this->save($quiz, [$this->question(['body' => $payload, 'explanation' => $payload])])->assertSessionHasNoErrors();

        $this->assertSame($payload, $quiz->questions()->first()->body);

        $page = $this->get(route('admin.quizzes.questions.edit', $quiz))->assertOk();
        $page->assertDontSee('<script>alert(1)</script>', false);
        $page->assertDontSee('<img src=x onerror=alert(2)>', false);
    }

    public function test_the_editor_page_lists_current_questions_and_options(): void
    {
        $quiz = $this->publishedQuiz(2);

        $this->get(route('admin.quizzes.questions.edit', $quiz))
            ->assertOk()
            ->assertSee($quiz->questions()->first()->body, false)
            ->assertSee(__('editor.save_all'));
    }

    public function test_errors_name_the_question_not_a_form_path(): void
    {
        $quiz = Quiz::factory()->create();

        $response = $this->from(route('admin.quizzes.questions.edit', $quiz))->save($quiz, [
            $this->question(),
            $this->question(['body' => '']),
        ]);

        $response->assertRedirect(route('admin.quizzes.questions.edit', $quiz))->assertSessionHasErrors('questions.1.body');

        $message = session('errors')->first('questions.1.body');
        $this->assertStringContainsString('Soalan 2', $message);
        $this->assertStringNotContainsString('questions.1', $message);
        $this->assertSame(0, $quiz->questions()->count(), 'a failed save must not write anything');
    }

    /** @return array<string, array{array<string, mixed>, string}> */
    public static function invalidQuestions(): array
    {
        return [
            'unknown type' => [['type' => 'essay'], 'questions.0.type'],
            'missing body' => [['body' => ''], 'questions.0.body'],
            'body too long' => [['body' => str_repeat('a', 1001)], 'questions.0.body'],
            'explanation too long' => [['explanation' => str_repeat('a', 1001)], 'questions.0.explanation'],
            'no points' => [['points' => 0], 'questions.0.points'],
            'too many points' => [['points' => 11], 'questions.0.points'],
            'one option only' => [['options' => [['body' => 'Satu']], 'correct' => 0], 'questions.0.options'],
            'six options' => [['options' => array_fill(0, 6, ['body' => 'x']), 'correct' => 0], 'questions.0.options'],
            'empty option' => [['options' => [['body' => 'A'], ['body' => ''], ['body' => 'C']]], 'questions.0.options.1.body'],
            'correct index out of range' => [['correct' => 3], 'questions.0.correct'],
            'negative correct index' => [['correct' => -1], 'questions.0.correct'],
            'no correct answer chosen' => [['correct' => null], 'questions.0.correct'],
        ];
    }

    /** @param  array<string, mixed>  $overrides */
    #[DataProvider('invalidQuestions')]
    public function test_invalid_questions_are_rejected_and_nothing_is_written(array $overrides, string $errorKey): void
    {
        $quiz = Quiz::factory()->create();

        $this->save($quiz, [$this->question($overrides)])->assertSessionHasErrors($errorKey);

        $this->assertSame(0, Question::count());
    }

    public function test_true_false_needs_a_valid_answer(): void
    {
        $quiz = Quiz::factory()->create();

        $this->save($quiz, [$this->trueFalse(['correct' => 2])])->assertSessionHasErrors('questions.0.correct');
        $this->save($quiz, [$this->trueFalse(['correct' => null])])->assertSessionHasErrors('questions.0.correct');
        $this->assertSame(0, Question::count());
    }

    public function test_a_quiz_has_a_question_limit(): void
    {
        $quiz = Quiz::factory()->create();

        $this->save($quiz, array_fill(0, 101, $this->question()))->assertSessionHasErrors('questions');
        $this->assertSame(0, Question::count());
    }

    public function test_a_failed_save_leaves_existing_questions_exactly_as_they_were(): void
    {
        $quiz = $this->publishedQuiz(2);
        $before = $this->loaded($quiz);
        $broken = $before;
        $broken[1]['body'] = '';

        $this->save($quiz, $broken)->assertSessionHasErrors('questions.1.body');

        $this->assertEquals($before, $this->loaded($quiz));
    }
}
