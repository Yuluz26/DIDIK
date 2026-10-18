<?php

namespace Database\Seeders;

use App\Enums\CategoryType;
use App\Enums\Difficulty;
use App\Enums\LinkStatus;
use App\Enums\QuestionType;
use App\Enums\QuizStatus;
use App\Models\Category;
use App\Models\Quiz;
use App\Models\QuizizzCollection;
use App\Models\QuizizzLink;
use App\Models\SchoolLevel;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Str;

/**
 * Sample quizzes and Quizizz links so the product can be seen working in local development.
 * Refuses to run in production. Idempotent: a quiz or link that already exists is left alone.
 *
 * The Quizizz links are placeholders in the right shape, not real activities.
 */
class DemoContentSeeder extends Seeder
{
    public function run(): void
    {
        if (app()->isProduction()) {
            $this->command?->warn('Demo content is never seeded in production. Nothing was changed.');

            return;
        }

        $this->call(ReferenceDataSeeder::class);

        DB::transaction(function () {
            $this->topics();

            foreach ($this->quizzes() as $data) {
                $this->createQuiz($data);
            }

            $this->quizizz();
        });
    }

    private function topics(): void
    {
        $topics = [
            'matematik' => ['Tambah dan Tolak', 'Bentuk', 'Wang'],
            'sains' => ['Haiwan', 'Tumbuhan'],
            'bahasa-melayu' => ['Suku Kata'],
            'bahasa-inggeris' => ['Animals and Colours'],
        ];

        foreach ($topics as $subjectSlug => $names) {
            $subject = Category::where('slug', $subjectSlug)->firstOrFail();

            foreach ($names as $position => $name) {
                Category::updateOrCreate(
                    ['slug' => Str::slug($name)],
                    [
                        'parent_id' => $subject->id,
                        'type' => CategoryType::Topic,
                        'name' => $name,
                        'theme' => $subject->theme,
                        'icon' => $subject->icon,
                        'position' => $position + 1,
                    ],
                );
            }
        }
    }

    private function createQuiz(array $data): void
    {
        if (Quiz::withTrashed()->where('title', $data['title'])->exists()) {
            return;
        }

        $quiz = Quiz::create([
            'title' => $data['title'],
            'summary' => $data['summary'],
            'language' => $data['language'] ?? 'ms',
            'category_id' => Category::where('slug', Str::slug($data['topic']))->value('id'),
            'school_level_id' => SchoolLevel::where('slug', $data['level'])->value('id'),
            'difficulty' => $data['difficulty'],
            'status' => $data['status'] ?? QuizStatus::Published,
            'published_at' => ($data['status'] ?? QuizStatus::Published) === QuizStatus::Published ? now() : null,
            'game_concept' => $data['concept'],
            'game_settings' => $data['settings'] ?? [],
            'attempts_allowed' => $data['attempts'] ?? null,
        ]);

        $quiz->syncTagNames($data['tags'] ?? '');

        foreach ($data['questions'] as $index => $item) {
            $isTrueFalse = array_key_exists('tf', $item);

            $question = $quiz->questions()->create([
                'type' => $isTrueFalse ? QuestionType::TrueFalse : QuestionType::Single,
                'body' => $item['q'],
                'explanation' => $item['why'] ?? null,
                'points' => $item['points'] ?? 1,
                'position' => $index + 1,
            ]);

            $options = $isTrueFalse ? ['Betul', 'Salah'] : $item['options'];
            $correct = $isTrueFalse ? ($item['tf'] ? 0 : 1) : $item['answer'];

            foreach ($options as $position => $text) {
                $question->options()->create([
                    'body' => $text,
                    'is_correct' => $position === $correct,
                    'position' => $position + 1,
                ]);
            }
        }
    }

    /** @return list<array<string, mixed>> */
    private function quizzes(): array
    {
        return [
            [
                'title' => 'Tambah Sampai 10',
                'summary' => 'Latihan tambah nombor kecil. Kira dengan jari kalau perlu.',
                'topic' => 'Tambah dan Tolak',
                'level' => 'tahun-1',
                'difficulty' => Difficulty::Easy,
                'concept' => 'stars',
                'settings' => ['show_streak' => true],
                'tags' => 'tambah, nombor',
                'questions' => [
                    ['q' => '2 + 3 = ?', 'options' => ['4', '5', '6'], 'answer' => 1, 'why' => 'Mula dari 2, kira tiga lagi: 3, 4, 5. Jawapannya 5.'],
                    ['q' => '4 + 4 = ?', 'options' => ['6', '8', '9'], 'answer' => 1, 'why' => '4 dan 4 ialah dua kumpulan yang sama banyak. Jumlahnya 8.'],
                    ['q' => '7 + 2 = ?', 'options' => ['8', '9', '10'], 'answer' => 1, 'why' => 'Mula dari 7, kira dua lagi: 8, 9.'],
                    ['q' => '5 + 5 = ?', 'options' => ['9', '10', '11'], 'answer' => 1, 'why' => 'Lima jari tangan kiri dan lima jari tangan kanan ialah 10.'],
                    ['q' => '6 + 3 = ?', 'options' => ['8', '9', '10'], 'answer' => 1, 'why' => 'Mula dari 6, kira tiga lagi: 7, 8, 9.'],
                    ['q' => '1 + 8 = ?', 'options' => ['7', '9', '10'], 'answer' => 1, 'why' => '1 + 8 sama dengan 8 + 1. Jawapannya 9.'],
                    ['q' => 'Ali ada 3 biji epal. Ibu beri 4 biji lagi. Berapa biji epal Ali sekarang?', 'options' => ['6', '7', '8'], 'answer' => 1, 'why' => '3 tambah 4 sama dengan 7.'],
                    ['q' => '9 + 1 = ?', 'options' => ['8', '10', '11'], 'answer' => 1, 'why' => 'Satu lagi selepas 9 ialah 10.'],
                ],
            ],
            [
                'title' => 'Tolak dengan Mudah',
                'summary' => 'Tolak nombor sehingga 20, satu langkah demi satu langkah.',
                'topic' => 'Tambah dan Tolak',
                'level' => 'tahun-2',
                'difficulty' => Difficulty::Medium,
                'concept' => 'quest',
                'settings' => ['level_size' => 4],
                'tags' => 'tolak, nombor',
                'questions' => [
                    ['q' => '9 − 4 = ?', 'options' => ['4', '5', '6'], 'answer' => 1, 'why' => 'Undur 4 langkah dari 9: 8, 7, 6, 5.'],
                    ['q' => '10 − 3 = ?', 'options' => ['6', '7', '8'], 'answer' => 1, 'why' => 'Undur 3 langkah dari 10: 9, 8, 7.'],
                    ['q' => '15 − 5 = ?', 'options' => ['8', '10', '12'], 'answer' => 1, 'why' => '15 tolak 5 meninggalkan 10.'],
                    ['q' => '12 − 6 = ?', 'options' => ['5', '6', '7'], 'answer' => 1, 'why' => '6 + 6 = 12, jadi 12 − 6 = 6.'],
                    ['q' => 'Ada 8 ekor burung di atas pokok. 3 ekor terbang pergi. Berapa ekor yang tinggal?', 'options' => ['4', '5', '6'], 'answer' => 1, 'why' => '8 tolak 3 sama dengan 5.'],
                    ['q' => '20 − 10 = ?', 'options' => ['5', '10', '15'], 'answer' => 1, 'why' => 'Separuh daripada 20 ialah 10.'],
                    ['q' => '14 − 7 = ?', 'options' => ['6', '7', '8'], 'answer' => 1, 'why' => '7 + 7 = 14, jadi 14 − 7 = 7.'],
                    ['q' => '18 − 9 = ?', 'options' => ['8', '9', '10'], 'answer' => 1, 'why' => '9 + 9 = 18, jadi 18 − 9 = 9.'],
                ],
            ],
            [
                'title' => 'Haiwan Sekeliling Kita',
                'summary' => 'Kenali haiwan, makanan dan cara mereka hidup.',
                'topic' => 'Haiwan',
                'level' => 'tahun-2',
                'difficulty' => Difficulty::Easy,
                'concept' => 'qa',
                'settings' => ['progress' => 'dots'],
                'tags' => 'haiwan, sains',
                'questions' => [
                    ['q' => 'Haiwan manakah yang bertelur?', 'options' => ['Ayam', 'Kucing', 'Lembu'], 'answer' => 0, 'why' => 'Ayam bertelur. Kucing dan lembu melahirkan anak.'],
                    ['q' => 'Anak katak dipanggil apa?', 'options' => ['Berudu', 'Ulat', 'Telur'], 'answer' => 0, 'why' => 'Telur katak menetas menjadi berudu. Berudu membesar menjadi katak.'],
                    ['q' => 'Haiwan manakah yang boleh terbang?', 'options' => ['Ikan', 'Burung', 'Lembu'], 'answer' => 1, 'why' => 'Burung ada sayap dan bulu untuk terbang.'],
                    ['q' => 'Apakah makanan kambing?', 'options' => ['Rumput', 'Daging', 'Ikan'], 'answer' => 0, 'why' => 'Kambing makan tumbuhan seperti rumput dan daun.'],
                    ['q' => 'Ikan bernafas menggunakan apa?', 'options' => ['Hidung', 'Insang', 'Telinga'], 'answer' => 1, 'why' => 'Insang membantu ikan mengambil udara yang larut dalam air.'],
                    ['q' => 'Kucing menyusukan anaknya.', 'tf' => true, 'why' => 'Kucing ialah mamalia. Anak kucing minum susu ibunya.'],
                    ['q' => 'Semua burung boleh terbang.', 'tf' => false, 'why' => 'Burung unta dan penguin ialah burung, tetapi tidak boleh terbang.'],
                ],
            ],
            [
                'title' => 'Bahagian Tumbuhan',
                'summary' => 'Akar, batang, daun dan bunga: apa kerja setiap satu?',
                'topic' => 'Tumbuhan',
                'level' => 'tahun-3',
                'difficulty' => Difficulty::Medium,
                'concept' => 'qa',
                'settings' => ['progress' => 'bar'],
                'tags' => 'tumbuhan, sains',
                'questions' => [
                    ['q' => 'Bahagian tumbuhan manakah yang menyerap air dari tanah?', 'options' => ['Daun', 'Akar', 'Bunga'], 'answer' => 1, 'why' => 'Akar menyerap air dan garam mineral dari tanah.'],
                    ['q' => 'Daun membuat makanan dengan bantuan apa?', 'options' => ['Cahaya matahari', 'Angin', 'Bunyi'], 'answer' => 0, 'why' => 'Daun menggunakan cahaya matahari, air dan udara untuk membuat makanan.'],
                    ['q' => 'Bahagian manakah yang boleh menjadi buah?', 'options' => ['Akar', 'Bunga', 'Batang'], 'answer' => 1, 'why' => 'Selepas diserbuk, bunga boleh membesar menjadi buah.'],
                    ['q' => 'Batang menyokong tumbuhan supaya tegak.', 'tf' => true, 'why' => 'Batang juga mengangkut air dan makanan ke seluruh tumbuhan.'],
                    ['q' => 'Apakah yang diperlukan oleh tumbuhan untuk hidup?', 'options' => ['Air, udara dan cahaya matahari', 'Gula dan garam', 'Bunyi dan angin'], 'answer' => 0, 'why' => 'Tanpa air, udara dan cahaya matahari, tumbuhan tidak dapat membesar.'],
                    ['q' => 'Biji benih yang ditanam dan disiram akan tumbuh menjadi apa?', 'options' => ['Batu', 'Anak pokok', 'Pasir'], 'answer' => 1, 'why' => 'Biji benih bercambah dan menjadi anak pokok.'],
                ],
            ],
            [
                'title' => 'Suku Kata Seronok',
                'summary' => 'Sebut perlahan-lahan dan kira suku katanya.',
                'topic' => 'Suku Kata',
                'level' => 'tahun-1',
                'difficulty' => Difficulty::Easy,
                'concept' => 'stars',
                'settings' => ['show_streak' => false],
                'tags' => 'suku kata, bahasa',
                'questions' => [
                    ['q' => 'Berapakah suku kata dalam perkataan “bola”?', 'options' => ['1 suku kata', '2 suku kata', '3 suku kata'], 'answer' => 1, 'why' => 'bo-la. Ada dua suku kata.'],
                    ['q' => 'Berapakah suku kata dalam perkataan “sekolah”?', 'options' => ['1 suku kata', '2 suku kata', '3 suku kata'], 'answer' => 2, 'why' => 'se-ko-lah. Ada tiga suku kata.'],
                    ['q' => 'Berapakah suku kata dalam perkataan “ibu”?', 'options' => ['1 suku kata', '2 suku kata', '3 suku kata'], 'answer' => 1, 'why' => 'i-bu. Ada dua suku kata.'],
                    ['q' => 'Berapakah suku kata dalam perkataan “makanan”?', 'options' => ['2 suku kata', '3 suku kata', '4 suku kata'], 'answer' => 1, 'why' => 'ma-ka-nan. Ada tiga suku kata.'],
                    ['q' => 'Berapakah suku kata dalam perkataan “kucing”?', 'options' => ['1 suku kata', '2 suku kata', '3 suku kata'], 'answer' => 1, 'why' => 'ku-cing. Ada dua suku kata.'],
                    ['q' => 'Berapakah suku kata dalam perkataan “komputer”?', 'options' => ['2 suku kata', '3 suku kata', '4 suku kata'], 'answer' => 1, 'why' => 'kom-pu-ter. Ada tiga suku kata.'],
                ],
            ],
            [
                'title' => 'Colours and Animals',
                'summary' => 'Easy English words for colours and animals.',
                'language' => 'en',
                'topic' => 'Animals and Colours',
                'level' => 'tahun-1',
                'difficulty' => Difficulty::Easy,
                'concept' => 'qa',
                'settings' => ['progress' => 'dots'],
                'tags' => 'english, colours, animals',
                'questions' => [
                    ['q' => 'What colour is a banana?', 'options' => ['Yellow', 'Blue', 'Black'], 'answer' => 0, 'why' => 'A ripe banana is yellow. Kuning.'],
                    ['q' => 'Which animal says “meow”?', 'options' => ['Cow', 'Cat', 'Fish'], 'answer' => 1, 'why' => 'A cat says meow. Kucing.'],
                    ['q' => 'What colour is the sky on a sunny day?', 'options' => ['Green', 'Blue', 'Pink'], 'answer' => 1, 'why' => 'The sky is blue. Biru.'],
                    ['q' => 'Which animal gives us milk?', 'options' => ['Cow', 'Fish', 'Bird'], 'answer' => 0, 'why' => 'A cow gives us milk. Lembu.'],
                    ['q' => 'How many legs does a bird have?', 'options' => ['Two', 'Four', 'Six'], 'answer' => 0, 'why' => 'A bird has two legs. Dua kaki.'],
                    ['q' => 'What is “ikan” in English?', 'options' => ['Bird', 'Fish', 'Cat'], 'answer' => 1, 'why' => '“Ikan” is fish.'],
                    ['q' => 'An apple is a fruit.', 'tf' => true, 'why' => 'Yes, an apple is a fruit. Epal ialah buah.'],
                ],
            ],
            [
                'title' => 'Bentuk di Sekeliling Kita',
                'summary' => 'Cari bulatan, segi tiga dan segi empat di sekeliling rumah.',
                'topic' => 'Bentuk',
                'level' => 'prasekolah',
                'difficulty' => Difficulty::Easy,
                'concept' => 'quest',
                'settings' => ['level_size' => 3],
                'tags' => 'bentuk, matematik',
                'questions' => [
                    ['q' => 'Roda berbentuk apa?', 'options' => ['Bulatan', 'Segi tiga', 'Segi empat'], 'answer' => 0, 'why' => 'Roda berbentuk bulatan supaya mudah bergolek.'],
                    ['q' => 'Berapakah sisi bagi segi tiga?', 'options' => ['2', '3', '4'], 'answer' => 1, 'why' => 'Segi tiga ada tiga sisi dan tiga sudut.'],
                    ['q' => 'Berapakah sisi bagi segi empat sama?', 'options' => ['3', '4', '5'], 'answer' => 1, 'why' => 'Segi empat sama ada empat sisi yang sama panjang.'],
                    ['q' => 'Bentuk manakah yang tidak ada sudut?', 'options' => ['Bulatan', 'Segi tiga', 'Segi empat'], 'answer' => 0, 'why' => 'Bulatan hanya ada satu sisi yang melengkung.'],
                    ['q' => 'Bendera Malaysia berbentuk segi empat tepat.', 'tf' => true, 'why' => 'Jalur Gemilang berbentuk segi empat tepat.'],
                    ['q' => 'Bulan penuh kelihatan seperti bentuk apa?', 'options' => ['Segi empat', 'Bulatan', 'Segi tiga'], 'answer' => 1, 'why' => 'Bulan purnama kelihatan bulat.'],
                ],
            ],
            [
                'title' => 'Wang dan Duit',
                'summary' => 'Sen dan ringgit dalam kehidupan seharian. (Draf)',
                'topic' => 'Wang',
                'level' => 'tahun-2',
                'difficulty' => Difficulty::Medium,
                'status' => QuizStatus::Draft,
                'concept' => 'qa',
                'settings' => [],
                'questions' => [
                    ['q' => '50 sen + 50 sen = ?', 'options' => ['RM1', 'RM2', '75 sen'], 'answer' => 0, 'why' => '100 sen sama dengan RM1.'],
                    ['q' => 'Kamu ada RM5. Kamu beli sebatang pensel RM2. Berapa baki wang kamu?', 'options' => ['RM2', 'RM3', 'RM7'], 'answer' => 1, 'why' => 'RM5 tolak RM2 sama dengan RM3.'],
                ],
            ],
        ];
    }

    private function quizizz(): void
    {
        $note = 'Pautan contoh. Gantikan dengan pautan Quizizz anda sendiri.';

        $links = [
            ['Latihan Tambah dan Tolak', 'matematik', 'tahun-1', LinkStatus::Published, 'contoh-tambah-tolak', 'tambah, tolak'],
            ['Darab Jadual 2 dan 5', 'matematik', 'tahun-3', LinkStatus::Published, 'contoh-darab-2-5', 'darab'],
            ['Pecahan untuk Pemula', 'matematik', 'tahun-4', LinkStatus::Published, 'contoh-pecahan', 'pecahan'],
            ['Kitaran Hidup Haiwan', 'sains', 'tahun-3', LinkStatus::Published, 'contoh-kitaran-hidup', 'haiwan'],
            ['Bahagian Badan Kita', 'sains', 'tahun-1', LinkStatus::Published, 'contoh-badan-kita', 'badan'],
            ['Imbuhan Awalan', 'bahasa-melayu', 'tahun-4', LinkStatus::Broken, 'contoh-imbuhan', 'imbuhan'],
            ['Cerita Pendek Tahun 2', 'bahasa-melayu', 'tahun-2', LinkStatus::Draft, 'contoh-cerita-pendek', 'bacaan'],
        ];

        $created = [];

        foreach ($links as [$title, $subject, $level, $status, $slug, $tags]) {
            $link = QuizizzLink::firstOrCreate(
                ['url' => "https://quizizz.com/admin/quiz/{$slug}"],
                [
                    'title' => $title,
                    'description' => $note,
                    'category_id' => Category::where('slug', $subject)->value('id'),
                    'school_level_id' => SchoolLevel::where('slug', $level)->value('id'),
                    'status' => $status,
                ],
            );

            if ($link->wasRecentlyCreated) {
                $link->syncTagNames($tags);
            }

            $created[$slug] = $link;
        }

        $collections = [
            ['Latihan Tambahan Matematik', 'Pilihan latihan Matematik untuk diulang di rumah.', LinkStatus::Published, 1, ['contoh-tambah-tolak', 'contoh-darab-2-5', 'contoh-pecahan']],
            ['Sains Seronok', 'Haiwan dan badan kita dalam bentuk kuiz.', LinkStatus::Published, 2, ['contoh-kitaran-hidup', 'contoh-badan-kita']],
            ['Bahasa Melayu (draf)', 'Belum siap diterbitkan.', LinkStatus::Draft, 3, ['contoh-imbuhan', 'contoh-cerita-pendek']],
        ];

        foreach ($collections as [$title, $description, $status, $position, $slugs]) {
            $collection = QuizizzCollection::firstOrCreate(
                ['title' => $title],
                ['description' => $description, 'status' => $status, 'position' => $position],
            );

            if ($collection->wasRecentlyCreated) {
                foreach ($slugs as $order => $slug) {
                    $collection->links()->attach($created[$slug]->id, ['position' => $order + 1]);
                }
            }
        }
    }
}
