<?php
use App\Helpers\UserContext;
use App\Helpers\ViewHelper;

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

UserContext::init();
$currentUser = UserContext::getCurrentUser();
$flash = ViewHelper::getFlash();
?>

<nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow">
    <div class="container">
        <a class="navbar-brand" href="<?= base_url('/') ?>">
            <b>IoT Project - Smart Store</b>
        </a>
        <div class="ms-auto text-white d-flex align-items-center">
            <?php if ($currentUser): ?>
                <span>
                    Welcome back,
                    <b>
                        <?= htmlspecialchars($currentUser['first_name'] ?? '') ?>
                        <?= htmlspecialchars($currentUser['last_name'] ?? '') ?>
                    </b>
                </span>
            <?php else: ?>
                <span class="me-2">Welcome Anon</span>
                <div class="dropdown">
                    <button class="btn btn-primary dropdown-toggle"
                            type="button"
                            id="loginDropdown"
                            data-bs-toggle="dropdown"
                            data-bs-auto-close="outside"
                            aria-expanded="false">
                        Please login
                    </button>
                    <div class="dropdown-menu dropdown-menu-end p-4 shadow"
                         aria-labelledby="loginDropdown"
                         style="min-width: 320px;">

                        <?php if (!empty($flash['success'])): ?>
                            <div class="alert alert-success alert-dismissible fade show py-2" role="alert">
                                <?= htmlspecialchars($flash['success']) ?>
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        <?php endif; ?>
                        <?php if (!empty($flash['error'])): ?>
                            <div class="alert alert-danger alert-dismissible fade show py-2" role="alert">
                                <?= htmlspecialchars($flash['error']) ?>
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        <?php endif; ?>

                        <form method="POST" action="<?= base_url('/auth/navbar-login') ?>">
                            <div class="mb-3">
                                <label class="form-label">Email address</label>
                                <input type="email"
                                       name="email"
                                       class="form-control"
                                       placeholder="email@example.com"
                                       required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Password</label>
                                <input type="password"
                                       name="password"
                                       class="form-control"
                                       placeholder="Password"
                                       required>
                            </div>
                            <div class="form-check mb-3">
                                <input type="checkbox"
                                       name="remember"
                                       class="form-check-input"
                                       id="rememberCheck">
                                <label class="form-check-label" for="rememberCheck">
                                    Remember me
                                </label>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">
                                Sign in
                            </button>
                        </form>
                    </div>
                </div>
            <?php endif; ?>
        </div>
    </div>
</nav>
