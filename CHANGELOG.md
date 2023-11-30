# Changelog

## v1.2.0 (30/11/2023)

### New Feature
- Added support for multipart file upload
- Print version number with -v flag

### Improvements
- If external response file is provided, response will always be stored in it

### Fix
- Close request payload file at the end

## v1.1.0 (24/10/2023)

### New Feature
- Uncurlify: Generate a restcall template from a curl command

### Improvements
- REST call errors return exit status 1
- Automatically use response as text while error parsing as JSON

### Fix
- Added missing imports in main

## v1.0.0 (29/12/2022)
- First release of `restcall`
