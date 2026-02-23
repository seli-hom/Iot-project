<?php

declare(strict_types = 1);

namespace App\Domain\Models;

use App\Helpers\Core\PDOService;
use PDO;

class UserModel extends BaseModel {

    public function __construct(PDOService $pdo) {
        parent::__construct($pdo);
    }

    /**
     * Create a new user record in the database.
     */
    public function createUser(array $data): int {

        $hashedPassword = password_hash($data['password'], PASSWORD_DEFAULT);

        $sql = "
            INSERT INTO users 
            (first_name, last_name, address, email, phone, password) 
            VALUES 
            (:first_name, :last_name, :address, :email, :phone, :password)
        ";

        $params = [
            ':first_name' => $data['fname'],
            ':last_name'  => $data['lname'],
            ':address'    => $data['address'],
            ':email'      => $data['email'],
            ':phone'      => $data['phone'],
            ':password'   => $hashedPassword,
        ];

        $this->execute($sql, $params);

        return (int)$this->pdo->lastInsertId();
    }

    /**
     * Find a user by email.
     */
    public function findByEmail(string $email): ?array {

        $sql = "
            SELECT * 
            FROM users 
            WHERE email = :email
            LIMIT 1
        ";

        $result = $this->selectOne($sql, [
            ':email' => $email
        ]);

        return $result ?: null;
    }

    /**
     * Find a user by phone.
     */
    public function findByPhone(string $phone): ?array {

        $sql = "
            SELECT * 
            FROM users 
            WHERE phone = :phone
            LIMIT 1
        ";

        $result = $this->selectOne($sql, [
            ':phone' => $phone
        ]);

        return $result ?: null;
    }

    /**
     * Fetch all users.
     */
    public function getUsers(): array {
        $sql = "SELECT * FROM users";
        return $this->selectAll($sql);
    }
}