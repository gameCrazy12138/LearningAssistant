[app]

# (str) Title of your application
title = LearningAssistant

# (str) Package name
package.name = learningassistant

# (str) Package domain (needed for android/ios packaging)
package.domain = org.yourname

# (str) Source code where the main.py live
source.dir = ../src

# (list) Source extensions to include in the build
source.include_exts = py,png,jpg,kv,atlas,json

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) The NDK version to use.
android.ndk = 25b

# (int) Android SDK version to use
android.sdk = 24

# (str) Python-for-android branch to use
p4a.branch = master

# (str) Extra python modules to include
requirements = python3,kivy==2.2.1,docutils,PIL

# (bool) If True, then gradle caching is enabled.
android.gradle_cache = True

# (list) Add java sources needed for android build
#android.add_src = 

# (list) Add extra gradle repos to search
#android.extra_repos = 

# (list) Put each source file/directory on a new line
android.add_aars = 

# (str) Whether to skip over known install-packages command errors
#android.skip_known_install_issues = 

# (int) Version code of your application
android.version_code = 1

# (str) Version string of your application
version = 3.0.4

# (list) Application category
#android.appcategory = 

# (str) Android entry point's class name
#android.entrypoint = org.kivy.android.PythonActivity

# (str) The filename in which the app's private data is backed up to
#android.backup_rules = 

# (str) Generate a mapping of obfuscated classes with original names
#android.enable_proguard_mapping = 

# (str) Proguard config file to use
#android.proguard_config = 

# (bool) Use proguard to shrink and obfuscate the code
#android.use_proguard = False

# (list) List of Java files to include in the build
#android.add_jars = 

# (str) The key alias to use when signing the APK
#android.release_key_alias = 

# (str) Path to keystore file
#android.keystore = 

# (str) Keystore password
#android.keystore_password = 

# (str) Key password
#android.key_password = 

# (str) Path to whitelist file
#android.proguard_whitelist = 

# (str) Additional proguard rules file
#android.additional_proguard_rules = 

# (bool) Whether to create a debug APK
android.debuggable = True

# (bool) Whether to create a release APK
#android.release = 

# (str) The path to the directory containing the application's data
#android.app_data_dir = 

# (str) Override the Android manifest file location
#android.manifest.custom_template_file = 

# (str) Override the Android build.gradle file location
#android.gradle.custom_template_file = 

# (list) List of tuples of directories to be zipped and added to APK assets
#android.assets = 

# (list) List of additional directories to be included in APK's lib folder
#android.extra_libs = 

# (str) Logcat level
#android.logcat_level = DEBUG

# (bool) Allow backup of the application data
#android.allow_backup = True

# (str) Theme to use for the application
#android.theme = 

# (bool) Enable multidex support
#android.enable_multidex = False

# (str) Specify the ABI(s) to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Whether to generate a universal APK
#android.generate_universal_apk = False

# (str) The root directory of the project
#project_root = 

# (str) The directory to place the build outputs
build_dir = ./build

# (str) The directory to place the final APK
dist_dir = ./dist

# (list) Patterns to exclude from the source directory
exclude_patterns = 
    *.pyc
    __pycache__
    .git
    .svn
    *.bak
    *.swp
    .DS_Store
    Thumbs.db
    *.log
    build
    dist

# (bool) Whether to show gradle output during build
#show_gradle_log = False

# (str) Gradle daemon max heap size
#org.gradle.jvmargs = -Xmx2048m

# (bool) Enable gradle parallel execution
#org.gradle.parallel = True

# (bool) Enable gradle caching
#org.gradle.caching = True
