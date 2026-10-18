<?php

/*
| Reverse proxies and load balancers that sit in front of the app (a CDN, nginx, a hosting
| platform's edge). Laravel only believes X-Forwarded-For / -Proto / -Host from an address listed
| here. Without it, behind a proxy every visitor looks like the same address (so every child
| shares one rate-limit bucket) and generated links come out as http://.
|
| Comma separated addresses or CIDR ranges, or * to trust whatever connects (only when the app is
| reachable through the proxy alone). Leave empty when nothing sits in front of the app.
*/
$proxies = trim((string) env('TRUSTED_PROXIES', ''));

return [
    'proxies' => $proxies === '*'
        ? '*'
        : (array_values(array_filter(array_map('trim', explode(',', $proxies)))) ?: null),
];
