set cdir=%~dp0
chdir /D docs && make html && chdir /D %cdir%
python setup.py sdist bdist_wheel
twine upload -s -i 29795048
