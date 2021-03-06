# pylint: disable=E1101,W0612
# coding: utf-8
"""
This file defines:
  - WriteMesh
"""
from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)
from six import string_types, iteritems, itervalues, PY2
from codecs import open
import warnings

from pyNastran.bdf.utils import print_filename
from pyNastran.utils.gui_io import save_file_dialog
from pyNastran.bdf.fieldWriter import print_card, print_card_8
from pyNastran.bdf.fieldWriter16 import print_card_16
from pyNastran.bdf.field_writer_double import print_card_double


class WriteMesh(object):
    """
    Major methods:
      - model.write_bdf(...)
      - model.echo_bdf(...)
      - model.auto_reject_bdf(...)
    """
    def __init__(self):
        self._auto_reject = True
        self.cards_to_read = set([])

    def echo_bdf(self, infile_name):
        """
        This method removes all comment lines from the bdf
        A write method is stil required.

        .. todo:: maybe add the write method
        """
        self.cards_to_read = set([])
        return self.read_bdf(infile_name)

    def auto_reject_bdf(self, infile_name):
        """
        This method parses supported cards, but does not group them into
        nodes, elements, properties, etc.

        .. todo:: maybe add the write method
        """
        self._auto_reject = True
        return self.read_bdf(infile_name)

    def _output_helper(self, out_filename, interspersed, size, is_double):
        """
        Performs type checking on the write_bdf inputs
        """
        if out_filename is None:
            wildcard_wx = "Nastran BDF (*.bdf; *.dat; *.nas; *.pch)|" \
                "*.bdf;*.dat;*.nas;*.pch|" \
                "All files (*.*)|*.*"
            wildcard_qt = "Nastran BDF (*.bdf *.dat *.nas *.pch);;All files (*)"
            title = 'Save BDF/DAT/PCH'
            out_filename = save_file_dialog(title, wildcard_wx, wildcard_qt)
            assert out_filename is not None, out_filename
        if not isinstance(out_filename, string_types):
            raise TypeError('out_filename=%r must be a string' % out_filename)

        if size == 8:
            assert is_double == False, 'is_double=%r' % is_double
            card_writer = print_card_8
        elif size == 16:
            assert is_double in [True, False], 'is_double=%r' % is_double
            if is_double == False:
                assert is_double == False, 'is_double=%r' % is_double
                card_writer = print_card_16
            else:
                assert is_double == True, 'is_double=%r' % is_double
                card_writer = print_card_double
        else:
            assert size in [8, 16], size

        assert isinstance(interspersed, bool)
        fname = print_filename(out_filename, self._relpath)
        self.log.debug("***writing %s" % fname)
        return out_filename, card_writer

    def write_bdf(self, out_filename=None, interspersed=True,
                  size=8, precision=None, is_double=False, enddata=None):
        """
        Writes the BDF.

        :param self:         the BDF object
        :param out_filename: the name to call the output bdf
                             (default=None; pops a dialog)
        :param interspersed: Writes a bdf with properties & elements
              interspersed like how Patran writes the bdf.  This takes
              slightly longer than if interspersed=False, but makes it
              much easier to compare to a Patran-formatted bdf and is
              more clear. (default=True)
        :param size:  the field size (8 is recommended)
        :param precision:  'single', 'double', None (None -> )
        :param enddata:  Flag to enable/disable writing ENDDATA
                         (default=None -> depends on input BDF)
        """
        if precision is not None:
            if precision == 'double':
                is_double = True
            elif precision == 'single':
                is_double = False
            else:
                raise ValueError('invalid precision=%r' % precision)
            warnings.warn("'precision' has been replaced by 'is_double'; 'single' -> False, 'double' -> True")

        out_filename, card_writer = self._output_helper(out_filename,
                                            interspersed, size, is_double)

        if PY2:
            outfile = open(out_filename, 'wb')
        else:
            outfile = open(out_filename, 'w')
        self._write_header(outfile)
        self._write_params(outfile, size, card_writer)
        self._write_nodes(outfile, size, card_writer, is_double)

        if interspersed:
            self._write_elements_properties(outfile, size, card_writer)
        else:
            self._write_elements(outfile, size, card_writer)
            self._write_properties(outfile, size, card_writer)
        self._write_materials(outfile, size, card_writer)

        self._write_masses(outfile, size, card_writer)
        self._write_common(outfile, size, is_double, card_writer)
        if (enddata is None and 'ENDDATA' in self.card_count) or enddata:
            outfile.write('ENDDATA\n')
        outfile.close()

    def _write_header(self, outfile):
        """
        Writes the executive and case control decks.

        :param self: the BDF object
        """
        self._write_executive_control_deck(outfile)
        self._write_case_control_deck(outfile)

    def _write_executive_control_deck(self, outfile):
        """
        Writes the executive control deck.

        :param self: the BDF object
        """
        if self.executive_control_lines:
            msg = '$EXECUTIVE CONTROL DECK\n'
            if self.sol == 600:
                new_sol = 'SOL 600,%s' % self.solMethod
            else:
                new_sol = 'SOL %s' % self.sol

            if self.iSolLine is not None:
                self.executive_control_lines[self.iSolLine] = new_sol

            for line in self.executive_control_lines:
                msg += line + '\n'
            outfile.write(msg)

    def _write_case_control_deck(self, outfile):
        """
        Writes the Case Control Deck.

        :param self: the BDF object
        """
        if self.caseControlDeck:
            msg = '$CASE CONTROL DECK\n'
            msg += str(self.caseControlDeck)
            assert 'BEGIN BULK' in msg, msg
            outfile.write(''.join(msg))

    def _write_elements(self, outfile, size, card_writer):
        """
        Writes the elements in a sorted order

        :param self: the BDF object
        """
        if self.elements:
            outfile.write('$ELEMENTS\n')
            for (eid, element) in sorted(iteritems(self.elements)):
                try:
                    outfile.write(element.write_bdf(size, card_writer))
                except:
                    print('failed printing element...'
                          'type=%s eid=%s' % (element.type, eid))
                    raise

    def _write_elements_properties(self, outfile, size, card_writer):
        """
        Writes the elements and properties in and interspersed order
        """
        missing_properties = []
        if self.properties:
            outfile.write('$ELEMENTS_WITH_PROPERTIES\n')

        eids_written = []
        pids = sorted(self.properties.keys())
        pid_eids = self.getElementIDsWithPIDs(pids, mode='dict')

        msg = []
        #failed_element_types = set([])
        for (pid, eids) in sorted(iteritems(pid_eids)):
            prop = self.properties[pid]
            if eids:
                msg.append(prop.write_bdf(size, card_writer))
                eids.sort()
                for eid in eids:
                    element = self.Element(eid)
                    try:
                        msg.append(element.write_bdf(size, card_writer))
                    except:
                        print('failed printing element...' 'type=%r eid=%s'
                              % (element.type, eid))
                        raise
                eids_written += eids
            else:
                missing_properties.append(prop.write_bdf(size, card_writer))
        outfile.write(''.join(msg))

        eids_missing = set(self.elements.keys()).difference(set(eids_written))
        if eids_missing:
            msg = ['$ELEMENTS_WITH_NO_PROPERTIES '
                   '(PID=0 and unanalyzed properties)\n']
            for eid in sorted(eids_missing):
                element = self.Element(eid, msg='')
                try:
                    msg.append(element.write_bdf(size, card_writer))
                except:
                    print('failed printing element...'
                          'type=%s eid=%s' % (element.type, eid))
                    raise
            outfile.write(''.join(msg))

        if missing_properties or self.pdampt or self.pbusht or self.pelast:
            msg = ['$UNASSOCIATED_PROPERTIES\n']
            for card in sorted(itervalues(self.pbusht)):
                msg.append(card.write_bdf(size, card_writer))
            for card in sorted(itervalues(self.pdampt)):
                msg.append(card.write_bdf(size, card_writer))
            for card in sorted(itervalues(self.pelast)):
                msg.append(card.write_bdf(size, card_writer))
            for card in missing_properties:
                # this is a string...
                #print("missing_property = ", card
                msg.append(card)
            outfile.write(''.join(msg))

    def _write_aero(self, outfile, size, card_writer):
        """Writes the aero cards"""
        if(self.aero or self.aeros or self.gusts or self.caeros
           or self.paeros or self.trims):
            msg = ['$AERO\n']
            for (unused_id, caero) in sorted(iteritems(self.caeros)):
                msg.append(caero.write_bdf(size, card_writer))
            for (unused_id, paero) in sorted(iteritems(self.paeros)):
                msg.append(paero.write_bdf(size, card_writer))
            for (unused_id, spline) in sorted(iteritems(self.splines)):
                msg.append(spline.write_bdf(size, card_writer))
            for (unused_id, trim) in sorted(iteritems(self.trims)):
                msg.append(trim.write_bdf(size, card_writer))

            for (unused_id, aero) in sorted(iteritems(self.aero)):
                msg.append(aero.write_bdf(size, card_writer))
            for (unused_id, aero) in sorted(iteritems(self.aeros)):
                msg.append(aero.write_bdf(size, card_writer))

            for (unused_id, gust) in sorted(iteritems(self.gusts)):
                msg.append(gust.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_aero_control(self, outfile, size, card_writer):
        """Writes the aero control surface cards"""
        if(self.aefacts or self.aeparams or self.aelinks or self.aelists or
           self.aestats or self.aesurfs):
            msg = ['$AERO CONTROL SURFACES\n']
            for (unused_id, aelinks) in sorted(iteritems(self.aelinks)):
                for aelink in aelinks:
                    msg.append(aelink.write_bdf(size, card_writer))
            for (unused_id, aeparam) in sorted(iteritems(self.aeparams)):
                msg.append(aeparam.write_bdf(size, card_writer))
            for (unused_id, aestat) in sorted(iteritems(self.aestats)):
                msg.append(aestat.write_bdf(size, card_writer))

            for (unused_id, aelist) in sorted(iteritems(self.aelists)):
                msg.append(aelist.write_bdf(size, card_writer))
            for (unused_id, aesurf) in sorted(iteritems(self.aesurfs)):
                msg.append(aesurf.write_bdf(size, card_writer))
            for (unused_id, aefact) in sorted(iteritems(self.aefacts)):
                msg.append(aefact.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_common(self, outfile, size, is_double, card_writer):
        """
        Write the common outputs so none get missed...

        :param self: the BDF object
        :returns msg: part of the bdf
        """
        self._write_rigid_elements(outfile, size, card_writer)
        self._write_dmigs(outfile, size, card_writer)
        self._write_loads(outfile, size, card_writer)
        self._write_dynamic(outfile, size, card_writer)
        self._write_aero(outfile, size, card_writer)
        self._write_aero_control(outfile, size, card_writer)
        self._write_flutter(outfile, size, card_writer)
        self._write_thermal(outfile, size, card_writer)
        self._write_thermal_materials(outfile, size, card_writer)

        self._write_constraints(outfile, size, card_writer)
        self._write_optimization(outfile, size, card_writer)
        self._write_tables(outfile, size, card_writer)
        self._write_sets(outfile, size, card_writer)
        self._write_contact(outfile, size, card_writer)
        self._write_rejects(outfile, size)
        self._write_coords(outfile, size, is_double)

    def _write_constraints(self, outfile, size, card_writer):
        """Writes the constraint cards sorted by ID"""
        if self.suports:
            msg = ['$CONSTRAINTS\n']
            for suport in self.suports:
                msg.append(suport.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

        if self.spcs or self.spcadds:
            msg = ['$SPCs\n']
            str_spc = str(self.spcObject)
            if str_spc:
                msg.append(str_spc)
            else:
                for (spc_id, spcadd) in sorted(iteritems(self.spcadds)):
                    msg.append(str(spcadd))
                for (spc_id, spcs) in sorted(iteritems(self.spcs)):
                    for spc in spcs:
                        msg.append(str(spc))
            outfile.write(''.join(msg))

        if self.mpcs or self.mpcadds:
            msg = ['$MPCs\n']
            for (unused_id, mpcadd) in sorted(iteritems(self.mpcadds)):
                msg.append(str(mpcadd))
            for (unused_id, mpcs) in sorted(iteritems(self.mpcs)):
                for mpc in mpcs:
                    msg.append(mpc.write_bdf(size, card_writer))
            outfile.write(''.join(msg))


    def _write_contact(self, outfile, size, card_writer):
        """Writes the contact cards sorted by ID"""
        if(self.bcrparas or self.bctadds or self.bctparas or self.bctsets
           or self.bsurf or self.bsurfs):
            msg = ['$CONTACT\n']
            for (unused_id, bcrpara) in sorted(iteritems(self.bcrparas)):
                msg.append(bcrpara.write_bdf(size, card_writer))
            for (unused_id, bctadds) in sorted(iteritems(self.bctadds)):
                msg.append(bctadds.write_bdf(size, card_writer))
            for (unused_id, bctpara) in sorted(iteritems(self.bctparas)):
                msg.append(bctpara.write_bdf(size, card_writer))

            for (unused_id, bctset) in sorted(iteritems(self.bctsets)):
                msg.append(bctset.write_bdf(size, card_writer))
            for (unused_id, bsurfi) in sorted(iteritems(self.bsurf)):
                msg.append(bsurfi.write_bdf(size, card_writer))
            for (unused_id, bsurfsi) in sorted(iteritems(self.bsurfs)):
                msg.append(bsurfsi.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_coords(self, outfile, size, is_double):
        """Writes the coordinate cards in a sorted order"""
        msg = []
        if len(self.coords) > 1:
            msg.append('$COORDS\n')
        for (unused_id, coord) in sorted(iteritems(self.coords)):
            if unused_id != 0:
                msg.append(coord.write_bdf(size, is_double))
        outfile.write(''.join(msg))

    def _write_dmigs(self, outfile, size, card_writer):
        """
        Writes the DMIG cards

        :param self:  the BDF object
        :param size:  large field (16) or small field (8)
        :returns msg: string representation of the DMIGs
        """
        msg = []
        for (unused_name, dmig) in sorted(iteritems(self.dmigs)):
            msg.append(dmig.write_bdf(size, card_writer))
        for (unused_name, dmi) in sorted(iteritems(self.dmis)):
            msg.append(dmi.write_bdf(size, card_writer))
        for (unused_name, dmij) in sorted(iteritems(self.dmijs)):
            msg.append(dmij.write_bdf(size, card_writer))
        for (unused_name, dmiji) in sorted(iteritems(self.dmijis)):
            msg.append(dmiji.write_bdf(size, card_writer))
        for (unused_name, dmik) in sorted(iteritems(self.dmiks)):
            msg.append(dmik.write_bdf(size, card_writer))
        outfile.write(''.join(msg))

    def _write_dynamic(self, outfile, size, card_writer):
        """Writes the dynamic cards sorted by ID"""
        if(self.dareas or self.nlparms or self.frequencies or self.methods or
           self.cMethods or self.tsteps or self.tstepnls):
            msg = ['$DYNAMIC\n']
            for (unused_id, method) in sorted(iteritems(self.methods)):
                msg.append(method.write_bdf(size, card_writer))
            for (unused_id, cmethod) in sorted(iteritems(self.cMethods)):
                msg.append(cmethod.write_bdf(size, card_writer))
            for (unused_id, darea) in sorted(iteritems(self.dareas)):
                msg.append(darea.write_bdf(size, card_writer))
            for (unused_id, nlparm) in sorted(iteritems(self.nlparms)):
                msg.append(nlparm.write_bdf(size, card_writer))
            for (unused_id, nlpci) in sorted(iteritems(self.nlpcis)):
                msg.append(nlpci.write_bdf(size, card_writer))
            for (unused_id, tstep) in sorted(iteritems(self.tsteps)):
                msg.append(tstep.write_bdf(size, card_writer))
            for (unused_id, tstepnl) in sorted(iteritems(self.tstepnls)):
                msg.append(tstepnl.write_bdf(size, card_writer))
            for (unused_id, freq) in sorted(iteritems(self.frequencies)):
                msg.append(freq.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_flutter(self, outfile, size, card_writer):
        """Writes the flutter cards"""
        if self.flfacts or self.flutters or self.mkaeros:
            msg = ['$FLUTTER\n']
            for (unused_id, flfact) in sorted(iteritems(self.flfacts)):
                #if unused_id != 0:
                msg.append(flfact.write_bdf(size, card_writer))
            for (unused_id, flutter) in sorted(iteritems(self.flutters)):
                msg.append(flutter.write_bdf(size, card_writer))
            for mkaero in self.mkaeros:
                msg.append(mkaero.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_loads(self, outfile, size, card_writer):
        """Writes the load cards sorted by ID"""
        if self.loads:
            msg = ['$LOADS\n']
            for (key, loadcase) in sorted(iteritems(self.loads)):
                for load in loadcase:
                    try:
                        msg.append(load.write_bdf(size, card_writer))
                    except:
                        print('failed printing load...type=%s key=%r'
                              % (load.type, key))
                        raise
            outfile.write(''.join(msg))

    def _write_masses(self, outfile, size, card_writer):
        if self.properties_mass:
            outfile.write('$PROPERTIES_MASS\n')
            for (pid, mass) in sorted(iteritems(self.properties_mass)):
                try:
                    outfile.write(mass.write_bdf(size, card_writer))
                except:
                    print('failed printing mass property...'
                          'type=%s eid=%s' % (mass.type, pid))
                    raise

        if self.masses:
            outfile.write('$MASSES\n')
            for (eid, mass) in sorted(iteritems(self.masses)):
                try:
                    outfile.write(mass.write_bdf(size, card_writer))
                except:
                    print('failed printing masses...'
                          'type=%s eid=%s' % (mass.type, eid))
                    raise

    def _write_materials(self, outfile, size, card_writer):
        """Writes the materials in a sorted order"""
        if(self.materials or self.hyperelasticMaterials or self.creepMaterials or
           self.MATS1 or self.MATS3 or self.MATS8 or self.MATT1 or
           self.MATT2 or self.MATT3 or self.MATT4 or self.MATT5 or
           self.MATT8 or self.MATT9):
            msg = ['$MATERIALS\n']
            for (mid, material) in sorted(iteritems(self.materials)):
                msg.append(material.write_bdf(size, card_writer))
            for (mid, material) in sorted(iteritems(self.hyperelasticMaterials)):
                msg.append(material.write_bdf(size, card_writer))
            for (mid, material) in sorted(iteritems(self.creepMaterials)):
                msg.append(material.write_bdf(size, card_writer))

            for (mid, material) in sorted(iteritems(self.MATS1)):
                msg.append(material.write_bdf(size, card_writer))
            for (mid, material) in sorted(iteritems(self.MATS3)):
                msg.append(material.write_bdf(size, card_writer))
            for (mid, material) in sorted(iteritems(self.MATS8)):
                msg.append(material.write_bdf(size, card_writer))

            for (mid, material) in sorted(iteritems(self.MATT1)):
                msg.append(material.write_bdf(size, card_writer))
            for (mid, material) in sorted(iteritems(self.MATT2)):
                msg.append(material.write_bdf(size, card_writer))
            for (mid, material) in sorted(iteritems(self.MATT3)):
                msg.append(material.write_bdf(size, card_writer))
            for (mid, material) in sorted(iteritems(self.MATT4)):
                msg.append(material.write_bdf(size, card_writer))
            for (mid, material) in sorted(iteritems(self.MATT5)):
                msg.append(material.write_bdf(size, card_writer))
            for (mid, material) in sorted(iteritems(self.MATT8)):
                msg.append(material.write_bdf(size, card_writer))
            for (mid, material) in sorted(iteritems(self.MATT9)):
                msg.append(material.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_nodes(self, outfile, size, card_writer, is_double):
        """
        Writes the NODE-type cards

        :param self: the BDF object
        """
        if self.spoints:
            msg = []
            msg.append('$SPOINTS\n')
            msg.append(self.spoints.write_bdf2(size, is_double))
            outfile.write(''.join(msg))

        if self.nodes:
            msg = []
            msg.append('$NODES\n')
            if self.gridSet:
                msg.append(self.gridSet.print_card(size))
            for (nid, node) in sorted(iteritems(self.nodes)):
                msg.append(node.write_bdf2(size, is_double))
            outfile.write(''.join(msg))
        if 0:  # not finished
            self._write_nodes_associated(outfile, size, card_writer)

    def _write_nodes_associated(self, outfile, size, card_writer):
        """
        Writes the NODE-type in associated and unassociated groups.

        :param self: the BDF object
        .. warning:: Sometimes crashes, probably on invalid BDFs.
        """
        msg = []
        associated_nodes = set([])
        for (eid, element) in iteritems(self.elements):
            associated_nodes = associated_nodes.union(set(element.nodeIDs()))

        all_nodes = set(self.nodes.keys())
        unassociated_nodes = list(all_nodes.difference(associated_nodes))
        #missing_nodes = all_nodes.difference(

        # TODO: this really shouldn't be a list...???
        associated_nodes = list(associated_nodes)

        if associated_nodes:
            msg += ['$ASSOCIATED NODES\n']
            if self.gridSet:
                msg.append(self.gridSet.write_bdf(size, card_writer))
            # TODO: this really shouldn't be a dictionary...???
            for key, node in sorted(iteritems(associated_nodes)):
                msg.append(node.write_bdf(size, card_writer))

        if unassociated_nodes:
            msg.append('$UNASSOCIATED NODES\n')
            if self.gridSet and not associated_nodes:
                msg.append(self.gridSet.write_bdf(size, card_writer))
            for key, node in sorted(iteritems(unassociated_nodes)):
                if key in self.nodes:
                    msg.append(node.write_bdf(size, card_writer))
                else:
                    msg.append('$ Missing NodeID=%s' % key)
        outfile.write(''.join(msg))

    def _write_optimization(self, outfile, size, card_writer):
        """Writes the optimization cards sorted by ID"""
        if(self.dconstrs or self.desvars or self.ddvals or self.dresps
           or self.dvprels or self.dvmrels or self.doptprm or self.dlinks
           or self.ddvals):
            msg = ['$OPTIMIZATION\n']
            for (unused_id, dconstr) in sorted(iteritems(self.dconstrs)):
                msg.append(dconstr.write_bdf(size, card_writer))
            for (unused_id, desvar) in sorted(iteritems(self.desvars)):
                msg.append(desvar.write_bdf(size, card_writer))
            for (unused_id, ddval) in sorted(iteritems(self.ddvals)):
                msg.append(ddval.write_bdf(size, card_writer))
            for (unused_id, dlink) in sorted(iteritems(self.dlinks)):
                msg.append(dlink.write_bdf(size, card_writer))
            for (unused_id, dresp) in sorted(iteritems(self.dresps)):
                msg.append(dresp.write_bdf(size, card_writer))
            for (unused_id, dvmrel) in sorted(iteritems(self.dvmrels)):
                msg.append(dvmrel.write_bdf(size, card_writer))
            for (unused_id, dvprel) in sorted(iteritems(self.dvprels)):
                msg.append(dvprel.write_bdf(size, card_writer))
            for (unused_id, equation) in sorted(iteritems(self.dequations)):
                msg.append(str(equation))
            if self.doptprm is not None:
                msg.append(self.doptprm.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_params(self, outfile, size, card_writer):
        """
        Writes the PARAM cards

        :param self: the BDF object
        """
        if self.params:
            msg = ['$PARAMS\n']
            for (unused_key, param) in sorted(iteritems(self.params)):
                msg.append(param.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_properties(self, outfile, size, card_writer):
        """Writes the properties in a sorted order"""
        if self.properties:
            msg = ['$PROPERTIES\n']
            for (unused_pid, prop) in sorted(iteritems(self.properties)):
                msg.append(prop.write_bdf(size, card_writer))

            for card in sorted(itervalues(self.pbusht)):
                msg.append(card.write_bdf(size, card_writer))
            for card in sorted(itervalues(self.pdampt)):
                msg.append(card.write_bdf(size, card_writer))
            for card in sorted(itervalues(self.pelast)):
                msg.append(card.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_rejects(self, outfile, size):
        """
        Writes the rejected (processed) cards and the rejected unprocessed
        cardLines
        """
        msg = []
        if self.reject_cards:
            msg.append('$REJECTS\n')
            for reject_card in self.reject_cards:
                try:
                    msg.append(print_card(reject_card))
                except RuntimeError:
                    for field in reject_card:
                        if field is not None and '=' in field:
                            raise SyntaxError('cannot reject equal signed '
                                              'cards\ncard=%s\n' % reject_card)
                    raise

        if self.rejects:
            msg.append('$REJECT_LINES\n')
        for reject_lines in self.rejects:
            #if reject_lines[0]=='' or reject_lines[0][0] == ' ':
                #continue
            #else:
            for reject in reject_lines:
                reject2 = reject.rstrip()
                if reject2:
                    msg.append(str(reject2) + '\n')
        outfile.write(''.join(msg))

    def _write_rigid_elements(self, outfile, size, card_writer):
        """Writes the rigid elements in a sorted order"""
        if self.rigidElements:
            msg = ['$RIGID ELEMENTS\n']
            for (eid, element) in sorted(iteritems(self.rigidElements)):
                try:
                    msg.append(element.write_bdf(size, card_writer))
                except:
                    print('failed printing element...'
                          'type=%s eid=%s' % (element.type, eid))
                    raise
            outfile.write(''.join(msg))

    def _write_sets(self, outfile, size, card_writer):
        """Writes the SETx cards sorted by ID"""
        if(self.sets or self.setsSuper or self.asets or self.bsets or
           self.csets or self.qsets):
            msg = ['$SETS\n']
            for (unused_id, set_obj) in sorted(iteritems(self.sets)):  # dict
                msg.append(set_obj.write_bdf(size, card_writer))
            for set_obj in self.asets:  # list
                msg.append(set_obj.write_bdf(size, card_writer))
            for set_obj in self.bsets:  # list
                msg.append(set_obj.write_bdf(size, card_writer))
            for set_obj in self.csets:  # list
                msg.append(set_obj.write_bdf(size, card_writer))
            for set_obj in self.qsets:  # list
                msg.append(set_obj.write_bdf(size, card_writer))
            for (set_id, set_obj) in sorted(iteritems(self.setsSuper)):  # dict
                msg.append(set_obj.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_tables(self, outfile, size, card_writer):
        """Writes the TABLEx cards sorted by ID"""
        if self.tables:
            msg = ['$TABLES\n']
            for (unused_id, table) in sorted(iteritems(self.tables)):
                msg.append(table.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

        if self.randomTables:
            msg = ['$RANDOM TABLES\n']
            for (unused_id, table) in sorted(iteritems(self.randomTables)):
                msg.append(table.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_thermal(self, outfile, size, card_writer):
        """Writes the thermal cards"""
        # PHBDY
        if self.phbdys or self.convectionProperties or self.bcs:
            # self.thermalProperties or
            msg = ['$THERMAL\n']

            for (unused_key, phbdy) in sorted(iteritems(self.phbdys)):
                msg.append(phbdy.write_bdf(size, card_writer))

            #for unused_key, prop in sorted(iteritems(self.thermalProperties)):
            #    msg.append(str(prop))
            for (unused_key, prop) in sorted(iteritems(self.convectionProperties)):
                msg.append(prop.write_bdf(size, card_writer))

            # BCs
            for (unused_key, bcs) in sorted(iteritems(self.bcs)):
                for bc in bcs:  # list
                    msg.append(bc.write_bdf(size, card_writer))
            outfile.write(''.join(msg))

    def _write_thermal_materials(self, outfile, size, card_writer):
        """Writes the thermal materials in a sorted order"""
        if self.thermalMaterials:
            msg = ['$THERMAL MATERIALS\n']
            for (mid, material) in sorted(iteritems(self.thermalMaterials)):
                msg.append(material.write_bdf(size, card_writer))
            outfile.write(''.join(msg))
