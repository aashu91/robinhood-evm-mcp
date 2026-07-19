import React, { useEffect, useState } from'react';
import axios from 'axios';

const Dashboard = () => {
    const [goldPrice, setGoldPrice] = useState(0);
    const [silverPrice, setSilverPrice] = useState(0);

    useEffect(() => {
        const fetchPrices = async () => {
            try {
                const response = await axios.get('/api/prices');
                setGoldPrice(response.data.goldPrice);
                setSilverPrice(response.data.silverPrice);
            } catch (error) {
                console.error('Error fetching prices:', error);
            }
        };

        fetchPrices();
    }, []);

    return (
        <div>
            <h1>🏦 Trust Bank Reserves Tracker</h1>
            <p>Gold (XAU/USD): {goldPrice.toFixed(2)} USD</p>
            <p>Silver (XAG/USD): {silverPrice.toFixed(2)} USD</p>
        </div>
    );
};

export default Dashboard;