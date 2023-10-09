const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const PORT = 3001; // You can choose another port if you wish

// Middlewares
app.use(cors()); // This allows requests from our React frontend
app.use(bodyParser.json()); // This will parse incoming JSON payloads

// POST route to handle data from the frontend
app.get('/take-attendance', (req, res) => {
    console.log ("hello world");
});
app.post('/take-attendance', (req, res) => {
    console.log(req.body);  // This will print the data sent by the frontend

    // You can process the data here as needed

    // Respond to the frontend
    res.json({ message: "Data received successfully!" });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
