<?php

return [

    /*
    | Shown on the privacy page when set. Leave empty to omit the contact line.
    */
    'contact_email' => env('DIDIK_CONTACT_EMAIL'),

    /*
    | Hosts an admin may link to from the Quizizz library (each also allows its subdomains).
    | Quizizz now trades as Wayground and old quizizz.com links redirect there, so both are
    | accepted, plus the join-code domain. An empty list rejects every link rather than allowing all.
    */
    'quizizz_hosts' => ['quizizz.com', 'wayground.com', 'joinmyquiz.com'],

    /*
    | How long quiz attempts (and the answers in them) are kept before didik:prune deletes them.
    | The privacy page quotes this number, so change it here and the page follows.
    */
    'retention_days' => (int) env('DIDIK_RETENTION_DAYS', 90),

    /*
    | Content-Security-Policy on every response (scripts and styles from this site only). Leave on:
    | it is what limits the damage if a page ever echoes something it should not.
    */
    'csp' => (bool) env('DIDIK_CSP', true),

    /*
    | Strict-Transport-Security max-age in seconds, sent only on HTTPS responses. 0 turns it off.
    | Six months by default; raise it once HTTPS is settled.
    */
    'hsts_seconds' => (int) env('DIDIK_HSTS_SECONDS', 15552000),

    /*
    | Host names the app answers to, besides APP_URL's own host and its subdomains. Needed when the
    | site is also served on another name (for example the bare domain next to www). Plain host
    | names, comma separated. Only enforced outside local and testing.
    */
    'trusted_hosts' => array_values(array_filter(array_map('trim', explode(',', (string) env('TRUSTED_HOSTS', ''))))),

];
