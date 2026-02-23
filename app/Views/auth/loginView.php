<?php

use App\Helpers\ViewHelper;

$page_title = $data['title'];

$flash = ViewHelper::getFlash();
?>

<h2><?= $page_title ?></h2>
<br>

<?php if (!empty($flash['success'])): ?>
    <div class="alert alert-success" role="alert">
        <?= htmlspecialchars($flash['success']) ?>
    </div>
<?php endif; ?>

<?php if (!empty($flash['error'])): ?>
    <div class="alert alert-danger" role="alert">
        <?= htmlspecialchars($flash['error']) ?>
    </div>
<?php endif; ?>

<div id="form-container">
    <form class="row g-3" action="./login/submit" method="POST">

        <div class="col-12">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" name="email" required>
        </div>

        <div class="col-12">
            <label class="form-label">Password</label>
            <input type="password" class="form-control" name="password" required>
        </div>

        <div class="col-12">
            <button type="submit" class="btn btn-primary">Login</button>
        </div>

        <div>
            <p>Dont have an account?
            <a class="btn btn-primary" href="./registration">Sign up</a>
        </div>

    </form>
</div>