<?php

namespace App\Domain\Models;

use App\Helpers\Core\PDOService;

class CustomerModel extends BaseModel
{
    public function __construct(PDOService $pdoservice)
    {
        parent::__construct($pdoservice);
    }

    public function insertCustomer(array $data): mixed {
        $sql = <<<sql
            INSERT INTO users (first_name, last_name, address, email, phone)
            VALUES (:first_name, :last_name, :address, :email, :phone)
        sql;

        $this->execute($sql, [
            'first_name' => $data['fname'],
            'last_name' => $data['lname'],
            'address' => $data['address'],
            'email' => $data['email'],
            'phone' => $data['phone']
        ]);

        return $this->pdo->lastInsertId();
    }
}