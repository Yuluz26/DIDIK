{{--
    A delete button that asks first. It opens a native dialog with the item's name in it; only the
    button inside the dialog sends the request. Needs: $action (URL), $name, optional $text.
--}}
@php($dialogId = 'delete-'.md5($action))

<button type="button" class="btn btn--sm" data-dialog-open="{{ $dialogId }}" aria-haspopup="dialog">
    <x-icon name="trash-2" /> {{ __('admin.common.delete') }}<span class="visually-hidden">: {{ $name }}</span>
</button>

<dialog class="dialog" id="{{ $dialogId }}" aria-labelledby="{{ $dialogId }}-title">
    <h2 id="{{ $dialogId }}-title" class="dialog__title">{{ __('admin.common.confirm_delete_title', ['name' => $name]) }}</h2>
    <p>{{ $text ?: __('admin.common.confirm_delete_text') }}</p>
    <form method="post" action="{{ $action }}" class="dialog__actions">
        @csrf
        @method('DELETE')
        <button type="button" class="btn" data-dialog-close>{{ __('admin.common.cancel') }}</button>
        <button type="submit" class="btn btn--danger"><x-icon name="trash-2" /> {{ __('admin.common.delete') }}</button>
    </form>
</dialog>
