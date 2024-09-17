build:
	-mkdir lib
	python3 msys.py export mingw-w64-x86_64-gtk4 mingw-w64-x86_64-libadwaita mingw-w64-x86_64-gstreamer --output lib

init:
	-rm msys.py
	wget https://raw.githubusercontent.com/hamza-Algohary/msyslinux/main/msys.py

release:
	zip -r gtk4-dlls.zip lib
	gh release create v0.1 -d gtk4-dlls.zip
	rm *.zip
clean:
	rm -rf lib *.zip *.py