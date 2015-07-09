all:
	@ rm HelloWorld_*.zip
	@for i in $$(find . -maxdepth 1 -type d|egrep './.+'|sed -e 's/.\///' ); do cd $$i && zip -r HelloWorld_$$i.zip * && mv *.zip .. && cd ..; done;
