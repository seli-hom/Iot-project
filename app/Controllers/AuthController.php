<?php

namespace App\Controllers;

use DI\Container;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;
use Slim\Routing\RouteContext;

use App\Domain\Models\UserModel;
use App\Helpers\UserContext;

class AuthController extends BaseController
{
    private UserModel $userModel;

    public function __construct(Container $container)
    {
        parent::__construct($container);
        $this->userModel = $container->get(UserModel::class);
        UserContext::init();
    }

    public function viewRegistrationForm(Request $request, Response $response, array $args): Response
    {
        return $this->render($response, 'common/layout.php', [
            'page_title'  => 'Register',
            'contentView' => APP_VIEWS_PATH . '/auth/registrationView.php',
            'data'        => [
                'title' => "Register"
            ]
        ]);
    }

    public function viewLoginForm(Request $request, Response $response, array $args): Response
    {
        return $this->render($response, 'common/layout.php', [
            'page_title'  => 'Login',
            'contentView' => APP_VIEWS_PATH . '/auth/loginView.php',
            'data'        => [
                'title' => "Login"
            ]
        ]);
    }

    public function processRegistrationForm(Request $request, Response $response): Response
    {
        $data = $request->getParsedBody();
        $routeParser = RouteContext::fromRequest($request)->getRouteParser();

        if (!filter_var($data['email'], FILTER_VALIDATE_EMAIL)) {
            \App\Helpers\ViewHelper::setFlash('error', 'Please enter a valid email address.');
            return $response->withHeader('Location', $routeParser->urlFor('auth.registration.form'))->withStatus(302);
        }

        if ($this->userModel->findByEmail($data['email'])) {
            \App\Helpers\ViewHelper::setFlash('error', 'This email is already registered.');
            return $response->withHeader('Location', $routeParser->urlFor('auth.registration.form'))->withStatus(302);
        }

        if (empty($data['address']) || strlen($data['address']) < 5) {
            \App\Helpers\ViewHelper::setFlash('error', 'Please enter a valid address.');
            return $response->withHeader('Location', $routeParser->urlFor('auth.registration.form'))->withStatus(302);
        }

        if (!preg_match('/^(?=.*[A-Za-z])(?=.*\d).{8,}$/', $data['password'])) {
            \App\Helpers\ViewHelper::setFlash('error', 'Password must be at least 8 characters long and include at least one letter and one number.');
            return $response->withHeader('Location', $routeParser->urlFor('auth.registration.form'))->withStatus(302);
        }

        $this->userModel->createUser($data);

        \App\Helpers\ViewHelper::setFlash('success', 'Your account was created successfully!');
        return $response->withHeader('Location', $routeParser->urlFor('auth.login.form'))->withStatus(302);
    }

    public function processLoginForm(Request $request, Response $response): Response
    {
        $data = $request->getParsedBody();
        $routeParser = RouteContext::fromRequest($request)->getRouteParser();

        if (!filter_var($data['email'], FILTER_VALIDATE_EMAIL)) {
            \App\Helpers\ViewHelper::setFlash('error', 'Please enter a valid email address.');
            return $response->withHeader('Location', $routeParser->urlFor('auth.login.form'))->withStatus(302);
        }

        $user = $this->userModel->findByEmail($data['email']);

        if (!$user || !password_verify($data['password'], $user['password'])) {
            \App\Helpers\ViewHelper::setFlash('error', 'Invalid email or password.');
            return $response->withHeader('Location', $routeParser->urlFor('auth.login.form'))->withStatus(302);
        }

        $_SESSION['user_id'] = $user['id'];
        return $response->withHeader('Location', $routeParser->urlFor('home.index'))->withStatus(302);
    }

    public function logout(Request $request, Response $response): Response
    {
        session_destroy();

        $routeParser = RouteContext::fromRequest($request)->getRouteParser();

        return $response
            ->withHeader('Location', $routeParser->urlFor('home.index'))
            ->withStatus(302);
    }
}