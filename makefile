clean:
	cd dart; rm -rf *.so *.c *.html build/ __pycache__; cd -
	cd dart2; python3 setup.py build_ext --inplace; cd ..
	cd dart_old; rm -rf *.so *.c *.html build/ __pycache__; cd -
	cd baselines/cedar; rm -rf *.so *.c *.html build/ __pycache__; cd -
	cd baselines/borat; rm -rf *.so *.c *.html build/ __pycache__; cd -

build:
	cd dart; python3 setup.py build_ext --inplace; cd ..
	cd dart2; python3 setup.py build_ext --inplace; cd ..
	cd dart_old; python3 setup.py build_ext --inplace; cd ..
	cd baselines/borat; python3 setup.py build_ext --inplace; cd ..
	cd baselines/cedar; python3 setup.py build_ext --inplace; cd ..

get_deps:
	pip3 install -r requirements.txt

all: clean get_deps build