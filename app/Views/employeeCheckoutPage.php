<?php
use App\Helpers\ViewHelper;

$page_title = $data['title'];
$flash = ViewHelper::getFlash();
?>

<div class="container d-flex flex-column align-items-center py-5">
    <div class="card shadow-sm mb-4" style="min-width: 450px; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto;">
        <div class="card-body p-4">
            <h3 class="card-title text-center mb-3">Register Customer</h3>

            <form class="row g-3" action="./employee/register-customer" method="POST">
                <div class="col-md-6">
                    <label class="form-label">First Name</label>
                    <input type="text" class="form-control" name="fname" required>
                </div>

                <div class="col-md-6">
                    <label class="form-label">Last Name</label>
                    <input type="text" class="form-control" name="lname" required>
                </div>

                <div class="col-12">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" name="email" required>
                </div>

                <div class="col-12">
                    <label class="form-label">Phone</label>
                    <input type="text" class="form-control" name="phone" required>
                </div>

                <div class="col-12">
                    <button type="submit" class="btn btn-primary w-100">Register Customer</button>
                </div>
            </form>
        </div>
    </div>

    <div class="card shadow-sm" style="min-width: 450px; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto;">
        <div class="card-body p-4">
            <h3 class="card-title text-center mb-3">Cart / Checkout</h3>

            <form action="./employee/checkout" method="POST">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Item</th>
                            <th>Qty</th>
                            <th>Price</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Sample Item</td>
                            <td><input type="number" name="qty[]" value="1" class="form-control form-control-sm"></td>
                            <td>$10</td>
                            <td>$10</td>
                        </tr>
                    </tbody>
                </table>

                <div class="d-flex justify-content-end mt-3">
                    <button type="submit" class="btn btn-success">Checkout</button>
                </div>
            </form>
        </div>
    </div>
</div>