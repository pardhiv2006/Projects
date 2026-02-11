import { ObjectId } from 'mongodb';
import bcrypt from 'bcryptjs';

export const UserRole = {
    USER: 'user',
    ADMIN: 'admin'
};

export async function createUser(db, userData) {
    const usersCollection = db.collection('users');
    
    // Check if user already exists
    const existingUser = await usersCollection.findOne({ email: userData.email });
    if (existingUser) {
        throw new Error('User already exists');
    }

    // Hash password
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(userData.password, salt);

    const newUser = {
        name: userData.name,
        email: userData.email,
        password: hashedPassword,
        role: userData.role || UserRole.USER,
        profile: {
            phone: userData.phone || '',
            address: userData.address || '',
            city: userData.city || '',
            zipCode: userData.zipCode || ''
        },
        createdAt: new Date(),
        updatedAt: new Date()
    };

    const result = await usersCollection.insertOne(newUser);
    return { ...newUser, _id: result.insertedId };
}

export async function findUserByEmail(db, email) {
    return await db.collection('users').findOne({ email });
}

export async function findUserById(db, id) {
    try {
        return await db.collection('users').findOne({ _id: new ObjectId(id) });
    } catch (error) {
        return null;
    }
}

export async function updateUserProfile(db, userId, profileData) {
    const result = await db.collection('users').findOneAndUpdate(
        { _id: new ObjectId(userId) },
        { 
            $set: { 
                name: profileData.name,
                'profile.phone': profileData.phone,
                'profile.address': profileData.address,
                'profile.city': profileData.city,
                'profile.zipCode': profileData.zipCode,
                updatedAt: new Date()
            } 
        },
        { returnDocument: 'after' }
    );
    return result;
}

export async function validatePassword(inputPassword, hashedPassword) {
    return await bcrypt.compare(inputPassword, hashedPassword);
}
