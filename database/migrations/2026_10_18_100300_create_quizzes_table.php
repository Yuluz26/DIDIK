<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('quizzes', function (Blueprint $table) {
            $table->id();
            $table->string('slug', 120)->unique();
            $table->string('title', 160);
            $table->text('summary')->nullable();
            // Language of the questions, so assistive tech can switch pronunciation (lang attribute).
            $table->string('language', 2)->default('ms');
            $table->foreignId('category_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('school_level_id')->nullable()->constrained()->nullOnDelete();
            $table->string('difficulty', 12)->default('sederhana');
            $table->string('status', 12)->default('draft');

            // Presentation only. Never read by scoring.
            $table->string('game_concept', 24)->default('qa');
            $table->json('game_settings')->nullable();

            // Quiz rules. Null attempts_allowed means unlimited.
            $table->unsignedTinyInteger('attempts_allowed')->nullable();
            $table->string('feedback_mode', 10)->default('instant');
            $table->boolean('shuffle_questions')->default(false);
            $table->boolean('shuffle_options')->default(false);

            $table->timestamp('available_from')->nullable();
            $table->timestamp('available_until')->nullable();
            $table->timestamp('published_at')->nullable();
            $table->foreignId('created_by')->nullable()->constrained('users')->nullOnDelete();
            $table->softDeletes();
            $table->timestamps();

            $table->index(['status', 'available_from']);
            $table->index(['category_id', 'school_level_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('quizzes');
    }
};
