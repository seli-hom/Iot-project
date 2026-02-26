<?php

use App\Helpers\ViewHelper;
/**
 * This file includes all html and php pertinent to the landing page 
 * (the page that displays when the project is accessed from the root)
 */

$page_title = $data['title'];
$flash = ViewHelper::getFlash();
?>

<div class="page-content text-center    ">
    <div className="container py-5 ">

        <h1 className="text-secondary mb-4">Welcome to the smart store!</h1>
        <h3>please login to continue</h3>
        <p><b>OR</b></p>
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

        <a href="<?= ViewHelper::url('auth/registration') ?>" class="btn btn-primary btn-lg">Registration Today!</a>
    </div>
</div>

