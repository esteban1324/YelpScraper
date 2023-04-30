<?php
// Open the CSV file
$file = fopen('mexican_restaurants1.csv', 'r');

// Start the HTML table
echo '<table>';

// Loop through each row in the CSV file
while (($row = fgetcsv($file)) !== false) {
    // Start a new table row
    echo '<tr>';

    // Loop through each cell in the row
    foreach ($row as $cell) {
        // Output the cell as a table cell
        echo '<td>' . htmlspecialchars($cell) . '</td>';
    }

    // End the table row
    echo '</tr>';
}

// End the HTML table
echo '</table>';

// Close the CSV file
fclose($file);
?>
