<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * The dashboard counts attempts started or finished in the last seven days, and the retention
 * command removes attempts older than a cut-off. Without these two indexes every such query reads
 * the whole table, which grows with every child who plays.
 */
return new class extends Migration
{
    public function up(): void
    {
        Schema::table('attempts', function (Blueprint $table) {
            $table->index('started_at');
            $table->index('completed_at');
        });
    }

    public function down(): void
    {
        Schema::table('attempts', function (Blueprint $table) {
            $table->dropIndex(['started_at']);
            $table->dropIndex(['completed_at']);
        });
    }
};
