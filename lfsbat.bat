SET file_extension=%~1

:: Remove all the desired files from VCS, but keep them locally
git rm --cached "*.%file_extension%"
git commit -m "Removed %file_extension% format from the repository"

:: Tell LFS to track this format, has to be done before the files are added
git lfs track "*.%file_extension%"

:: Make sure to add the changes made by LFS above
git add .gitattributes

:: Add to LFS!
git add "*.%file_extension%"
git commit -m "Added %file_extension% format to LFS"?