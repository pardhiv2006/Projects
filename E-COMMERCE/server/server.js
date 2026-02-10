import express from 'express';
import cors from 'cors';
import { MongoMemoryServer } from 'mongodb-memory-server';
import { MongoClient, ObjectId } from 'mongodb';

const app = express();
const PORT = 5001;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB setup
let db;
let productsCollection;
let ordersCollection;

// Initialize in-memory MongoDB
async function initDB() {
    const mongod = await MongoMemoryServer.create();
    const uri = mongod.getUri();
    const client = new MongoClient(uri);

    await client.connect();
    db = client.db('firstmart');
    productsCollection = db.collection('products');
    ordersCollection = db.collection('orders');

    console.log('✅ Connected to in-memory MongoDB');

    // Seed initial data
    await seedProducts();
}

// Seed products data
async function seedProducts() {
    const count = await productsCollection.countDocuments();
    if (count === 0) {
        const { products } = await import('./data.js');
        await productsCollection.insertMany(products);
        console.log(`✅ Seeded ${products.length} products`);
    }
}

// Routes

// Get all products
app.get('/api/products', async (req, res) => {
    try {
        const products = await productsCollection.find({}).toArray();
        res.json(products);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get product by ID
app.get('/api/products/:id', async (req, res) => {
    try {
        const product = await productsCollection.findOne({ id: parseInt(req.params.id) });
        if (!product) {
            return res.status(404).json({ error: 'Product not found' });
        }
        res.json(product);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get products by category
app.get('/api/products/category/:category', async (req, res) => {
    try {
        const products = await productsCollection.find({
            category: req.params.category
        }).toArray();
        res.json(products);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Search products
app.get('/api/products/search/:query', async (req, res) => {
    try {
        const query = req.params.query;
        const products = await productsCollection.find({
            $or: [
                { name: { $regex: query, $options: 'i' } },
                { category: { $regex: query, $options: 'i' } },
                { description: { $regex: query, $options: 'i' } }
            ]
        }).toArray();
        res.json(products);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Create order
app.post('/api/orders', async (req, res) => {
    try {
        const { items, total, subtotal, discount, discountApplied } = req.body;

        if (!items || items.length === 0) {
            return res.status(400).json({ error: 'Order must contain items' });
        }

        // Generate order ID
        const orderId = `#ORD-${Math.floor(Math.random() * 89999) + 10000}`;

        // Calculate expected delivery date (3-7 days from now)
        const daysToAdd = Math.floor(Math.random() * 5) + 3;
        const expectedDelivery = new Date();
        expectedDelivery.setDate(expectedDelivery.getDate() + daysToAdd);

        const order = {
            id: orderId,
            items: items,
            total: total,
            subtotal: subtotal || total + discount,
            discount: discount || 0,
            discountApplied: discountApplied || false,
            date: new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }),
            expectedDelivery: expectedDelivery.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
            status: 'Ready for Delivery',
            createdAt: new Date(),
            timestamp: Date.now()
        };

        const result = await ordersCollection.insertOne(order);
        res.status(201).json({ ...order, _id: result.insertedId });
    } catch (error) {
        console.error('Error creating order:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get all orders
app.get('/api/orders', async (req, res) => {
    try {
        const orders = await ordersCollection.find({}).toArray();
        res.json(orders);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Update order status (for cancellation or delivery completion)
app.patch('/api/orders/:id', async (req, res) => {
    try {
        const { status } = req.body;

        if (!status) {
            return res.status(400).json({ error: 'Status is required' });
        }

        // Support both MongoDB ObjectId and custom order ID format
        let query;
        try {
            query = { _id: new ObjectId(req.params.id) };
        } catch {
            query = { id: req.params.id };
        }

        const result = await ordersCollection.updateOne(
            query,
            { $set: { status: status, updatedAt: new Date() } }
        );

        if (result.matchedCount === 0) {
            return res.status(404).json({ error: 'Order not found' });
        }

        res.json({ message: 'Order updated successfully', status });
    } catch (error) {
        console.error('Error updating order:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get orders by status
app.get('/api/orders/status/:status', async (req, res) => {
    try {
        const orders = await ordersCollection.find({ status: req.params.status }).toArray();
        res.json(orders);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Get order by ID
app.get('/api/orders/:id', async (req, res) => {
    try {
        let query;
        try {
            query = { _id: new ObjectId(req.params.id) };
        } catch {
            query = { id: req.params.id };
        }

        const order = await ordersCollection.findOne(query);
        if (!order) {
            return res.status(404).json({ error: 'Order not found' });
        }
        res.json(order);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Health check
app.get('/api/health', (req, res) => {
    res.json({ status: 'OK', message: 'First Mart API is running' });
});

// Start server
initDB().then(() => {
    app.listen(PORT, () => {
        console.log(`🚀 Server running on http://localhost:${PORT}`);
    });
});
