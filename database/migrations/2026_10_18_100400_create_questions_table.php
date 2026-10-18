<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('questions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('quiz_id')->constrained()->cascadeOnDelete();
            $table->string('type', 12)->default('single');
            $table->text('body');
            $table->text('explanation')->nullable();
            $table->unsignedTinyInteger('points')->default(1);
            $table->unsignedSmallInteger('position')->default(0);
            $table->softDeletes();
            $table->timestamps();

            $table->index(['quiz_id', 'position']);
        });

        Schema::create('question_options', function (Blueprint $table) {
            $table->id();
            $table->foreignId('question_id')->constrained()->cascadeOnDelete();
            $table->string('body', 255);
            $table->boolean('is_correct')->default(false);
            $table->unsignedTinyInteger('position')->default(0);
            $table->softDeletes();
            $table->timestamps();

            // Generated column: holds the question id only for a live correct option, so the
            // unique index below lets the database enforce "at most one correct option".
            $table->unsignedBigInteger('correct_guard')
                ->nullable()
                ->virtualAs('CASE WHEN is_correct = 1 AND deleted_at IS NULL THEN question_id END')
                ->unique();

            $table->index(['question_id', 'position']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('question_options');
        Schema::dropIfExists('questions');
    }
};
