from numpy import array,log,exp
from baseCard import BaseCard

class Set(BaseCard):
    type = 'Set'
    def __init__(self,card,data):
        ## Unique identification number. (Integer > 0)
        self.sid = None
        ## list of IDs in the SETx
        self.IDs = None

    def cleanIDs(self):
        self.IDs = list(set(self.IDs))

    def SetIDs(self):
        return self.IDs

    def reprFields(self):
        fields = self.rawFields()
        return fields

class SetSuper(Set):
    def __init__(self,card,data):
        ## Superelement identification number. Must be a primary superelement. (Integer >= 0)
        self.seid = None
        ## list of IDs in the SESETx
        self.IDs = None

class SET1(Set):
    """
    Defines a list of structural grid points or element identification numbers.
    SET1 SID ID1 ID2 ID3 ID4 ID5 ID6 ID7
    ID8 -etc.-
    SET1 3 31 62 93 124 16 17 18
    19
    SET1 6 29 32 THRU 50 61 THRU 70
    17 57
    """
    type = 'SET1'
    def __init__(self,card=None,data=None): ## @todo doesnt support data
        Set.__init__(self,card,data)
        ## Unique identification number. (Integer > 0)
        self.sid = card.field(1)

        ## List of structural grid point or element identification numbers. (Integer > 0 or
        ## 'THRU'; for the 'THRU' option, ID1 < ID2 or 'SKIN'; in field 3)
        self.IDs = []

        fields = card.fields(2)
        self.isSkin = False
        i = 0
        if isinstance(fields[0],str) and fields[0].upper()=='SKIN':
            self.isSkin = True
            i+=1
        self.IDs = self.expandThru(fields[i:])
        self.cleanIDs()

    def IsSkin(self):
        return self.isSkin

    def rawFields(self):
        fields = ['SET1',self.sid]
        if self.isSkin:
            fields.append('SKIN')
        fields += self.SetIDs()
        return fields

class SET3(Set):
    """
    Defines a list of grids, elements or points.
    SET3 SID DES ID1 ID2 ID3 ID4 ID5 ID6
    ID7 ID8 -etc-
    SET3 1 POINT 11 12
    """
    type = 'SET1'
    def __init__(self,card=None,data=None): ## @todo doesnt support data
        Set.__init__(self,card,data)
        ## Unique identification number. (Integer > 0)
        self.sid = card.field(1)
        
        #Set description (Character). Valid options are 'GRID', 'ELEM', 'POINT' and 'PROP'.
        self.desc = card.field(2).upper()
        assert self.desc in ['GRID','POINT','ELEM','PROP']

        ## Identifiers of grids points, elements, points or properties. (Integer > 0)
        self.IDs = []

        fields = card.fields(2)
        self.IDs = self.expandThru(fields)
        self.cleanIDs()

    def IsPoint(self):
        if self.desc=='GRID':
            return True
        return False

    def IsPoint(self):
        if self.desc=='POINT':
            return True
        return False

    def IsProperty(self):
        if self.desc=='PROP':
            return True
        return False

    def IsElement(self):
        if self.desc=='ELEM':
            return True
        return False
    
    def rawFields(self):
        fields = ['SET3',self.sid,self.desc]+self.SetIDs()
        return fields

class SESET(SetSuper):
    """
    Defines interior grid points for a superelement.
    """
    type = 'SESET'
    def __init__(self,card=None,data=None):
        SetSuper.__init__(self,card,data)
        self.seid = card.field(1,0)
        ## Grid or scalar point identification number. (0 < Integer < 1000000; G1 < G2)
        self.IDs = []

        fields = card.fields(2)
        self.IDs = self.expandThru(fields)
        self.cleanIDs()

    def rawFields(self):
        fields = ['SESET',self.seid]+self.SetIDs()
        return fields

class SEQSEP(SetSuper): # not integrated...is this an SESET ???
    """
    Used with the CSUPER entry to define the correspondence of the
    exterior grid points between an identical or mirror-image superelement
    and its primary superelement.
    """
    type = 'SEQSEP'
    def __init__(self,card=None,data=None):
        SetSuper.__init__(self,card,data)
        ## Identification number for secondary superelement. (Integer >= 0).
        self.ssid = card.field(1)
        ## Identification number for the primary superelement. (Integer >= 0).
        self.psid = card.field(2)
        ## Exterior grid point identification numbers for the primary superelement. (Integer > 0)
        self.IDs = []

        fields = card.fields(3)
        self.IDs = self.expandThru(fields)
        self.cleanIDs()

    def rawFields(self):
        fields = ['SEQSEP',self.ssid,self.psid]+self.SetIDs()
        return fields

class RADSET(Set): # not integrated
    """
    Specifies which radiation cavities are to be included for
    radiation enclosure analysis.
    RADSET ICAVITY1 ICAVITY2 ICAVITY3 ICAVITY4 ICAVITY5 ICAVITY6 ICAVITY7 ICAVITY8
    ICAVITY9 -etc.-
    """
    type = 'SESET'
    def __init__(self,card=None,data=None):
        Set.__init__(self,card,data)
        self.seid = card.field(1)
        ## Grid or scalar point identification number. (0 < Integer < 1000000; G1 < G2)
        self.IDs = []

        fields = card.fields(2)
        self.IDs = self.expandThru(fields)
        self.cleanIDs()

    def addRadsetObject(self,radset):
        self.IDs += radset.IDs
        self.cleanIDs()
        
    def rawFields(self):
        fields = ['SESET',self.seid]+self.SetIDs()
        return fields
