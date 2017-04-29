all:
	@if [ find -name HelloWorld_*.zip ]; then rm HelloWorld_*.zip; fi
	@for i in $$(find . -maxdepth 1 -type d|egrep './.+'|sed -e 's/.\///' ); do cd $$i && zip -r HelloWorld_$$i.zip * && mv *.zip .. && cd ..; done;
