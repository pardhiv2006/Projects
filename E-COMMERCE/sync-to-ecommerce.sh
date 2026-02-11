#!/bin/bash

SOURCE="/Users/rajeshchinthala/Desktop/Pardhiv_Intern/Cyborg/application-4"
TARGET="/Users/rajeshchinthala/Desktop/Pardhiv_Intern/Projects/E-COMMERCE"

echo "Syncing changes from $SOURCE to $TARGET..."

# Create necessary directories in target
mkdir -p "$TARGET/server"
mkdir -p "$TARGET/src/pages"
mkdir -p "$TARGET/src/components"

# Copy modified files
cp "$SOURCE/server/.env" "$TARGET/server/.env"
cp "$SOURCE/server/server.js" "$TARGET/server/server.js"
cp "$SOURCE/src/pages/Profile.jsx" "$TARGET/src/pages/Profile.jsx"
cp "$SOURCE/src/pages/Profile.css" "$TARGET/src/pages/Profile.css"
cp "$SOURCE/src/components/Navbar.jsx" "$TARGET/src/components/Navbar.jsx"
cp "$SOURCE/.gitignore" "$TARGET/.gitignore"
cp "$SOURCE/test-auth.sh" "$TARGET/test-auth.sh"
cp "$SOURCE/test-profile-update.sh" "$TARGET/test-profile-update.sh"

echo "✅ Changes synced successfully!"
