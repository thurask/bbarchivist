Changelog
=========


(unreleased)
------------
- Add S3 URL fallback.
- Use 7z 19.00.
- oem_eea support.
- Randomly generate user agents for most web operations.
- Fix compatibility with time.clock.

3.9.0 (2018-09-12)
------------
- SDM636 loader support.
- KEY2 loader support.
- Add new syntax option to newprd.
- Add (temp) bbb5 devcfg to loader.
- Add no prefix switch for newprd.


3.8.0 (2018-05-10)
------------------
- Use 7z 18.05.
- Fix filtering issue with link generator.
- Reenable downloads for full OS, but skip hash verify.
- Add decorator to retry timeouts while scanning.
- Add remote option for OTA scan.
- Migrate config files to appdata.
- Add export switch for TCL tools.
- Update flasher for bbb5, Indo bbb7, oem_russia.


3.7.0 (2017-11-06)
------------------
- Questionnaire fix.
- Add new PRD scanner script.
- Support non-KEYone tclloader files.
- Add device filter to tclscan.


3.6.0 (2017-10-18)
------------------
- Add questionnaire to tclscan.
- Disable extra spaces at end of family lookup.
- Fix spacing when checking one-device family certs.
- Improve scan text output.
- Add option for tclscan to scan for OTA upgrades.


3.5.0 (2017-09-22)
------------------
- Add UCRT DLLs to build for pre-W10 and x86.
- Fix PTCRB scraper.
- Use 7z 17.01.
- Add script files to pyinstaller_exe.
- Attach datafile to certchecker.
- Add TCL delta script.
- Add TCL loader handling script.
- Move dat files to subdir.
- Add TCL scanner script.
- Add KEYone prd list.
- Refactor JSON into separate files in subdir.
- Add code to download Android platform tools.
- Disable scraping BBMobile loader page.
- Prep for KEYone carrier variants.


3.4.0 (2017-05-14)
------------------
- Add KEYone autoloader urls, BBMobile support scraper.
- Temporarily filter droidlookup devices.
- Fix link generator, tests.
- Don't accidentally delete uncompressed loaders.
- Add 10.3.3+ filtering for STL100-1.
- Add new devices to droidlookup devicetype.
- Update to VS2017.


3.3.0 (2017-03-28)
------------------
- Add minimum versions to requirements.
- Change device ID reminder.
- Build 32 and 64 bit releases, with UPX.
- Change no alpha 2 flag to no alpha/beta 2 flag.


3.2.1 (2017-01-24)
------------------
- Add edge cases to JSON.
- Fix trailing whitespace.


3.2.0 (2017-01-02)
------------------
- Add zero-length filter to textgenerator.
- Add questionnaire to barlinker.
- Update dates.
- Fix args with droidscraper.
- Disable GPG agent, make it truly unattended.
- Use defusedxml.
- Make loader offset bytestring instead of file.
- Add cached bars utilization for archivist, lazyloader.


3.1.0 (2016-12-07)
------------------
- Move from cx_freeze to pyinstaller.
- Add default case to downloader script.
- Fix incorrect args for frozen archivist.
- Fix typo in autolookup args.
- Fix typo with blitz links.
- Fix pathing with lazyloader.
- Create folder if specified but doesn't exist.
- Add git index handling to download_dats.
- Fix threading issue.
- Clean exception handling a bit.


3.0.1 (2016-11-21)
------------------
- Move some temporary directories to tempdir.
- Fix typo with URL generator.


3.0.0 (2016-11-01)
------------------
- Full DTEK60 scan support.
- Add barlinker script.
- Add autoloader page scraper.


2.9.0 (2016-10-02)
------------------
- Make kernchecker look nicer.
- Make SQL insertion for autolookup threaded.
- Run autolookup/URL generation in a separate thread.
- Fix bug with SSL email.
- Since when did separate folders not work?
- Fix bug with pseudocap.
- Fix bug in archivist.
- SHA3 support for python 3.6.
- Fix errors in sqlexport script.
- Fix DTEK50 hashes.
- Droidlookup now scans all by default.


2.8.0 (2016-09-04)
------------------
- Fix kernchecker only reading first page of github branches.
- Prod only filter for autolookup, SDK support for linkgen.
- Add selective filter to filehasher/gpgrunner.
- Add info generator as standalone + archivist.
- Add software release availability checker.
- Add --all switch to droidlookup, refactor args.


2.7.0 (2016-08-09)
------------------
- Fix requests breaking 3.2.
- Privlookup->droidlookup, DTEK50 support.
- Add Dev Alpha URL generator.


2.6.0 (2016-07-01)
------------------
- Add webbrowser code list to cchecker.
- Add single lookup to privlookup.
- Cleanup print output for privlookup.
- Add CAP/CFP version to version args.
- CAP 3.11.0.27.
- Fix email.


2.5.1 (2016-05-17)
------------------
- Add commit date to versioneer.
- Sort metadata.
- Add default start and stop to privlookup.
- Use https where possible.
- Cx_freeze support for versioneer.
- Util lookup for kernchecker.
- Fix download_dats without needing dependencies.
- Simplejson.


2.5.0 (2016-05-02)
------------------
- Versioneer for frozen exes, metadata scanner.
- Use versioneer.
- Sha-0.
- Add hash lookup to Priv scanner.


2.4.2 (2016-04-12)
------------------
- Actually use threadpoolexecutor for Priv loader scan.


2.4.1 (2016-03-13)
------------------
- Add Priv autoloader scanner.
- Add uncompressed tar support.


2.4.0 (2016-03-07)
------------------
- Add separate CAP shim.
- Make hashing parallel.
- Deprecate single-file hash.
- Make GPG signature creation parallel.
- Fix archivist if release is not for all devices.
- Add availability filter to sqlexport.
- Add guard to SR lookup.
- Add manual dat download script.
- Fix CSV export column name.


2.3.1 (2016-01-05)
------------------
- Fix bugs, update date, add selective option to cchecker.
- Fix bug with signed file discovery.
- Convert timer from seconds to hh:mm:ss.
- Add family lookup for certchecker.


2.3.0 (2015-12-18)
------------------
- Add more executables to cx_freeze.
- Add CFP shim script.
- Fix bug with core downloader.
- Fix download errors.
- Add kernel check script.
- Fix escreens bug.
- Remove GUI, since it sucks and doesn't work with py3.5.
- Add list certs/all devices function to certchecker.


2.2.2 (2015-10-25)
------------------
- Add core autoloader support to lazyloader/archivist.
- Get PTCRB checking working with priv.
- Fix bug with pseudocap.
- Make SQL list dump explicitly formatted.
- Add autoloader verifier functions (Windows only).
- Make removing signed files show basename, not abspath.
- Add entry list function for sqlexport.
- Fix incorrect availability for SQL entry.


2.2.1 (2015-10-03)
------------------
- SQL takes in all SW rels; add available/first date fields.
- Add SQL DB pop function to sqlexport.
- Improve PTCRB entry detection/cleaning.
- Fix CAP ConfigParser.
- Fix config files deleting themselves.


2.2.0 (2015-09-15)
------------------
- Add self-email functionality for autolookup.


2.1.3 (2015-09-09)
------------------
- Add SQL validation to autolookup.
- Add hybrid radio software guessing to archivist, lazyloader.
- Add existence checker for SQL.


2.1.2 (2015-09-09)
------------------
- Add ceiling to autolookup.
- Fix json not being included w/frozen lazyloader.


2.1.1 (2015-09-08)
------------------
- Add bar downloader script.
- Fix error with radio only loaders.
- Fix broken alt SW check.
- Add more input checks to lazyloader.


2.1.0 (2015-08-29)
------------------
- Add app names to exported app list.
- Clean up cchecker args, add forced OS option.
- Fix selective compression.
- More granular errors for SQL.
- Force loader creation w/archivist.
- Add method option to archivist.
- Make 7z compression/verification quiet.
- Add compression script.
- Fix 7z verification.
- Fix bugs with 7z verify, STL100-1 OS image fallback.
- Add radio SW to lazyloader/archivist preamble.
- Make CAP path ini-dependent.
- Convert compression mode to ConfigParser, fix radio folder names.
- Rewrite hash wrapper to take ConfigParser.


2.0.2 (2015-08-17)
------------------
- Add different radio (and hybrid loader naming) option to lazyloader, archivist.
- Linkgen: option to use different radio with different SW release.
- Add available-only (quiet) mode to autolookup.


2.0.1 (2015-07-29)
------------------
- (Attempt to) Fix broken loaders due to improper offset length.
- Add force SW release option to cchecker, archive verifier to archivist.
- Add manifest/blitz checking to scripts, VZW OS fallback for archivist.
- Add archive verifier wrapper function, manifest verifier functions.
- Fix bundle lookup in carrierchecker args.


2.0.0 (2015-07-12)
------------------
- Add SQL DB/CSV export functions.
- Add standalone cap script.
- Add no gui arg to lazyloader
- Fix linkgen guessing.
- Fix errors with argument validators.
- Validate mcc/mnc for carrierchecker.


1.9.0 (2015-07-06)
------------------
- Add cert checker through beautifulsoup.
- Replace hardcoded device lists and IDs with JSON.
- 7z compression now works with space-containing paths.


1.8.1 (2015-06-28)
------------------
- Add "GUI" to lazyloader.
- Prevent autolookup overflow.
- Add custom increment to autolookup.


1.8.0 (2015-06-19)
------------------
- Fix error with unavailable link text sizes.
- Add size to generated links.
- Add Content-Length getter to networkutils.
- Add app bar export to carrierchecker.
- Add bar integrity check to archivist, carrierchecker, lazyloader.
- Add link generation option to autolookup.


1.7.3 (2015-06-15)
------------------
- Add Ctrl+C kill switch to multithread lookup.
- Add no-download option to lazyloader.
- Add timeout to lookup to keep things fresh.
- Multithread autolookup.


1.7.2 (2015-06-14)
------------------
- Fix availability check.
- Replace HEAD request with GET request for carrier checker.
- Start making unit tests.
- Fix argparse validation errors.
- Prevent recursive GPG signatures.
- Preserve leading zeroes for Adler32, CRC32 results.


1.7.1 (2015-06-12)
------------------
- Add block to check for device in lazyloader.
- Add option to continue on unknown radio version.
- Add cx_freeze setup for lazyloader.
- Allow for local ca certs bundle.
- Fix bug with individual cksum files.
- Fix possible error condition with version-dependent links.


1.7.0 (2015-05-30)
------------------
- Add radiocheck, pre-10.3.1 support to archivist.
- Make download/blitz output much less verbose.
- Add edge cases to lazyloader (renames, missing files, radio not +1).
- Add availability check to linkgen.


1.6.2 (2015-05-20)
------------------
- If downloading through lazyloader, replace filename with "OS/radio".
- Add option to guess software/radio from OS for some scripts.
- Replace visible PGP passphrase input with getpass (i.e. hidden).


1.6.1 (2015-05-18)
------------------
- Add one/many cksum file option to archivist, filehasher.
- Fix issue with grabbing STL100-1/Z3 OS name.
- Hashes now in separate files by default.
- Invalid downloads/autoloader creation less shouty.
- Add filesize to downloader.


1.6.0 (2015-05-16)
------------------
- Make loader creation less shouty in case of error.
- Replace raw entry of PGP key/phrase with configparser file.
- Be selective with deleting uncompressed loader folders.
- Skip empty folders with verifier.


1.5.2 (2015-05-12)
------------------
- Make blitz packaging work on 3.2.
- Remove alpha2 lookup.
- Add current OS version counter to autolookup.


1.5.1 (2015-05-11)
------------------
- Replace loadergen default CAP with supplied CAP file.
- Fix autoloader error in pseudocap.


1.5.0 (2015-05-09)
------------------
- Add blocksize to CRC32.
- Make loadergen exceptions verbose.
- Add Verizon OS files to linkgen.
- Add logging to autolookup.
- Add cmd wrapper for autolookup.
- Ctrl+C to break lookup loop.
- Autolookup method wrapper.
- Error checking for swrel lookup.
- Add bundle check setting to carrierchecker.
- Add sw release lookup, available bundle lookup.


1.4.2 (2015-05-01)
------------------
- Fix GPG crash.


1.4.1 (2015-05-01)
------------------
- Fix crash on trying to gpg-verify folders.


1.4.0 (2015-05-01)
------------------
- Add GPG verification; option for archivist or standalone script.
- Add Python 3.2/3.3 support.


1.3.2 (2015-04-30)
------------------
- Fix linkgen output bug.


1.3.1 (2015-04-30)
------------------
- Pypi upload is stupid.


1.3.0 (2015-04-30)
------------------
- Add blitz creation.
- Add link exporter.


1.2.4 (2015-04-29)
------------------
- Add link export option to cchecker.


1.2.3 (2015-04-27)
------------------
- Fix type error with bb-escreens.
- Remove trailing newlines in filehasher.


1.2.2 (2015-04-24)
------------------
- Escreen code generator.
- Validate blocksize before using.
- Pretty format OS/radio versions in archivist.


1.2.1 (2015-04-23)
------------------
- Fix folder create with cchecker.
- Add all hash arg to archivist cmd wrapper.
- Add cmd script for file hashing.


1.2.0 (2015-04-22)
------------------
- Make working dirs if they don't exist.
- Add upgrade/debrick bar download to carrierchecker.
- Update CAP to 3.11.0.22.
- Add whirlpool hash.


1.1.3 (2015-04-20)
------------------
- Fix missing Leap lookup, add model name to cchecker.


1.1.2 (2015-04-20)
------------------
- Re-add press enter to exit.


1.1.1 (2015-04-19)
------------------
- Fix case sensitivity with cchecker.


1.1.0 (2015-04-19)
------------------
- Add carrier checker.


1.0.1 (2015-04-16)
------------------
- Initial commit, 1.0.1.
