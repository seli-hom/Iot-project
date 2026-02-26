<?php

declare(strict_types = 1);

namespace App\Domain\Models;

use App\Helpers\Core\PDOService;
use PDO;

class UserModel extends BaseModel {

    public function __construct(PDOService $pdo) {
        parent::__construct($pdo);
    }

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

    public function findByEmail(string $email): ?array {
        $sql = "SELECT * FROM users WHERE email = :email LIMIT 1";
        $result = $this->selectOne($sql, [':email' => $email]);
        return $result ?: null;
    }

    public function findByPhone(string $phone): ?array {
        $sql = "SELECT * FROM users WHERE phone = :phone LIMIT 1";
        $result = $this->selectOne($sql, [':phone' => $phone]);
        return $result ?: null;
    }

    public function getUsers(): array {
        $sql = "SELECT * FROM users";
        return $this->selectAll($sql);
    }

    /**
     * Verify credentials for login
     *
     * @param string $email
     * @param string $password
     * @return array|null Returns user array if valid, null if invalid
     */
    public function verifyCredentials(string $email, string $password): ?array
    {
        $user = $this->findByEmail($email);
        if (!$user) {
            return null;
        }

        if (password_verify($password, $user['password'])) {
            unset($user['password']);
            return $user;
        }

        return null;
    }
}