<?php

use App\Helpers\ViewHelper;
//TODO: set the page title dynamically based on the view being rendered in the controller.
// $page_title = 'Customer Registration';
$page_title = $data['title'];

ViewHelper::loadHeader($page_title);
?>

<div class="page-content">
    <h2><?= $page_title ?></h2>
    <br>
    <a href="<?= ViewHelper::url('customer/registration') ?>">Go To Customer Registration Page</a>
</div>


<?php

ViewHelper::loadJsScripts();
ViewHelper::loadFooter();
?>
