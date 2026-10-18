<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('attempts', function (Blueprint $table) {
            $table->id();
            $table->uuid('uuid')->unique();
            $table->foreignId('quiz_id')->constrained()->restrictOnDelete();
            // HMAC of the session id. The raw session id is never stored.
            $table->char('session_hash', 64);
            // Question and option order chosen when the attempt started, so a refresh resumes safely.
            $table->json('layout');
            $table->timestamp('started_at');
            $table->timestamp('completed_at')->nullable();
            $table->unsignedSmallInteger('score')->default(0);
            $table->unsignedSmallInteger('max_score')->default(0);
            $table->unsignedSmallInteger('correct_count')->default(0);
            $table->unsignedSmallInteger('question_count')->default(0);
            $table->unsignedTinyInteger('stars')->nullable();
            $table->timestamps();

            $table->index(['quiz_id', 'completed_at']);
            $table->index(['session_hash', 'quiz_id']);
        });

        Schema::create('attempt_answers', function (Blueprint $table) {
            $table->id();
            $table->foreignId('attempt_id')->constrained()->cascadeOnDelete();
            $table->foreignId('question_id')->constrained()->restrictOnDelete();
            $table->foreignId('option_id')->constrained('question_options')->restrictOnDelete();
            $table->boolean('is_correct');
            $table->unsignedTinyInteger('points_awarded')->default(0);
            $table->timestamp('answered_at');

            $table->unique(['attempt_id', 'question_id']);
            $table->index(['question_id', 'is_correct']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('attempt_answers');
        Schema::dropIfExists('attempts');
    }
};
