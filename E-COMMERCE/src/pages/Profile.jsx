import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { User, Mail, Phone, MapPin, Building, Hash, Save, CheckCircle, AlertCircle, LogOut } from 'lucide-react';
import './Profile.css';

const Profile = () => {
    const { user, updateProfile, logout } = useAuth();
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        phone: '',
        address: '',
        city: '',
        zipCode: ''
    });
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        if (user) {
            setFormData({
                name: user.name || '',
                phone: user.profile?.phone || '',
                address: user.profile?.address || '',
                city: user.profile?.city || '',
                zipCode: user.profile?.zipCode || ''
            });
        }
    }, [user]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setSuccess('');
        setError('');

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:5001/api/profile', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to update profile');
            }

            updateProfile(data);
            setSuccess('Profile updated successfully!');
            setTimeout(() => setSuccess(''), 3000);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.id]: e.target.value });
    };

    if (!user) return <div className="profile-loading">Loading...</div>;

    return (
        <div className="profile-container">
            <div className="profile-card">
                <div className="profile-header">
                    <div className="profile-avatar">
                        <User size={64} />
                    </div>
                    <h1>My Profile</h1>
                    <p>{user.email}</p>
                    <span className="role-badge">{user.role}</span>
                </div>

                {success && (
                    <div className="profile-message success">
                        <CheckCircle size={20} />
                        <span>{success}</span>
                    </div>
                )}

                {error && (
                    <div className="profile-message error">
                        <AlertCircle size={20} />
                        <span>{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="profile-form">
                    <div className="form-section">
                        <h2>Personal Information</h2>
                        <div className="form-grid">
                            <div className="form-group">
                                <label htmlFor="name">Full Name</label>
                                <div className="input-icon">
                                    <User size={18} />
                                    <input type="text" id="name" value={formData.name} onChange={handleChange} required />
                                </div>
                            </div>
                            <div className="form-group">
                                <label htmlFor="phone">Phone Number</label>
                                <div className="input-icon">
                                    <Phone size={18} />
                                    <input type="text" id="phone" value={formData.phone} onChange={handleChange} placeholder="+1 234 567 890" />
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="form-section">
                        <h2>Shipping Address</h2>
                        <div className="form-group">
                            <label htmlFor="address">Street Address</label>
                            <div className="input-icon">
                                <MapPin size={18} />
                                <input type="text" id="address" value={formData.address} onChange={handleChange} placeholder="123 Main St" />
                            </div>
                        </div>
                        <div className="form-grid">
                            <div className="form-group">
                                <label htmlFor="city">City</label>
                                <div className="input-icon">
                                    <Building size={18} />
                                    <input type="text" id="city" value={formData.city} onChange={handleChange} placeholder="New York" />
                                </div>
                            </div>
                            <div className="form-group">
                                <label htmlFor="zipCode">Zip Code</label>
                                <div className="input-icon">
                                    <Hash size={18} />
                                    <input type="text" id="zipCode" value={formData.zipCode} onChange={handleChange} placeholder="10001" />
                                </div>
                            </div>
                        </div>
                    </div>

                    <button type="submit" className="save-button" disabled={loading}>
                        {loading ? 'Saving...' : <><Save size={20} /> Save Changes</>}
                    </button>

                    <div className="profile-actions">
                        <button
                            type="button"
                            className="logout-button-profile"
                            onClick={() => {
                                logout();
                                navigate('/');
                            }}
                        >
                            <LogOut size={20} /> Logout from Account
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Profile;
