<?php
use App\Helpers\ViewHelper;

$page_title = $data['title'];
$flash = ViewHelper::getFlash();
?>

<div class="container d-flex justify-content-center py-5">
    <div class="card shadow-sm" style="min-width: 450px; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto;">
        <div class="card-body p-4">
            <h3 class="card-title text-center mb-3">Your Cart</h3>

            <form action="./checkout/submit" method="POST">
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
                            <td>Example Item</td>
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