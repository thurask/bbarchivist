set cdir=%~dp0
chdir /D docs && make html && chdir /D %cdir% && rmdir /s /q dist && python setup.py sdist bdist_wheel && twine upload dist/* -s -i 29795048
