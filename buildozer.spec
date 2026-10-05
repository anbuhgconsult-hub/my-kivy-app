[app]

# (str) Title of your application
title = My Kivy App

# (str) Package name
package.name = mykivyapp

# (str) Package domain
package.domain = org.example

# (str) Source code location
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,jpeg,kv,txt

# (list) Application requirements
requirements = python3,kivy

# (str) Application versioning
version = 0.1

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API required
android.minapi = 21
# (str) Android NDK version to use
android.ndk = 25b

# (str) Supported orientations
orientation = portrait

# (bool) Fullscreen or not
fullscreen = 0

[buildozer]

# (int) Log level
log_level = 2

# (int) Warning on root
warn_on_root = 1
