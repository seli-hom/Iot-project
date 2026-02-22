<?php

use App\Helpers\ViewHelper;
//TODO: set the page title dynamically based on the view being rendered in the controller.
$page_title = $data['title'];
ViewHelper::loadHeader($page_title);
?>

<div class="page-content">
    <h2><?= $page_title ?></h2>
    <br>
    <div id="form-container">
        <form class="row g-3">
            <div class="col-md-6">
                <label for="fname" class="form-label">First Name</label>
                <input type="text" class="form-control" id="fname">
            </div>
            <div class="col-md-6">
                <label for="lname" class="form-label">Last Name</label>
                <input type="text" class="form-control" id="lname">
            </div>
            <div class="col-12">
                <label for="inputAddress" class="form-label">Address</label>
                <input type="text" class="form-control" id="inputAddress">
            </div>
            <div class="col-12">
                <label for="inputEmail" class="form-label">Email</label>
                <input type="email" class="form-control" id="inputEmail">
            </div>
            <div class="col-12">
                <label for="inputPhone" class="form-label">Phone Number</label>
                <input type="email" class="form-control" id="inputPhone">
            </div>
            <div class="col-12">
                <button type="submit" class="btn btn-primary">Sign in</button>
            </div>
        </form>
    </div>
</div>


<?php

ViewHelper::loadJsScripts();
ViewHelper::loadFooter();
?>
