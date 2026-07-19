const express = require('express');
const app = express();
const web3Helper = require('./web3_helper');

app.get('/api/prices', async (req, res) => {
    try {
        const goldPrice = await web3Helper.getGoldPrice();
        const silverPrice = await web3Helper.getSilverPrice();
        res.json({ goldPrice, silverPrice });
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch prices' });
    }
});

app.listen(3000, () => {
    console.log('Server is running on port 3000');
});