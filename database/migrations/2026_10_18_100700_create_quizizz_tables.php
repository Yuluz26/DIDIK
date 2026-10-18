<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('quizizz_links', function (Blueprint $table) {
            $table->id();
            $table->string('title', 160);
            $table->string('url', 500);
            $table->text('description')->nullable();
            $table->foreignId('category_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('school_level_id')->nullable()->constrained()->nullOnDelete();
            $table->string('thumbnail_path')->nullable();
            $table->string('status', 12)->default('draft')->index();
            $table->softDeletes();
            $table->timestamps();
        });

        Schema::create('quizizz_collections', function (Blueprint $table) {
            $table->id();
            $table->string('title', 120);
            $table->string('slug', 140)->unique();
            $table->text('description')->nullable();
            $table->string('status', 12)->default('draft')->index();
            $table->unsignedSmallInteger('position')->default(0);
            $table->timestamps();
        });

        Schema::create('quizizz_collection_link', function (Blueprint $table) {
            $table->foreignId('quizizz_collection_id')->constrained()->cascadeOnDelete();
            $table->foreignId('quizizz_link_id')->constrained()->cascadeOnDelete();
            $table->unsignedSmallInteger('position')->default(0);

            $table->primary(['quizizz_collection_id', 'quizizz_link_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('quizizz_collection_link');
        Schema::dropIfExists('quizizz_collections');
        Schema::dropIfExists('quizizz_links');
    }
};
