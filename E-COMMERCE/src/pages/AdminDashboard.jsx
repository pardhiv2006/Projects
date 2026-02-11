import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Package, Search, Plus, Filter, MoreVertical, Edit, Trash2, ExternalLink } from 'lucide-react';
import './AdminDashboard.css';

const AdminDashboard = () => {
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchProducts();
    }, []);

    const fetchProducts = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:5001/api/admin/products', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.error);

            setProducts(data);
        } catch (err) {
            setError('Failed to fetch products: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const filteredProducts = products.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.category.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="admin-container">
            <header className="admin-header">
                <div>
                    <h1>Admin Dashboard</h1>
                    <p>Manage your products and inventory</p>
                </div>
                <button className="add-product-btn">
                    <Plus size={20} /> Add Product
                </button>
            </header>

            <div className="admin-stats">
                <div className="stat-card">
                    <div className="stat-icon products"><Package size={24} /></div>
                    <div className="stat-info">
                        <h3>Total Products</h3>
                        <p>{products.length}</p>
                    </div>
                </div>
                {/* More stats could go here */}
            </div>

            <div className="admin-content">
                <div className="table-controls">
                    <div className="search-bar">
                        <Search size={20} />
                        <input
                            type="text"
                            placeholder="Search products..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="filter-group">
                        <button className="icon-btn"><Filter size={20} /></button>
                    </div>
                </div>

                {error && <div className="admin-error">{error}</div>}

                <div className="table-wrapper">
                    <table className="admin-table">
                        <thead>
                            <tr>
                                <th>Product</th>
                                <th>Category</th>
                                <th>Price</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr><td colSpan="4" className="text-center">Loading products...</td></tr>
                            ) : filteredProducts.length === 0 ? (
                                <tr><td colSpan="4" className="text-center">No products found</td></tr>
                            ) : filteredProducts.map(product => (
                                <tr key={product.id}>
                                    <td>
                                        <div className="product-cell">
                                            <img src={product.image} alt={product.name} />
                                            <div>
                                                <div className="product-name">{product.name}</div>
                                                <div className="product-id">ID: #{product.id}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td><span className="category-pill">{product.category}</span></td>
                                    <td className="price-cell">${product.price.toFixed(2)}</td>
                                    <td>
                                        <div className="action-btns">
                                            <button className="icon-btn" title="View"><ExternalLink size={18} /></button>
                                            <button className="icon-btn" title="Edit"><Edit size={18} /></button>
                                            <button className="icon-btn delete" title="Delete"><Trash2 size={18} /></button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
