#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Alibaba Cloud API
# Copyright (c) 2008-2018 Hive Solutions Lda.
#
# This file is part of Hive Alibaba Cloud API.
#
# Hive Alibaba Cloud API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Alibaba Cloud API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Alibaba Cloud API. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2018 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import hmac
import base64
import hashlib
import datetime

import appier

from . import bucket
from . import object

BASE_URL = "https://oss-cn-beijing.aliyuncs.com/"
""" The default base URL to be used when no other
base URL value is provided to the constructor """

class API(
    appier.API,
    bucket.BucketAPI,
    object.ObjectAPI
):

    def __init__(self, *args, **kwargs):
        appier.API.__init__(self, *args, **kwargs)
        self.base_url = appier.conf("ALIYUN_BASE_URL", BASE_URL)
        self.access_key = appier.conf("ALIYUN_ACCESS_KEY", None)
        self.secret = appier.conf("ALIYUN_SECRET", None)
        self.base_url = kwargs.get("base_url", self.base_url)
        self.access_key = kwargs.get("access_key", self.access_key)
        self.secret = kwargs.get("secret", self.secret)
        self.bucket_url = self.base_url.replace("https://", "https://%s.")

    def build(
        self,
        method,
        url,
        data = None,
        data_j = None,
        data_m = None,
        headers = None,
        params = None,
        mime = None,
        kwargs = None
    ):
        sign = kwargs.pop("sign", False)
        if sign and self.access_key and self.secret:
            headers["Content-MD5"] = self._content_md5(data = data)
            headers["Content-Type"] = self._content_type()
            headers["Date"] = self._date()
            headers["Authorization"] = self._signature(
                method,
                data = data,
                headers = headers
            )

    def _content_md5(self, data = None):
        content_md5 = hashlib.md5(data or b"").digest()
        content_md5 = base64.b64encode(content_md5)
        return appier.legacy.str(content_md5)

    def _content_type(self, data = None):
        return "text/plain"

    def _date(self):
        date = datetime.datetime.utcnow()
        return date.strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _signature(self, method, data = None, headers = None):
        #@todo isto pode ainda não estár set !!!
        content_md5 = headers["Content-MD5"]
        content_type = headers.get("Content-Type", "")
        date = headers["Date"]

        #@todo this is hardcoded for the list operation
        canonical_headers = ""
        canonical_resource = "/"

        secret = appier.legacy.bytes(self.secret, force = True)
        method = appier.legacy.bytes(method, force = True)
        content_md5 = appier.legacy.bytes(content_md5, force = True)
        content_type = appier.legacy.bytes(content_type, force = True)
        date = appier.legacy.bytes(date, force = True)
        canonical_headers = appier.legacy.bytes(canonical_headers, force = True)
        canonical_resource = appier.legacy.bytes(canonical_resource, force = True)

        base = "%s\n%s\n%s\n%s\n%s%s" % (
            method,
            content_md5,
            content_type,
            date,
            canonical_headers,
            canonical_resource
        )
        base = appier.legacy.bytes(base, force = True)

        signature = hmac.new(secret, base, hashlib.sha1).digest()
        signature = base64.b64encode(signature)
        signature = appier.legacy.str(signature)

        return "OSS %s:%s" % (self.access_key, signature)
