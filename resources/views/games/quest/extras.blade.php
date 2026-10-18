<section class="stage__panel checkpoint" x-show="isCheckpoint" x-cloak role="status">
    <x-mascot mood="cheer" size="lg" />
    <h2 class="stage__title" x-text="checkpointTitle"></h2>
    <p x-show="checkpointText !== ''" x-text="checkpointText"></p>
    <button type="button" class="btn btn--primary" x-ref="continue" @click="continueLevel()">
        {{ __('public.player.quest.continue') }}
        <x-icon name="arrow-right" />
    </button>
</section>
