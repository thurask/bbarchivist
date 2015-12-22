set cdir=%~dp0
chdir /D docs && make html && chdir /D %cdir% && python setup.py sdist bdist_wheel upload --sign --identity=29795048
