from itertools import izip

from numpy import zeros, searchsorted

from pyNastran.bdf.fieldWriter import set_blank_if_default
from pyNastran.bdf.fieldWriter import print_card
from pyNastran.bdf.bdfInterface.assign_type import (integer, integer_or_blank,
    double, double_or_blank, string_or_blank)


class DLOAD(object):
    type = 'DLOAD'
    def __init__(self, model):
        """
        Defines the DLOAD object.

        :param self: the DLOAD object
        :param model: the BDF object
        """
        self.model = model
        self.load_id = None
        self.scale = None

        #: individual scale factors (corresponds to load_ids)
        self.scale_factors = []
        #: individual load_ids (corresponds to scale_factors)
        self.load_ids = []

    def add_from_bdf(self, card, comment):
        """
        Fills the DLOAD object from the BDF reader

        :param self: the DLOAD object
        :param card:  the BDFCard object
        :param comment: a comment
        """
        if comment:
            self._comment = comment

        #: load ID
        self.load_id = integer(card, 1, 'sid')

        #: overall scale factor
        self.scale = double(card, 2, 'scale')

        # alternating of scale factor & load set ID
        nLoads = len(card) - 3
        assert nLoads % 2 == 0
        for i in xrange(nLoads // 2):
            n = 2 * i + 3
            self.scale_factors.append(double(card, n, 'scaleFactor'))
            self.load_ids.append(integer(card, n + 1, 'loadID'))

    def build(self):
        pass

    def comment(self):
        if hasattr(self, '_comment'):
            return self.comment
        return []

    def get_stats(self):
        msg = []
        msg.append('  %-8s: %i' % ('DLOAD[%s]' % self.load_id))
        return msg

    def write_bdf(self, f, size=8, lids=None):
        list_fields = ['DLOAD', self.load_id, self.scale]
        for (scaleFactor, lid) in izip(self.scale_factors, self.load_ids):
            list_fields += [scaleFactor, lid]
        f.write(print_card(list_fields, size))