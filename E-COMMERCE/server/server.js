import express from 'express';
import cors from 'cors';
import { MongoMemoryServer } from 'mongodb-memory-server';
import { MongoClient, ObjectId } from 'mongodb';
import jwt from 'jsonwebtoken';
import dotenv from 'dotenv';
import { createUser, findUserByEmail, findUserById, updateUserProfile, validatePassword, UserRole } from './models.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5001;
const JWT_SECRET = process.env.JWT_SECRET || 'fallback_secret_for_dev';

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB setup
let db;
let productsCollection;
let ordersCollection;

// Initialize in-memory MongoDB
// Initialize MongoDB
async function initDB() {
    let uri = process.env.MONGODB_URI;

    if (!uri || uri.includes('<username>')) {
        console.log('⚠️ No MONGODB_URI found or it is a placeholder. Using in-memory MongoDB with local persistence...');
        const mongod = await MongoMemoryServer.create({
            instance: {
                dbPath: './db-data', // Local directory for persistence
                storageEngine: 'wiredTiger'
            }
        });
        uri = mongod.getUri();
    }

    const client = new MongoClient(uri);

    await client.connect();
    db = client.db('firstmart');
    productsCollection = db.collection('products');
    ordersCollection = db.collection('orders');

    console.log('✅ Connected to MongoDB');

    // Seed initial data
    await seedProducts();
    await seedAdmin();
}

// Seed admin user
async function seedAdmin() {
    const adminEmail = 'admin@firstmart.com';
    const existingAdmin = await findUserByEmail(db, adminEmail);
    if (!existingAdmin) {
        await createUser(db, {
            name: 'System Admin',
            email: adminEmail,
            password: 'admin123',
            role: UserRole.ADMIN
        });
        console.log('✅ Default admin created: admin@firstmart.com / admin123');
    }
}

// Auth Middleware
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) return res.status(401).json({ error: 'Access denied. Token missing.' });

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) return res.status(403).json({ error: 'Invalid token.' });
        req.user = user;
        next();
    });
};

const isAdmin = (req, res, next) => {
    if (req.user && req.user.role === UserRole.ADMIN) {
        next();
    } else {
        res.status(403).json({ error: 'Require Admin Role' });
    }
};

// Seed products data
async function seedProducts() {
    const count = await productsCollection.countDocuments();
    if (count === 0) {
        const { products } = await import('./data.js');
        await productsCollection.insertMany(products);
        console.log(`✅ Seeded ${products.length} products`);
    }
}

// Auth Routes

// Signup
app.post('/api/auth/signup', async (req, res) => {
    try {
        const { name, email, password } = req.body;
        const user = await createUser(db, { name, email, password });

        const token = jwt.sign(
            { id: user._id, email: user.email, role: user.role },
            JWT_SECRET,
            { expiresIn: '24h' }
        );

        res.status(201).json({ token, user: { id: user._id, name: user.name, email: user.email, role: user.role, profile: user.profile } });
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

// Login
app.post('/api/auth/login', async (req, res) => {
    try {
        const { email, password } = req.body;
        const user = await findUserByEmail(db, email);

        if (!user || !(await validatePassword(password, user.password))) {
            return res.status(401).json({ error: 'Invalid email or password' });
        }

        const token = jwt.sign(
            { id: user._id, email: user.email, role: user.role },
            JWT_SECRET,
            { expiresIn: '24h' }
        );

        res.json({ token, user: { id: user._id, name: user.name, email: user.email, role: user.role, profile: user.profile } });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// User Profile Routes

// Get profile
app.get('/api/profile', authenticateToken, async (req, res) => {
    try {
        const user = await findUserById(db, req.user.id);
        if (!user) return res.status(404).json({ error: 'User not found' });

        const { password, ...userWithoutPassword } = user;
        res.json(userWithoutPassword);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Update profile
app.put('/api/profile', authenticateToken, async (req, res) => {
    try {
        const profileData = req.body;
        const updatedUser = await updateUserProfile(db, req.user.id, profileData);
        if (!updatedUser) return res.status(404).json({ error: 'User not found' });

        const { password, ...userWithoutPassword } = updatedUser;
        res.json(userWithoutPassword);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Admin Product Management

// Admin - Get all products (with extra details if needed, for now same as public)
app.get('/api/admin/products', authenticateToken, isAdmin, async (req, res) => {
    try {
        const products = await productsCollection.find({}).toArray();
        res.json(products);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});


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
app.post('/api/orders', authenticateToken, async (req, res) => {
    try {
        const { items, total, subtotal, discount, discountApplied } = req.body;
        const userId = req.user.id;

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
            userId: userId,
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

// Get user's orders
app.get('/api/orders', authenticateToken, async (req, res) => {
    try {
        const userId = req.user.id;
        let query = { userId: userId };

        // If admin, show all orders (optional, but good for admin dashboard)
        if (req.user.role === UserRole.ADMIN) {
            query = {};
        }

        const orders = await ordersCollection.find(query).toArray();
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
