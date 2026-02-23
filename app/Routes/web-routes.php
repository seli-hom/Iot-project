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
        // Register a new user:
        $auth->get('/registration', [AuthController::class, 'viewRegistrationForm'])
            ->setName('auth.registration.form'); 
        $auth->post('/registration/submit', [AuthController::class, 'processRegistrationForm'])
            ->setName('auth.registration.submit'); 

        // Login an existing user
        $auth->get('/login', [AuthController::class, 'viewLoginForm'])
            ->setName('auth.login.form'); 
        $auth->post('/login/submit', [AuthController::class, 'processLoginForm'])
            ->setName('auth.login.submit'); 

        // Sign out of the active user's account
        $auth->get('/logout', [AuthController::class, 'logout'])
            ->setName('auth.logout'); 
    });
};