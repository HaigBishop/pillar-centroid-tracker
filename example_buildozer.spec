[app]
title = Pillar Centroid Tracker
author = Haig Bishop
package.name = pillar_centroid_tracker
package.domain = org.haig
orientation = landscape
osx.python_version = 3
osx.kivy_version = 2.3.0
osx.kivy_path = /Applications/Kivy.app
requirements = python3,kivy==2.3.0,certifi==2024.8.30,chardet==5.2.0,charset-normalizer==3.4.0,contourpy==1.3.1,cycler==0.12.1,docutils==0.21.2,fonttools==4.55.2,idna==3.10,imageio==2.36.1,joblib==1.4.2,kivy-garden==0.1.5,kiwisolver==1.4.7,matplotlib==3.9.3,numpy==2.1.3,opencv-python==4.10.0.84,packaging==24.2,pillow==11.0.0,plyer==2.1.0,pygments==2.18.0,pyobjc-core==10.3.2,pyobjc-framework-cocoa==10.3.2,pyparsing==3.2.0,python-dateutil==2.9.0.post0,requests==2.32.3,scikit-learn==1.5.2,scipy==1.14.1,six==1.17.0,threadpoolctl==3.5.0,urllib3==2.2.3
version = 1.1.2
source.dir = .
icon.filename = resources/icon.icns
presplash.filename = resources/icon_splash.png
source.include_exts = py,png,kv,txt,ttf,ico,icns
source.include_patterns = resources/*
source.exclude_exts = spec
source.exclude_dirs = __pycache__,readme_images,example_image_seqs
source.exclude_patterns = *.tmp,*.log,*.gitignore

[buildozer]
build_dir = ./.buildozer
bin_dir = ./bin
log_level = 2
