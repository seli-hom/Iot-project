<?php

namespace App\Helpers;

class UserContext {
    /**
     * Initialize session and default keys
     */
    public static function init (): void {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }

        if (!isset($_SESSION['currentUser'])) {
            $_SESSION['currentUser'] = null;
        }
    }

    /**
     * Get the current logged-in user
     */
    public static function getCurrentUser (): ?array {
        return $_SESSION['currentUser'] ?? null;
    }

    /**
     * Log in a user and set their session data
     */
    public static function login (array $userData): void {
        $_SESSION['currentUser'] = [
            'first_name' => $userData['first_name'] ?? $userData['fname'] ?? '',
            'last_name' => $userData['last_name'] ?? $userData['lname'] ?? '',
            'email' => $userData['email'] ?? '',
        ];
    }

    /**
     * Log out the current user
     */
    public static function logout (): void {
        $_SESSION['currentUser'] = null;
    }

    /**
     * Check if a user is logged in
     */
    public static function isLoggedIn (): bool {
        return !empty($_SESSION['currentUser']);
    }
}
