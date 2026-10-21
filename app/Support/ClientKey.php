<?php

namespace App\Support;

use Illuminate\Http\Request;

/**
 * The network address of a caller, as a key for counting requests.
 *
 * An IPv6 subscriber normally holds a whole /64, so counting each full address would let one
 * client mint a fresh quota by cycling through addresses inside its own block. IPv6 is therefore
 * grouped by its /64, and an IPv4 address written as IPv6 (::ffff:203.0.113.9) is the IPv4 address.
 */
final class ClientKey
{
    public static function address(Request $request): string
    {
        $ip = (string) $request->ip();
        $packed = @inet_pton($ip);

        if ($packed === false || strlen($packed) !== 16) {
            return $ip;
        }

        if (str_starts_with($packed, str_repeat("\0", 10)."\xff\xff")) {
            return (string) inet_ntop(substr($packed, 12));
        }

        return inet_ntop(substr($packed, 0, 8).str_repeat("\0", 8)).'/64';
    }
}
