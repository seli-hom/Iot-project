<?php

use App\Helpers\LocalizationHelper;
use App\Helpers\UserContext;

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

UserContext::init();
$currentUser = UserContext::getCurrentUser();
?>

<footer class="bg-primary text-white py-4 mt-auto">
    <div class="container d-flex justify-content-between align-items-center">
        
        <span>&copy; <?= date('Y') ?> IoT Project</span>

        <div>
            <a href="<?= base_url('/') ?>" class="text-white me-3 text-decoration-none">
                Home
            </a>
            <a href="<?= base_url('/') ?>auth/registration" class="text-white text-decoration-none">
                Register
            </a>
        </div>

    </div>
</footer>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function () {
    const trigger = document.getElementById("loginDropdown");
    if (trigger) {
        const dropdown = new bootstrap.Dropdown(trigger);
        dropdown.show();
    }
});
</script>
</body>
</html>
