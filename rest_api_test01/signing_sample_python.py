import base64
import email.utils
import hashlib

# pip install httpsig_cffi requests six
import httpsig_cffi.sign
import requests
import six

from datetime import datetime as dt
import time

# Version 1.0.1

class SignedRequestAuth(requests.auth.AuthBase):
    """A requests auth instance that can be reused across requests"""
    generic_headers = [
        "date",
        "(request-target)",
        "host"
    ]
    body_headers = [
        "content-length",
        "content-type",
        "x-content-sha256",
    ]
    required_headers = {
        "get": generic_headers,
        "head": generic_headers,
        "delete": generic_headers,
        "put": generic_headers + body_headers,
        "post": generic_headers + body_headers
    }

    def __init__(self, key_id, private_key):
        # Build a httpsig_cffi.requests_auth.HTTPSignatureAuth for each
        # HTTP method's required headers
        self.signers = {}
        for method, headers in six.iteritems(self.required_headers):
            signer = httpsig_cffi.sign.HeaderSigner(
                key_id=key_id, secret=private_key,
                algorithm="rsa-sha256", headers=headers[:])
            use_host = "host" in headers
            self.signers[method] = (signer, use_host)

    def inject_missing_headers(self, request, sign_body):
        # Inject date, content-type, and host if missing
        request.headers.setdefault(
            "date", email.utils.formatdate(usegmt=True))
        request.headers.setdefault("content-type", "application/json")
        request.headers.setdefault(
            "host", six.moves.urllib.parse.urlparse(request.url).netloc)

        # Requests with a body need to send content-type,
        # content-length, and x-content-sha256
        if sign_body:
            body = request.body or ""
            if "x-content-sha256" not in request.headers:
                m = hashlib.sha256(body.encode("utf-8"))
                base64digest = base64.b64encode(m.digest())
                base64string = base64digest.decode("utf-8")
                request.headers["x-content-sha256"] = base64string
            request.headers.setdefault("content-length", len(body))

    def __call__(self, request):
        verb = request.method.lower()
        # nothing to sign for options
        if verb == "options":
            return request
        signer, use_host = self.signers.get(verb, (None, None))
        if signer is None:
            raise ValueError(
                "Don't know how to sign request verb {}".format(verb))

        # Inject body headers for put/post requests, date for all requests
        sign_body = verb in ["put", "post"]
        self.inject_missing_headers(request, sign_body=sign_body)

        if use_host:
            host = six.moves.urllib.parse.urlparse(request.url).netloc
        else:
            host = None

        signed_headers = signer.sign(
            request.headers, host=host,
            method=request.method, path=request.path_url)
        request.headers.update(signed_headers)
        return request


# -----BEGIN RSA PRIVATE KEY-----
# ...
# -----END RSA PRIVATE KEY-----
def get_auth():
    with open("/root/.oci/config") as cf:
        config = cf.read()
        lines = config.split("\n")
        for l in lines:
            fields = l.split("=")
            if len(fields) > 1:
                if fields[0] == 'user': uocid = fields[1]
                elif fields[0] == 'fingerprint': fnpt = fields[1]
                elif fields[0] == 'tenancy': tocid = fields[1]
                elif fields[0] == 'key_file': kf = fields[1]
                

    with open(kf) as f:
        private_key = f.read().strip()
    # This is the keyId for a key uploaded through the console
    api_key = "/".join([
        tocid,
        uocid,
        fnpt
    ])

    auth = SignedRequestAuth(api_key, private_key)
    return auth

def get_headers():

    headers = {
        "content-type": "application/json",
        "date": email.utils.formatdate(usegmt=True),
        # Uncomment to use a fixed date
        # "date": "Thu, 05 Jan 2014 21:31:40 GMT"
    }
    return headers

def get_objects(uri):
    auth = get_auth()
    headers = get_headers()
    #url = uri + "?compartmentId={compartmentId}"
    #url = url.format(
    #    compartmentId="ocid1.compartment.oc1..aaaaaaaapjubpc2gi5b3o7gxqbyyfww6bnuzsnyrjp6scns2zrw3b2kz2qbq"
    #)
    #uri = "https://objectstorage.us-phoenix-1.oraclecloud.com/n/"
    response = requests.get(uri, auth=auth, headers=headers).json()
    print response["objects"]
    #print response.headers
    return response["objects"]

def get_object_metadata(uri):
    auth = get_auth()
    headers = get_headers()
    response = requests.get(uri, auth=auth, headers=headers)
    tt = dt.strptime(response.headers['last-modified'][:-4], '%a, %d %b %Y %H:%M:%S')
    tt = time.mktime(tt.timetuple())
    res = {'size':int(response.headers['content-length']), 'lastmod':int(tt)}
    print res
    #print dt.microsecond(res['lastmod'])
    return res

def debug_message(m):
    print "================"
    print m
    print "================"
