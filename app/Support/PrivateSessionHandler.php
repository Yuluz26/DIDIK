<?php

namespace App\Support;

use Illuminate\Session\DatabaseSessionHandler;

/**
 * The framework's database session handler, minus one habit: it writes the visitor's IP address and
 * browser string next to every session. DIDIK has no use for either, and for a children's site not
 * collecting them is the safer default, so they are left empty (the columns stay NULL).
 */
class PrivateSessionHandler extends DatabaseSessionHandler
{
    protected function addRequestInformation(&$payload)
    {
        return $this;
    }
}
