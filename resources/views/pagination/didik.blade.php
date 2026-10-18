@if ($paginator->hasPages())
    <nav aria-label="{{ __('public.pagination.label') }}">
        <ul class="pager">
            <li>
                @if ($paginator->onFirstPage())
                    <span class="btn btn--sm" aria-disabled="true"><x-icon name="chevron-left" /> {{ __('public.pagination.previous') }}</span>
                @else
                    <a class="btn btn--sm" href="{{ $paginator->previousPageUrl() }}" rel="prev"><x-icon name="chevron-left" /> {{ __('public.pagination.previous') }}</a>
                @endif
            </li>

            @foreach ($elements as $element)
                @if (is_string($element))
                    <li aria-hidden="true">{{ $element }}</li>
                @endif

                @if (is_array($element))
                    @foreach ($element as $page => $url)
                        <li>
                            @if ($page === $paginator->currentPage())
                                <span class="chip" aria-current="page" aria-label="{{ __('public.pagination.page', ['page' => $page]) }}">{{ $page }}</span>
                            @else
                                <a class="chip" href="{{ $url }}" aria-label="{{ __('public.pagination.page', ['page' => $page]) }}">{{ $page }}</a>
                            @endif
                        </li>
                    @endforeach
                @endif
            @endforeach

            <li>
                @if ($paginator->hasMorePages())
                    <a class="btn btn--sm" href="{{ $paginator->nextPageUrl() }}" rel="next">{{ __('public.pagination.next') }} <x-icon name="chevron-right" /></a>
                @else
                    <span class="btn btn--sm" aria-disabled="true">{{ __('public.pagination.next') }} <x-icon name="chevron-right" /></span>
                @endif
            </li>
        </ul>
    </nav>
@endif
