<?php

namespace App\Controllers;

use App\Domain\Models\RegistrationModel;
use DI\Container;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class RegistrationController extends BaseController
{
    public function __construct(Container $container, private RegistrationModel $registration_model) {
        parent::__construct($container);
    }

    public function index(Request $request, Response $response, array $args): Response {
        $data['data'] = [
            'title' => "Customer Registration",
        ];

        return $this->render($response, 'customer/customerRegistrationView.php', $data);
    }
}
