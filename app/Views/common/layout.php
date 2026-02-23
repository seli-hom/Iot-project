<?php
use App\Helpers\ViewHelper;
use App\Helpers\UserContext;

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

UserContext::init();


$page_title = $page_title ?? 'IoT Project - Smart Store';

$requestUri = $_SERVER['REQUEST_URI'] ?? '';
$basePath   = rtrim($_SERVER['BASE_PATH'] ?? '', '/');

$normalizedPath = $basePath && str_starts_with($requestUri, $basePath)
    ? substr($requestUri, strlen($basePath))
    : $requestUri;
?>

<?php ViewHelper::loadHeader($page_title); ?>
<?php ViewHelper::loadNavBar(); ?>

<div id="page-content">
    <?php require $contentView; ?>
</div>

<?php
ViewHelper::loadFooter();
ViewHelper::loadJsScripts();
?>
