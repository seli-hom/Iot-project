<?php

namespace App\Controllers;

use App\Domain\Models\RegistrationModel;
use DI\Container;
use Psr\Http\Message\ResponseInterface as Response;
use Psr\Http\Message\ServerRequestInterface as Request;

class RegistrationController extends BaseController
{
    public function __construct(Container $container, private RegistrationModel $registration_model)
    {
        parent::__construct($container);
    }

    public function index(Request $request, Response $response, array $args): Response
    {
        $data['data'] = [
            'title' => "Customer Registration",
        ];

        return $this->render($response, '/customer/customerRegistrationView.php', $data);
    }

    public function create(Request $request, Response $response, array $args)
    {
        // echo '<pre>';
        // print_r($_POST);
        // die('Form reached RegistrationController');

        $registration_form_data = $request->getParsedBody();
        $first_name = $registration_form_data['fname'];
        $last_name = $registration_form_data['lname'];
        $address = $registration_form_data['address'];
        $email = $registration_form_data['email'];
        $phone = $registration_form_data['phone'];

        $data = [
            'fname' => $first_name,
            'lname' => $last_name,
            'address' => $address,
            'email' => $email,
            'phone' => $phone
        ];

        if (!empty($first_name) && !empty($last_name) && !empty($address) && !empty($email) && !empty($phone)) {
            try {
                $customer_registered = $this->registration_model->insertCustomer($data);

                if ($customer_registered) {
                    exec(PYTHON_SCRIPTS_PATH . 'helo.py');
                }
                return $response->withHeader('Location', '/Iot-project/customer/registration')->withStatus(302);
            } catch (\Throwable $th) {
                dd('Sorry, we could not process your request');
            }
        }
    }
}
