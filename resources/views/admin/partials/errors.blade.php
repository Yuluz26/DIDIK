{{--
    One summary of every problem on a form, placed at the top. It takes focus when the page loads
    after a failed save, and each item links to its field. Inline messages stay beside the fields.
--}}
@if ($errors->any())
    @php($count = $errors->count())
    <div class="error-summary" role="alert" tabindex="-1" x-data x-init="$el.focus()">
        <h2>{{ $count === 1 ? __('admin.common.error_summary_one') : __('admin.common.error_summary', ['count' => $count]) }}</h2>
        <ul>
            @foreach ($errors->keys() as $key)
                @foreach ($errors->get($key) as $message)
                    <li><a href="#{{ $anchors[$key] ?? str_replace('.', '-', $key) }}">{{ $message }}</a></li>
                @endforeach
            @endforeach
        </ul>
    </div>
@endif
