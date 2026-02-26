<div class="container d-flex justify-content-center py-5">
    <div class="card shadow-sm" style="min-width: 500px; max-width: 600px; width: 100%; max-height: 90vh; overflow-y: auto;">
        <div class="card-body p-4">
            <h3 class="card-title text-center mb-3"><?= $page_title ?></h3>

            <!-- Flash Messages -->
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

            <form class="row g-3" action="./registration/submit" method="POST">
                <div class="col-md-6">
                    <label class="form-label">First Name</label>
                    <input type="text" class="form-control" name="fname" required>
                </div>

                <div class="col-md-6">
                    <label class="form-label">Last Name</label>
                    <input type="text" class="form-control" name="lname" required>
                </div>

                <div class="col-12">
                    <label class="form-label">Address</label>
                    <input type="text" class="form-control" name="address" required>
                </div>

                <div class="col-12">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-control" name="email" required>
                </div>

                <div class="col-12">
                    <label class="form-label">Phone Number</label>
                    <input type="text" class="form-control" name="phone" required>
                </div>

                <div class="col-12">
                    <label class="form-label">Password</label>
                    <input type="password" class="form-control" name="password" required>
                </div>

                <div class="col-12">
                    <button type="submit" class="btn btn-primary w-100">Register</button>
                </div>

                <div class="col-12 text-center mt-2">
                    <p>Already have an account? <a href="./login">Login</a></p>
                </div>
            </form>
        </div>
    </div>
</div>