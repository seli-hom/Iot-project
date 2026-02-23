<?php

use App\Helpers\ViewHelper;
/**
 * This file includes all html and php pertinent to the landing page 
 * (the page that displays when the project is accessed from the root)
 */

$page_title = $data['title'];
$flash = ViewHelper::getFlash();
?>

<div class="page-content">
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

    <a href="<?= ViewHelper::url('auth/registration') ?>">Go To Customer Registration Page</a>
</div>

