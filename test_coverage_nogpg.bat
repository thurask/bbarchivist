REM For systems without gpg or gpg >=2.1
py.test --color=no --cov=bbarchivist tests/ --cov-report html --cov-config .coveragerc -v -m "not needsgpg"