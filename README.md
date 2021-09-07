# restcall
A small command line script to invoke REST APIs

## Usage

### Generate a template
```
restcall -g get-service-name.json

restcall -g post-service-name.json
```

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
    "reqPayload": {}
}
```
Edit the template and populate the required values.
Here are the parameters, their meaning and the allowed values:
- url - the REST URL
- httpMethod - GET, POST, PUT, PATCH, DELETE
- reqAuthType - none, bearer
- reqAuthToken - the actual token if the reqAuthType is `bearer`
- reqContentType - the request content type. eg. `application/json`
- reqHeaders - the request headers
- reqPayload - the request body

### Make the REST call

```
restcall get-service-name.json
```

It will generate the response file `get-service-name-res.json`.

## License
This repository and the files under it are licensed under the MIT license.
