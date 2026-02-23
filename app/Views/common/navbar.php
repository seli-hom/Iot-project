<?php
use App\Helpers\UserContext;

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

UserContext::init();
$currentUser = UserContext::getCurrentUser();

?>

<nav id="nav-bar" class="display-flex-row">

    <a id="brand" class="bilbo-swash-caps-regular" href="../">
        <h1>IoT Project</h1>
    </a>

    <div id="nav-bar-content" class="display-flex-row">

        <div id="nav-bar-user" class="display-flex-col">

            <?php if ($currentUser): ?>
                <h4>
                    Welcome,
                    <?= htmlspecialchars($currentUser['first_name'] ?? 'Guest') ?>
                    <?= htmlspecialchars($currentUser['last_name'] ?? '') ?>!
                </h4>

            <?php else: ?>
                <h5>Welcome, Anonymous one!</h5>
            <?php endif; ?>

        </div>
    </div>
</nav>
