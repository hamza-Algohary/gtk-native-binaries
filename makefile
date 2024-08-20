build:
	-mkdir lib
	python3 msys.py jar mingw-w64-x86_64-gtk4 mingw-w64-x86_64-libadwaita mingw-w64-x86_64-gstreamer --name gtk_native.jar --class GtkNative --package gtk_native --path win --output lib

init:
	-rm msys.py
	wget https://raw.githubusercontent.com/hamza-Algohary/msyslinux/main/msys.py
install:
	mvn install:install-file -Dfile=lib/gtk_native.jar -DgroupId="io.github.hamza-Algohary" -DartifactId=gtk_native -Dversion=0.1.0 -Dpackaging=jar -DgeneratePom=true