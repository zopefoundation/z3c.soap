from ZSI import TCcompound, TC
from ZSI.schema import LocalElementDeclaration, ElementDeclaration
from ZSI.schema import GED


class ns0:
    targetNamespace = "urn:ws-xwebservices-com:XWebEmailValidation:EmailValidation:v2"


class ns1:
    targetNamespace = "urn:ws-xwebservices-com:XWebEmailValidation:EmailValidation:v2:Messages"

    class ValidateEmailRequest_Dec(TCcompound.ComplexType, ElementDeclaration):
        literal = "ValidateEmailRequest"
        schema = "urn:ws-xwebservices-com:XWebEmailValidation:EmailValidation:v2:Messages"

        def __init__(self, **kw):
            ns = ns1.ValidateEmailRequest_Dec.schema
            TClist = [TC.String(pname=(ns, "Email"), aname="_Email",
                                minOccurs=1, maxOccurs=1, nillable=False,
                                typed=False, encoded=kw.get("encoded"))]
            kw["pname"] = (u'urn:ws-xwebservices-com:XWebEmailValidation:EmailValidation:v2:Messages', u'ValidateEmailRequest')
            kw["aname"] = "_ValidateEmailRequest"
            self.attribute_typecode_dict = {}
            TCcompound.ComplexType.__init__(self, None, TClist, inorder=0, **kw)

            class Holder:
                typecode = self

                def __init__(self):
                    # pyclass
                    self._Email = None
                    return
            Holder.__name__ = "ValidateEmailRequest_Holder"
            self.pyclass = Holder


    class ValidateEmailResponse_Dec(TCcompound.ComplexType, ElementDeclaration):
        literal = "ValidateEmailResponse"
        schema = "urn:ws-xwebservices-com:XWebEmailValidation:EmailValidation:v2:Messages"

        def __init__(self, **kw):
            ns = ns1.ValidateEmailResponse_Dec.schema
            TClist = [self.__class__.Status_Dec(minOccurs=1, maxOccurs=1,
                                                nillable=False,
                                                encoded=kw.get("encoded"))]
            kw["pname"] = (u'urn:ws-xwebservices-com:XWebEmailValidation:EmailValidation:v2:Messages', u'ValidateEmailResponse')
            kw["aname"] = "_ValidateEmailResponse"
            self.attribute_typecode_dict = {}
            TCcompound.ComplexType.__init__(self, None, TClist, inorder=0, **kw)

            class Holder:
                typecode = self

                def __init__(self):
                    # pyclass
                    self._Status = None
                    return

            Holder.__name__ = "ValidateEmailResponse_Holder"
            self.pyclass = Holder

        class Status_Dec(TC.String, LocalElementDeclaration):
            literal = "Status"
            schema = "urn:ws-xwebservices-com:XWebEmailValidation:EmailValidation:v2:Messages"

            def __init__(self, **kw):
                kw["pname"] = "Status"
                kw["aname"] = "_Status"
                TC.String.__init__(self, **kw)

                class IHolder(str):
                    typecode=self
                self.pyclass = IHolder
                IHolder.__name__ = "_Status_immutable_holder"

validateEmailIn = GED("urn:ws-xwebservices-com:XWebEmailValidation:EmailValidation:v2:Messages", "ValidateEmailRequest").pyclass
validateEmailOut = GED("urn:ws-xwebservices-com:XWebEmailValidation:EmailValidation:v2:Messages", "ValidateEmailResponse").pyclass
