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

];
