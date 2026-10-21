const express = require('express');
const mongoose = require('mongoose');

const app = express();
const PORT = process.env.PORT || 3000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://localhost:27017/users_db';
const APP_SECRET = process.env.APP_SECRET || 'jwt-signing-secret';

app.use(express.json());

app.get('/', (req, res) => {
    res.json({ message: 'User Management API running', status: 'ready' });
});

app.get('/health', (req, res) => {
    res.json({ status: 'healthy', uptime: process.uptime() });
});

app.get('/api/users', (req, res) => {
    res.json([
        { id: 1, name: 'Alice DevOps', role: 'Engineer' },
        { id: 2, name: 'Bob SRE', role: 'Architect' }
    ]);
});

app.post('/api/users', (req, res) => {
    res.status(201).json({ message: 'User created' });
});

app.listen(PORT, () => {
    console.log(`Server listening on port ${PORT}`);
});
