<?php

use App\Helpers\ViewHelper;
//TODO: set the page title dynamically based on the view being rendered in the controller.
$page_title = 'Customer Registration';
ViewHelper::loadHeader($page_title);
?>

<div class="page-content">
    <h2>Home Page</h2>
</div>


<?php

ViewHelper::loadJsScripts();
ViewHelper::loadFooter();
?>
