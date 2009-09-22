SOAP Support
============

This SOAP implementation allows you provide SOAP views for objects. The
SOAP layer is based on `ZSI <http://pywebsvcs.sourceforge.net/>`__.

The package requires ZSI 2.0 or better.

SOAP support is implemented in a way very similar to the standard Zope
XML-RPC support.  To call methods via SOAP, you need to create and
register SOAP views.

This package is largely inspired from Zope 3 SOAP (http://svn.zope.org/soap).

Let's write a simple SOAP view that echoes various types of input:

  >>> import ZSI
  >>> from Products.Five import BrowserView
  >>> class EchoView(BrowserView):
  ...
  ...     def echoString(self, value):
  ...         return value
  ...
  ...     def echoStringArray(self, value):
  ...         return value
  ...
  ...     def echoInteger(self, value):
  ...         return value
  ...
  ...     def echoIntegerArray(self, value):
  ...         return value
  ...
  ...     def echoFloat(self, value):
  ...         return value
  ...
  ...     def echoFloatArray(self, value):
  ...         return value
  ...
  ...     def echoStruct(self, value):
  ...         return value
  ...
  ...     def echoStructArray(self, value):
  ...         return value
  ...
  ...     def echoVoid(self):
  ...         return
  ...
  ...     def echoBase64(self, value):
  ...         import base64
  ...         return base64.encodestring(value)
  ...
  ...     def echoDate(self, value):
  ...         import time
  ...         return time.gmtime(time.mktime(value))
  ...
  ...     def echoDecimal(self, value):
  ...         return value
  ...
  ...     def echoBoolean(self, value):
  ...         return value
  ...
  ...     def ValidateEmailRequest(self, requestData, response):
  ...         mail = requestData._Email
  ...         response._Status = '%s is OK' % mail
  ...         return response
  ...
  ...     def testFault(self):
  ...         raise ZSI.Fault(ZSI.Fault.Client, "Testing the zsi fault")



Now we'll register it as a SOAP view. For now we'll just register the
view for folder objects and call it on the root folder:

  >>> from zope.configuration import xmlconfig
  >>> ignored = xmlconfig.string("""
  ... <configure
  ...     xmlns="http://namespaces.zope.org/zope"
  ...     xmlns:browser="http://namespaces.zope.org/browser"
  ...     xmlns:soap="http://namespaces.zope.org/soap"
  ...     >
  ...
  ...   <!-- We only need to do this include in this example,
  ...        Normally the include has already been done for us. -->
  ...
  ...   <include package="z3c.soap" file="meta.zcml" />
  ...   <include package="Products.Five" file="meta.zcml" />
  ...   <include package="z3c.soap"/>
  ...
  ...   <soap:view
  ...       for="OFS.interfaces.IFolder"
  ...       methods="echoString echoStringArray echoInteger echoIntegerArray
  ...                echoFloat echoFloatArray echoStruct echoVoid echoBase64
  ...                echoDate echoDecimal echoBoolean ValidateEmailRequest
  ...                testFault"
  ...       class="z3c.soap.README.EchoView"
  ...       permission="zope2.SOAPAccess"
  ...       />
  ...
  ...   <utility
  ...       factory="z3c.soap.tests.mailvalidation.validateEmailIn"
  ...       name="ValidateEmailRequest"
  ...       provides="z3c.soap.interfaces.IZSIRequestType"/>
  ...
  ...   <utility
  ...       factory="z3c.soap.tests.mailvalidation.validateEmailOut"
  ...       name="ValidateEmailRequest"
  ...       provides="z3c.soap.interfaces.IZSIResponseType"/>
  ...
  ...
  ... </configure>
  ... """)


And call our SOAP method:

  >>> from Testing.ZopeTestCase import user_name, user_password
  >>> self.setRoles(['Manager'])

  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoString xmlns:m="http://www.soapware.org/">
  ...      <arg1 xsi:type="xsd:string">hello</arg1>
  ...    </m:echoString>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password), handle_errors=True)
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml
  <BLANKLINE>
  ...hello...


Note that we get an unauthorized error if we don't supply authentication
credentials, because we protected the view with the ManageContent permission
when we registered it:

  >>> self.logout()
  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoString xmlns:m="http://www.soapware.org/">
  ...      <arg1 xsi:type="xsd:string">hello</arg1>
  ...    </m:echoString>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """)
  HTTP/1.0 401 Unauthorized
  Content-Length: ...
  Content-Type: text/xml
  Www-Authenticate: basic realm="Zope2"
  <BLANKLINE>
  <SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body><SOAP-ENV:Fault><faultcode>SOAP-ENV:Server</faultcode><faultstring>Not authorized</faultstring></SOAP-ENV:Fault></SOAP-ENV:Body></SOAP-ENV:Envelope>


Parameters
----------

SOAP views can take any parameters that ZSI can understand. The following
demonstrate the use of primitive SOAP-defined types:

  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoString xmlns:m="http://www.soapware.org/">
  ...      <arg1 xsi:type="xsd:string">hello</arg1>
  ...    </m:echoString>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml...
  <BLANKLINE>
  ...hello...


  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoStringArray xmlns:m="http://www.soapware.org/">
  ...    <param SOAP-ENC:arrayType="xsd:ur-type[4]" xsi:type="SOAP-ENC:Array">
  ...    <item xsi:type="xsd:string">one</item>
  ...    <item xsi:type="xsd:string">two</item>
  ...    <item xsi:type="xsd:string">three</item>
  ...    <item xsi:type="xsd:string">four</item>
  ...    </param>
  ...    </m:echoStringArray>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml...
  <BLANKLINE>
  ...one...two...three...four...


  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoInteger xmlns:m="http://www.soapware.org/">
  ...      <arg1 xsi:type="xsd:int">42</arg1>
  ...    </m:echoInteger>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml...
  <BLANKLINE>
  ...42...


  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoIntegerArray xmlns:m="http://www.soapware.org/">
  ...    <param SOAP-ENC:arrayType="xsd:ur-type[4]" xsi:type="SOAP-ENC:Array">
  ...    <item xsi:type="xsd:int">1</item>
  ...    <item xsi:type="xsd:int">2</item>
  ...    <item xsi:type="xsd:int">3</item>
  ...    <item xsi:type="xsd:int">4</item>
  ...    </param>
  ...    </m:echoIntegerArray>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml...
  <BLANKLINE>
  ...1...2...3...4...


Note that floats are returned as xsd:decimal values:

  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoFloat xmlns:m="http://www.soapware.org/">
  ...      <arg1 xsi:type="xsd:float">42.2</arg1>
  ...    </m:echoFloat>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml
  <BLANKLINE>
  ...xsi:type="xsd:float">42.200000</...


Even if they're in float arrays:

  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoFloatArray xmlns:m="http://www.soapware.org/">
  ...    <param SOAP-ENC:arrayType="xsd:ur-type[4]" xsi:type="SOAP-ENC:Array">
  ...    <item xsi:type="xsd:float">1.1</item>
  ...    <item xsi:type="xsd:float">2.2</item>
  ...    <item xsi:type="xsd:float">3.3</item>
  ...    <item xsi:type="xsd:float">4.4</item>
  ...    </param>
  ...    </m:echoFloatArray>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml
  <BLANKLINE>
  ...xsi:type="xsd:float">1.100000</...
  ...xsi:type="xsd:float">2.200000</...
  ...xsi:type="xsd:float">3.300000</...
  ...xsi:type="xsd:float">4.400000</...


  >>> result = http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoStruct xmlns:m="http://www.soapware.org/">
  ...      <param>
  ...      <first xsi:type="xsd:string">first 1</first>
  ...      <last xsi:type="xsd:string">last 1</last>
  ...      </param>
  ...    </m:echoStruct>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))

  >>> result = str(result)
  >>> assert(result.find('first 1') > -1)
  >>> assert(result.find('last 1') > -1)


Note that arrays of structs (at least per the interop suite) do not
seem to work:

  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  ...  xmlns:so="http://soapinterop.org/">
  ...  <SOAP-ENV:Body>
  ...    <m:echoStructArray xmlns:m="http://www.soapware.org/xsd">
  ...    <inputArray SOAP-ENC:arrayType="so:SOAPStruct[2]"
  ...                xsi:type="SOAP-ENC:Array">
  ...      <item xsi:type="so:SOAPStruct">
  ...      <varString xsi:type="xsd:string">str 1</varString>
  ...      <varInt xsi:type="xsd:int">1</varInt>
  ...      </item>
  ...      <item xsi:type="so:SOAPStruct">
  ...      <varString xsi:type="xsd:string">str 2</varString>
  ...      <varInt xsi:type="xsd:int">2</varInt>
  ...      </item>
  ...    </inputArray>
  ...    </m:echoStructArray>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password), handle_errors=True)
  HTTP/1.0 500 Internal Server Error
  Content-Length: ...
  Content-Type: text/xml
  <BLANKLINE>
  <SOAP-ENV:Envelope ...
  ...
  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoVoid xmlns:m="http://www.soapware.org/">
  ...    </m:echoVoid>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml
  <BLANKLINE>
  ...echoVoidResponse...


  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoBase64 xmlns:m="http://www.soapware.org/">
  ...      <arg1 xsi:type="SOAP-ENC:base64">AAECAwQF</arg1>
  ...    </m:echoBase64>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml...
  <BLANKLINE>
  ...AAECAwQF...


Datetimes appear to work:

  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoDate xmlns:m="http://www.soapware.org/">
  ...      <arg1 xsi:type="xsd:dateTime">1970-11-27T11:34:56.000Z</arg1>
  ...    </m:echoDate>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml...
  <BLANKLINE>
  ...1970-11-27T10:34:56...

  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoDecimal xmlns:m="http://www.soapware.org/">
  ...      <arg1 xsi:type="xsd:float">123456789.0123</arg1>
  ...    </m:echoDecimal>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml...
  <BLANKLINE>
  ...123456789.0123...


  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 102
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoBoolean xmlns:m="http://www.soapware.org/">
  ...      <arg1 xsi:type="xsd:boolean">1</arg1>
  ...    </m:echoBoolean>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml...
  <BLANKLINE>
  ...1...



Faults
------

If you need to raise an error, you can either raise an exception as usual
or (if you need more control over fault info) return a `ZSI.Fault` object
directly. Either case causes a fault response to be returned:

  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 104
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:echoInteger xmlns:m="http://www.soapware.org/">
  ...      <arg1 xsi:type="xsd:int">hello</arg1>
  ...    </m:echoInteger>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password), handle_errors=True)
  HTTP/1.0 500 Internal Server Error
  Content-Length: ...
  Content-Type: text/xml
  <BLANKLINE>
  <SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body><SOAP-ENV:Fault><faultcode>SOAP-ENV:Server</faultcode><faultstring>Processing Failure</faultstring><detail><ZSI:FaultDetail><ZSI:string>
  ...

Here is a ZSI Fault response:

  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 104
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <?xml version="1.0"?>
  ... <SOAP-ENV:Envelope
  ...  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ...  <SOAP-ENV:Body>
  ...    <m:testFault xmlns:m="http://www.soapware.org/">
  ...    </m:testFault>
  ...  </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>
  ... """ % (user_name, user_password), handle_errors=True)
  HTTP/1.0 200 OK
  Content-Length: 488
  Content-Type: text/xml
  <BLANKLINE>
  <SOAP-ENV:Envelope xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ZSI="http://www.zolera.com/schemas/ZSI/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Header></SOAP-ENV:Header><SOAP-ENV:Body><SOAP-ENV:Fault><faultcode>SOAP-ENV:Client</faultcode><faultstring>Testing the zsi fault</faultstring></SOAP-ENV:Fault></SOAP-ENV:Body></SOAP-ENV:Envelope>


Complex Types
-------------

For ZSI to successfully marshal complex values (instances of classes),
you must define a typecode that describes the object (see the ZSI docs
for details on defining typecodes). Once the typecode is defined, it must
be accessible through an instance via the attribute name 'typecode' to
be automatically marshalled.


  >>> print http(r"""
  ... POST /test_folder_1_ HTTP/1.0
  ... Authorization: Basic %s:%s
  ... Content-Length: 104
  ... Content-Type: text/xml
  ... SOAPAction: /
  ...
  ... <SOAP-ENV:Envelope
  ...  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  ...  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  ...  xmlns:ZSI="http://www.zolera.com/schemas/ZSI/"
  ...  xmlns:xsd="http://www.w3.org/2001/XMLSchema"
  ...  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  ... <SOAP-ENV:Header></SOAP-ENV:Header>
  ... <SOAP-ENV:Body xmlns:ns1="urn:ws-xwebservices-com:XWebEmailValidation:EmailValidation:v2:Messages">
  ...   <ns1:ValidateEmailRequest>
  ...     <ns1:Email>jfroche@affinitic.be</ns1:Email>
  ...   </ns1:ValidateEmailRequest>
  ... </SOAP-ENV:Body>
  ... </SOAP-ENV:Envelope>""" % (user_name, user_password))
  HTTP/1.0 200 OK
  Content-Length: ...
  Content-Type: text/xml
  <BLANKLINE>
  ...jfroche@affinitic.be is OK...

