const express = require("express");

const app = express();

app.get("/", (req, res) => {

    res.json({
        message: "Node Express application"
    });

});

app.get("/users", (req, res) => {

    res.json({
        users: []
    });

});

app.listen(3000, () => {

    console.log(
        "Server running on port 3000"
    );

});
