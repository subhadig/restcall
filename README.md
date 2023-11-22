# restcall
A small JSON-based command-line utility to make REST calls.

## Installation
`restcall` is distributed as a Python package and can be installed using `pip`.
```
python -m pip install restcall
```

## Usage

### Generate a template
```
restcall -t get-service-name.json

restcall -t post-service-name.json
```

### Import template from curl command
```
restcall -u curl-command.txt get-service-name.json
```
The `curl-command.txt` file contains the curl command.

### Modify the generated template

The generated template looks like this:

```json
{
    "url": "",
    "httpMethod": "POST",
    "reqAuthType": "none",
    "reqAuthToken": "",
    "reqContentType": "",
    "reqHeaders": {},
    "reqPayload": "",
    "resFile": ""
}
```
Edit the template and populate the required values.
Here are the parameters, their meaning and the allowed values:
- url - the REST URL
- httpMethod - GET, POST, PUT, PATCH, DELETE
- reqAuthType - `none`, `bearer`, `bearer_generate`, `basic`
- reqAuthToken
    - the actual token if the reqAuthType is `bearer`
    - filepath to the restcall template to generate the token if the reqAuthType is `bearer_generate`
    - `username:password` if the reqAuthType is `basic`
- reqContentType - the request content type. eg. `application/json`
- reqHeaders - the request headers
- reqPayload - the request body. If binary, provide the file path.
- resFile - the file path for storing response externally

### Make the REST call
```
restcall get-service-name.json
```

It will generate the response file `get-service-name-res.json`.

### Output equivalent curl command:
```
restcall -c get-service-name.json
```

## SSL
By default SSL certificate verification is disabled.

## License
This repository and the files under it are licensed under the MIT license.
