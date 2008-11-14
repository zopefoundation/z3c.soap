##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

__version__='$Revision: 1.90.2.6 $'[11:-2]

import re
from cgi import FieldStorage, escape
from ZPublisher.Converters import get_converter
from ZPublisher.HTTPRequest import *
from z3c.soap.interfaces import ISOAPRequest
from ZPublisher.TaintedString import TaintedString
from zope.interface import directlyProvides
xmlrpc=None # Placeholder for module that we'll import if we have to.
soap=None

def processInputs(
        self,
        # "static" variables that we want to be local for speed
        SEQUENCE=1,
        DEFAULT=2,
        RECORD=4,
        RECORDS=8,
        REC=12, # RECORD|RECORDS
        EMPTY=16,
        CONVERTED=32,
        hasattr=hasattr,
        getattr=getattr,
        setattr=setattr,
        search_type=re.compile('(:[a-zA-Z][-a-zA-Z0-9_]+|\\.[xy])$').search,
        ):
        """Process request inputs

        We need to delay input parsing so that it is done under
        publisher control for error handling purposes.
        """
        response=self.response
        environ=self.environ
        method=environ.get('REQUEST_METHOD','GET')

        if method != 'GET': fp=self.stdin
        else:               fp=None

        form=self.form
        other=self.other
        taintedform=self.taintedform


        meth=None
        fs=FieldStorage(fp=fp,environ=environ,keep_blank_values=1)
        if not hasattr(fs,'list') or fs.list is None:
            contentType = None
            if fs.headers.has_key('content-type'):
              contentType = fs.headers['content-type']
              # cut off a possible charset definition
              if contentType.find(';') >= 0:
                contentType = contentType[0:contentType.find(';')]
            # Hm, maybe it's an SOAP
            # SOAP 1.1 has HTTP SOAPAction Field
            # SOAP 1.2 has Content-Type application/soap+xml
            #
            # found a Content-Type of text/xml-SOAP on a Microsoft page
            # this page points 3 HTTP-Fields for SOAP Requests:
            # MethodName, InterfaceName (opt) and MessageCall
            #
            if (environ.has_key('HTTP_SOAPACTION') or
                (contentType in ['application/soap+xml',
                                'text/xml',
                                 'text/xml-SOAP']) and fs.value.find('SOAP-ENV:Body') > 0):
                global soap
                if soap is None:
                      import soap
                fp.seek(0)
                directlyProvides(self, ISOAPRequest)
                sparser = soap.SOAPParser(fp.read())
                meth = sparser.method
                self.args = sparser.parse()
                response = soap.SOAPResponse(response)
                response._soap11 = environ.has_key('HTTP_SOAPACTION')
                response._soap12 = (contentType == 'application/soap+xml')
                response._contentType = contentType
                response._method = meth
                response._error_format = 'text/xml'
                other['RESPONSE'] = self.response = response
                other['REQUEST_METHOD'] = method
                self.maybe_webdav_client = 0

            # Hm, maybe it's an XML-RPC
            # check for a real XML-RPC methodCall !
            # This allows to post normal text/xml files to Zope !
            elif (contentType == 'text/xml' and method == 'POST' and fs.value.find('<methodCall>') > 0):
                # Ye haaa, XML-RPC!
                global xmlrpc
                if xmlrpc is None: from ZPublisher import xmlrpc
                meth, self.args = xmlrpc.parse_input(fs.value)
                response=xmlrpc.response(response)
                other['RESPONSE']=self.response=response
                self.maybe_webdav_client = 0
            else:
                self._file=fs.file
        else:
            fslist=fs.list
            tuple_items={}
            lt=type([])
            CGI_name=isCGI_NAME
            defaults={}
            tainteddefaults={}
            converter=None

            for item in fslist:

                isFileUpload = 0
                key=item.name
                if (hasattr(item,'file') and hasattr(item,'filename')
                    and hasattr(item,'headers')):
                    if (item.file and
                        (item.filename is not None
                         # RFC 1867 says that all fields get a content-type.
                         # or 'content-type' in map(lower, item.headers.keys())
                         )):
                        item=FileUpload(item)
                        isFileUpload = 1
                    else:
                        item=item.value

                flags=0
                character_encoding = ''
                # Variables for potentially unsafe values.
                tainted = None
                converter_type = None

                # Loop through the different types and set
                # the appropriate flags

                # We'll search from the back to the front.
                # We'll do the search in two steps.  First, we'll
                # do a string search, and then we'll check it with
                # a re search.


                l=key.rfind(':')
                if l >= 0:
                    mo = search_type(key,l)
                    if mo: l=mo.start(0)
                    else:  l=-1

                    while l >= 0:
                        type_name=key[l+1:]
                        key=key[:l]
                        c=get_converter(type_name, None)

                        if c is not None:
                            converter=c
                            converter_type = type_name
                            flags=flags|CONVERTED
                        elif type_name == 'list':
                            flags=flags|SEQUENCE
                        elif type_name == 'tuple':
                            tuple_items[key]=1
                            flags=flags|SEQUENCE
                        elif (type_name == 'method' or type_name == 'action'):
                            if l: meth=key
                            else: meth=item
                        elif (type_name == 'default_method' or type_name == \
                              'default_action'):
                            if not meth:
                                if l: meth=key
                                else: meth=item
                        elif type_name == 'default':
                            flags=flags|DEFAULT
                        elif type_name == 'record':
                            flags=flags|RECORD
                        elif type_name == 'records':
                            flags=flags|RECORDS
                        elif type_name == 'ignore_empty':
                            if not item: flags=flags|EMPTY
                        elif has_codec(type_name):
                            character_encoding = type_name

                        l=key.rfind(':')
                        if l < 0: break
                        mo=search_type(key,l)
                        if mo: l = mo.start(0)
                        else:  l = -1



                # Filter out special names from form:
                if CGI_name(key) or key[:5]=='HTTP_': continue

                # If the key is tainted, mark it so as well.
                tainted_key = key
                if '<' in key:
                    tainted_key = TaintedString(key)

                if flags:

                    # skip over empty fields
                    if flags&EMPTY: continue

                    #Split the key and its attribute
                    if flags&REC:
                        key=key.split(".")
                        key, attr=".".join(key[:-1]), key[-1]

                        # Update the tainted_key if necessary
                        tainted_key = key
                        if '<' in key:
                            tainted_key = TaintedString(key)

                        # Attributes cannot hold a <.
                        if '<' in attr:
                            raise ValueError(
                                "%s is not a valid record attribute name" %
                                escape(attr))

                    # defer conversion
                    if flags&CONVERTED:
                        try:
                            if character_encoding:
                                # We have a string with a specified character encoding.
                                # This gets passed to the converter either as unicode, if it can
                                # handle it, or crunched back down to latin-1 if it can not.
                                item = unicode(item,character_encoding)
                                if hasattr(converter,'convert_unicode'):
                                    item = converter.convert_unicode(item)
                                else:
                                    item = converter(item.encode('iso-8859-15'))
                            else:
                                item=converter(item)

                            # Flag potentially unsafe values
                            if converter_type in ('string', 'required', 'text',
                                                  'ustring', 'utext'):
                                if not isFileUpload and '<' in item:
                                    tainted = TaintedString(item)
                            elif converter_type in ('tokens', 'lines',
                                                    'utokens', 'ulines'):
                                is_tainted = 0
                                tainted = item[:]
                                for i in range(len(tainted)):
                                    if '<' in tainted[i]:
                                        is_tainted = 1
                                        tainted[i] = TaintedString(tainted[i])
                                if not is_tainted:
                                    tainted = None

                        except:
                            if (not item and not (flags&DEFAULT) and
                                defaults.has_key(key)):
                                item = defaults[key]
                                if flags&RECORD:
                                    item=getattr(item,attr)
                                if flags&RECORDS:
                                    item = getattr(item[-1], attr)
                                if tainteddefaults.has_key(tainted_key):
                                    tainted = tainteddefaults[tainted_key]
                                    if flags&RECORD:
                                        tainted = getattr(tainted, attr)
                                    if flags&RECORDS:
                                        tainted = getattr(tainted[-1], attr)
                            else:
                                raise

                    elif not isFileUpload and '<' in item:
                        # Flag potentially unsafe values
                        tainted = TaintedString(item)

                    # If the key is tainted, we need to store stuff in the
                    # tainted dict as well, even if the value is safe.
                    if '<' in tainted_key and tainted is None:
                        tainted = item

                    #Determine which dictionary to use
                    if flags&DEFAULT:
                        mapping_object = defaults
                        tainted_mapping = tainteddefaults
                    else:
                        mapping_object = form
                        tainted_mapping = taintedform

                    #Insert in dictionary
                    if mapping_object.has_key(key):
                        if flags&RECORDS:
                            #Get the list and the last record
                            #in the list. reclist is mutable.
                            reclist = mapping_object[key]
                            x = reclist[-1]

                            if tainted:
                                # Store a tainted copy as well
                                if not tainted_mapping.has_key(tainted_key):
                                    tainted_mapping[tainted_key] = deepcopy(
                                        reclist)
                                treclist = tainted_mapping[tainted_key]
                                lastrecord = treclist[-1]

                                if not hasattr(lastrecord, attr):
                                    if flags&SEQUENCE: tainted = [tainted]
                                    setattr(lastrecord, attr, tainted)
                                else:
                                    if flags&SEQUENCE:
                                        getattr(lastrecord,
                                            attr).append(tainted)
                                    else:
                                        newrec = record()
                                        setattr(newrec, attr, tainted)
                                        treclist.append(newrec)

                            elif tainted_mapping.has_key(tainted_key):
                                # If we already put a tainted value into this
                                # recordset, we need to make sure the whole
                                # recordset is built.
                                treclist = tainted_mapping[tainted_key]
                                lastrecord = treclist[-1]
                                copyitem = item

                                if not hasattr(lastrecord, attr):
                                    if flags&SEQUENCE: copyitem = [copyitem]
                                    setattr(lastrecord, attr, copyitem)
                                else:
                                    if flags&SEQUENCE:
                                        getattr(lastrecord,
                                            attr).append(copyitem)
                                    else:
                                        newrec = record()
                                        setattr(newrec, attr, copyitem)
                                        treclist.append(newrec)

                            if not hasattr(x,attr):
                                #If the attribute does not
                                #exist, setit
                                if flags&SEQUENCE: item=[item]
                                setattr(x,attr,item)
                            else:
                                if flags&SEQUENCE:
                                    # If the attribute is a
                                    # sequence, append the item
                                    # to the existing attribute
                                    y = getattr(x, attr)
                                    y.append(item)
                                    setattr(x, attr, y)
                                else:
                                    # Create a new record and add
                                    # it to the list
                                    n=record()
                                    setattr(n,attr,item)
                                    mapping_object[key].append(n)
                        elif flags&RECORD:
                            b=mapping_object[key]
                            if flags&SEQUENCE:
                                item=[item]
                                if not hasattr(b,attr):
                                    # if it does not have the
                                    # attribute, set it
                                    setattr(b,attr,item)
                                else:
                                    # it has the attribute so
                                    # append the item to it
                                    setattr(b,attr,getattr(b,attr)+item)
                            else:
                                # it is not a sequence so
                                # set the attribute
                                setattr(b,attr,item)

                            # Store a tainted copy as well if necessary
                            if tainted:
                                if not tainted_mapping.has_key(tainted_key):
                                    tainted_mapping[tainted_key] = deepcopy(
                                        mapping_object[key])
                                b = tainted_mapping[tainted_key]
                                if flags&SEQUENCE:
                                    seq = getattr(b, attr, [])
                                    seq.append(tainted)
                                    setattr(b, attr, seq)
                                else:
                                    setattr(b, attr, tainted)

                            elif tainted_mapping.has_key(tainted_key):
                                # If we already put a tainted value into this
                                # record, we need to make sure the whole record
                                # is built.
                                b = tainted_mapping[tainted_key]
                                if flags&SEQUENCE:
                                    seq = getattr(b, attr, [])
                                    seq.append(item)
                                    setattr(b, attr, seq)
                                else:
                                    setattr(b, attr, item)

                        else:
                            # it is not a record or list of records
                            found=mapping_object[key]

                            if tainted:
                                # Store a tainted version if necessary
                                if not tainted_mapping.has_key(tainted_key):
                                    copied = deepcopy(found)
                                    if isinstance(copied, lt):
                                        tainted_mapping[tainted_key] = copied
                                    else:
                                        tainted_mapping[tainted_key] = [copied]
                                tainted_mapping[tainted_key].append(tainted)

                            elif tainted_mapping.has_key(tainted_key):
                                # We may already have encountered a tainted
                                # value for this key, and the tainted_mapping
                                # needs to hold all the values.
                                tfound = tainted_mapping[tainted_key]
                                if isinstance(tfound, lt):
                                    tainted_mapping[tainted_key].append(item)
                                else:
                                    tainted_mapping[tainted_key] = [tfound,
                                                                    item]

                            if type(found) is lt:
                                found.append(item)
                            else:
                                found=[found,item]
                                mapping_object[key]=found
                    else:
                        # The dictionary does not have the key
                        if flags&RECORDS:
                            # Create a new record, set its attribute
                            # and put it in the dictionary as a list
                            a = record()
                            if flags&SEQUENCE: item=[item]
                            setattr(a,attr,item)
                            mapping_object[key]=[a]

                            if tainted:
                                # Store a tainted copy if necessary
                                a = record()
                                if flags&SEQUENCE: tainted = [tainted]
                                setattr(a, attr, tainted)
                                tainted_mapping[tainted_key] = [a]

                        elif flags&RECORD:
                            # Create a new record, set its attribute
                            # and put it in the dictionary
                            if flags&SEQUENCE: item=[item]
                            r = mapping_object[key]=record()
                            setattr(r,attr,item)

                            if tainted:
                                # Store a tainted copy if necessary
                                if flags&SEQUENCE: tainted = [tainted]
                                r = tainted_mapping[tainted_key] = record()
                                setattr(r, attr, tainted)
                        else:
                            # it is not a record or list of records
                            if flags&SEQUENCE: item=[item]
                            mapping_object[key]=item

                            if tainted:
                                # Store a tainted copy if necessary
                                if flags&SEQUENCE: tainted = [tainted]
                                tainted_mapping[tainted_key] = tainted

                else:
                    # This branch is for case when no type was specified.
                    mapping_object = form

                    if not isFileUpload and '<' in item:
                        tainted = TaintedString(item)
                    elif '<' in key:
                        tainted = item

                    #Insert in dictionary
                    if mapping_object.has_key(key):
                        # it is not a record or list of records
                        found=mapping_object[key]

                        if tainted:
                            # Store a tainted version if necessary
                            if not taintedform.has_key(tainted_key):
                                copied = deepcopy(found)
                                if isinstance(copied, lt):
                                    taintedform[tainted_key] = copied
                                else:
                                    taintedform[tainted_key] = [copied]
                            elif not isinstance(taintedform[tainted_key], lt):
                                taintedform[tainted_key] = [
                                    taintedform[tainted_key]]
                            taintedform[tainted_key].append(tainted)

                        elif taintedform.has_key(tainted_key):
                            # We may already have encountered a tainted value
                            # for this key, and the taintedform needs to hold
                            # all the values.
                            tfound = taintedform[tainted_key]
                            if isinstance(tfound, lt):
                                taintedform[tainted_key].append(item)
                            else:
                                taintedform[tainted_key] = [tfound, item]

                        if type(found) is lt:
                            found.append(item)
                        else:
                            found=[found,item]
                            mapping_object[key]=found
                    else:
                        mapping_object[key]=item
                        if tainted:
                            taintedform[tainted_key] = tainted

            #insert defaults into form dictionary
            if defaults:
                for key, value in defaults.items():
                    tainted_key = key
                    if '<' in key: tainted_key = TaintedString(key)

                    if not form.has_key(key):
                        # if the form does not have the key,
                        # set the default
                        form[key]=value

                        if tainteddefaults.has_key(tainted_key):
                            taintedform[tainted_key] = \
                                tainteddefaults[tainted_key]
                    else:
                        #The form has the key
                        tdefault = tainteddefaults.get(tainted_key, value)
                        if isinstance(value, record):
                            # if the key is mapped to a record, get the
                            # record
                            r = form[key]

                            # First deal with tainted defaults.
                            if taintedform.has_key(tainted_key):
                                tainted = taintedform[tainted_key]
                                for k, v in tdefault.__dict__.items():
                                    if not hasattr(tainted, k):
                                        setattr(tainted, k, v)

                            elif tainteddefaults.has_key(tainted_key):
                                # Find out if any of the tainted default
                                # attributes needs to be copied over.
                                missesdefault = 0
                                for k, v in tdefault.__dict__.items():
                                    if not hasattr(r, k):
                                        missesdefault = 1
                                        break
                                if missesdefault:
                                    tainted = deepcopy(r)
                                    for k, v in tdefault.__dict__.items():
                                        if not hasattr(tainted, k):
                                            setattr(tainted, k, v)
                                    taintedform[tainted_key] = tainted

                            for k, v in value.__dict__.items():
                                # loop through the attributes and value
                                # in the default dictionary
                                if not hasattr(r, k):
                                    # if the form dictionary doesn't have
                                    # the attribute, set it to the default
                                    setattr(r,k,v)
                            form[key] = r

                        elif isinstance(value, lt):
                            # the default value is a list
                            l = form[key]
                            if not isinstance(l, lt):
                                l = [l]

                            # First deal with tainted copies
                            if taintedform.has_key(tainted_key):
                                tainted = taintedform[tainted_key]
                                if not isinstance(tainted, lt):
                                    tainted = [tainted]
                                for defitem in tdefault:
                                    if isinstance(defitem, record):
                                        for k, v in defitem.__dict__.items():
                                            for origitem in tainted:
                                                if not hasattr(origitem, k):
                                                    setattr(origitem, k, v)
                                    else:
                                        if not defitem in tainted:
                                            tainted.append(defitem)
                                taintedform[tainted_key] = tainted

                            elif tainteddefaults.has_key(tainted_key):
                                missesdefault = 0
                                for defitem in tdefault:
                                    if isinstance(defitem, record):
                                        try:
                                            for k, v in \
                                                defitem.__dict__.items():
                                                for origitem in l:
                                                    if not hasattr(origitem, k):
                                                        missesdefault = 1
                                                        raise NestedLoopExit
                                        except NestedLoopExit:
                                            break
                                    else:
                                        if not defitem in l:
                                            missesdefault = 1
                                            break
                                if missesdefault:
                                    tainted = deepcopy(l)
                                    for defitem in tdefault:
                                        if isinstance(defitem, record):
                                            for k, v in defitem.__dict__.items():
                                                for origitem in tainted:
                                                    if not hasattr(origitem, k):
                                                        setattr(origitem, k, v)
                                        else:
                                            if not defitem in tainted:
                                                tainted.append(defitem)
                                    taintedform[tainted_key] = tainted

                            for x in value:
                                # for each x in the list
                                if isinstance(x, record):
                                    # if the x is a record
                                    for k, v in x.__dict__.items():

                                        # loop through each
                                        # attribute and value in
                                        # the record

                                        for y in l:

                                            # loop through each
                                            # record in the form
                                            # list if it doesn't
                                            # have the attributes
                                            # in the default
                                            # dictionary, set them

                                            if not hasattr(y, k):
                                                setattr(y, k, v)
                                else:
                                    # x is not a record
                                    if not x in l:
                                        l.append(x)
                            form[key] = l
                        else:
                            # The form has the key, the key is not mapped
                            # to a record or sequence so do nothing
                            pass

            # Convert to tuples
            if tuple_items:
                for key in tuple_items.keys():
                    # Split the key and get the attr
                    k=key.split( ".")
                    k,attr='.'.join(k[:-1]), k[-1]
                    a = attr
                    new = ''
                    # remove any type_names in the attr
                    while not a=='':
                        a=a.split( ":")
                        a,new=':'.join(a[:-1]), a[-1]
                    attr = new
                    if form.has_key(k):
                        # If the form has the split key get its value
                        tainted_split_key = k
                        if '<' in k: tainted_split_key = TaintedString(k)
                        item =form[k]
                        if isinstance(item, record):
                            # if the value is mapped to a record, check if it
                            # has the attribute, if it has it, convert it to
                            # a tuple and set it
                            if hasattr(item,attr):
                                value=tuple(getattr(item,attr))
                                setattr(item,attr,value)
                        else:
                            # It is mapped to a list of  records
                            for x in item:
                                # loop through the records
                                if hasattr(x, attr):
                                    # If the record has the attribute
                                    # convert it to a tuple and set it
                                    value=tuple(getattr(x,attr))
                                    setattr(x,attr,value)

                        # Do the same for the tainted counterpart
                        if taintedform.has_key(tainted_split_key):
                            tainted = taintedform[tainted_split_key]
                            if isinstance(item, record):
                                seq = tuple(getattr(tainted, attr))
                                setattr(tainted, attr, seq)
                            else:
                                for trec in tainted:
                                    if hasattr(trec, attr):
                                        seq = getattr(trec, attr)
                                        seq = tuple(seq)
                                        setattr(trec, attr, seq)
                    else:
                        # the form does not have the split key
                        tainted_key = key
                        if '<' in key: tainted_key = TaintedString(key)
                        if form.has_key(key):
                            # if it has the original key, get the item
                            # convert it to a tuple
                            item=form[key]
                            item=tuple(form[key])
                            form[key]=item

                        if taintedform.has_key(tainted_key):
                            tainted = tuple(taintedform[tainted_key])
                            taintedform[tainted_key] = tainted

        if meth:
            if environ.has_key('PATH_INFO'):
                path=environ['PATH_INFO']
                while path[-1:]=='/': path=path[:-1]
            else: path=''
            other['PATH_INFO']=path="%s/%s" % (path,meth)
            self._hacked_path=1

HTTPRequest.processInputs = processInputs
import logging
logger = logging.getLogger('Zope')
logger.info("z3c.soap: modified ZPublisher.HTTPRequest.processInputs")

# vi:ts=4
