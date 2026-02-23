<?php

use App\Helpers\LocalizationHelper;
use App\Helpers\UserContext;

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Initialize session and current user
UserContext ::init();
$currentUser = UserContext ::getCurrentUser();
?>

<footer id="footer-bar">
    <div id="footer-content">
        <p> This is a footer :3</p>
    </div>
</footer>
</body>