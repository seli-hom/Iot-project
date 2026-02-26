<?php

declare(strict_types=1);

/**
 * This file contains the routes for the web application.
 */

use App\Controllers\HomeController;
use App\Controllers\AuthController;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

return static function (Slim\App $app): void {

    //* NOTE: Route naming pattern: [controller_name].[method_name]
    $app->get('/', [HomeController::class, 'index'])
        ->setName('home.index');

    $app->get('/home', [HomeController::class, 'index'])
        ->setName('home.index');

    // A route to test runtime error handling and custom exceptions.
    $app->get('/error', function (Request $request, Response $response, $args) {
        throw new \Slim\Exception\HttpBadRequestException($request, "This is a runtime error. Something went wrong");
    });

    // User Authentication routes
    $app->group('/auth', function ($auth) {
        // Register a new user
        $auth->get('/registration', [AuthController::class, 'viewRegistrationForm'])
            ->setName('auth.registration.form'); 
        $auth->post('/registration/submit', [AuthController::class, 'processRegistrationForm'])
            ->setName('auth.registration.submit'); 

        // Login page (optional dedicated page)
        $auth->get('/login', [AuthController::class, 'viewLoginForm'])
            ->setName('auth.login.form'); 

        // Login submission from the login page
        $auth->post('/login/submit', [AuthController::class, 'processLoginForm'])
            ->setName('auth.login.submit'); 

        // Login submission from the navbar (works from any page)
        $auth->post('/navbar-login', [AuthController::class, 'processNavbarLogin'])
            ->setName('auth.navbar.login'); 

        // Logout
        $auth->get('/logout', [AuthController::class, 'logout'])
            ->setName('auth.logout'); 
    });

    // Customer view routes
    $app->group('/customer', function ($group) {
        $group->get('/registration', [RegistrationController::class, 'index'])
            ->setName('registration.index');
        $group->get('/turnon', RegistrationController::class, 'turnLenOn')->setName('registration.led');
        $group->post('/registration/create', [RegistrationController::class, 'create'])
            ->setName('registration.create');
    });

    //    // Employee checkout routes
    // $app->group('/employee', function ($group) {
    //     // Employee dashboard / register customer
    //     $group->get('/dashboard', [EmployeeController::class, 'dashboard'])
    //         ->setName('employee.dashboard');

    //     // Employee checkout actions
    //     $group->post('/checkout', [EmployeeController::class, 'processCheckout'])
    //         ->setName('employee.checkout.submit');
    // });

    // // Self-checkout routes (for logged-in customers)
    // $app->group('/checkout', function ($group) {
    //     $group->get('/self', [CheckoutController::class, 'viewCart'])
    //         ->setName('checkout.self.view');

    //     $group->post('/self/submit', [CheckoutController::class, 'processCart'])
    //         ->setName('checkout.self.submit');
    // });
};