<?php

return [
    'qa' => [
        'name' => 'Soalan & Jawapan',
        'description' => 'Satu soalan pada satu masa. Tenang dan jelas, sesuai untuk semua umur.',
        'fields' => [
            'progress' => [
                'label' => 'Penunjuk kemajuan',
                'options' => ['dots' => 'Titik', 'bar' => 'Palang'],
            ],
        ],
    ],
    'stars' => [
        'name' => 'Kutip Bintang',
        'description' => 'Setiap jawapan betul menyalakan satu bintang. Lihat koleksi bintang bertambah.',
        'fields' => [
            'show_streak' => [
                'label' => 'Tunjuk jawapan betul berturut-turut',
                'help' => 'Kiraan ini hanya hiasan dan tidak mengubah markah.',
            ],
        ],
    ],
    'quest' => [
        'name' => 'Misi Berlevel',
        'description' => 'Seperti Sang Kancil menyeberang sungai: setiap soalan satu batu, setiap tahap satu persinggahan.',
        'fields' => [
            'level_size' => [
                'label' => 'Soalan bagi setiap tahap',
                'help' => 'Antara 3 dan 10.',
            ],
        ],
    ],
];
