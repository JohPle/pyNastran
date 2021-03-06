from six import iteritems
from numpy import zeros

from pyNastran.op2.resultObjects.op2_Objects import ScalarObject
from pyNastran.f06.f06_formatting import writeFloats13E, writeFloats10E, writeFloats8p4F, get_key0


class GridPointStressesArray(ScalarObject):
    """
        msg = header + ['                                  S T R E S S E S   A T   G R I D   P O I N T S   - -     S U R F A C E       5\n',
                        '0                       SURFACE X-AXIS X  NORMAL(Z-AXIS)  Z         REFERENCE COORDINATE SYSTEM FOR SURFACE DEFINITION CID        0\n',
                        '     GRID      ELEMENT            STRESSES IN SURFACE SYSTEM           PRINCIPAL STRESSES            MAX             \n',
                        '     ID          ID    FIBRE   NORMAL-X   NORMAL-Y   SHEAR-XY     ANGLE      MAJOR      MINOR      SHEAR     VON MISES\n']
              #'0     13683          3736    TRIAX6         4.996584E+00   0.0            1.203093E+02   0.0            0.0            0.0'
              #'      13683          3737    TRIAX6        -4.996584E+00   0.0           -1.203093E+02   0.0            0.0            0.0'
              #'      13683                  *TOTALS*       6.366463E-12   0.0           -1.364242E-12   0.0            0.0            0.0'
    """
    def __init__(self, data_code, isubcase, dt):
        ScalarObject.__init__(self, data_code, isubcase)
        self.ntotal = 0
        self.ntimes = 0

    def build(self):
        self.grid_element = zeros((self.ntotal, 2), dtype='int32')
        #oxx, oyy, txy, angle, major, minor, ovm
        self.data = zeros((self.ntimes, self.ntotal, 7), dtype='float32')

    def add_sort1(self, dt, eKey, eid, elemName, nx, ny, txy, angle, majorP, minorP, tmax, ovm):
        self.times[self.itime] = dt
        self.grid_element[self.ntotal, :] = [eKey, eid]
        self.data[self.itime, self.ntotal, :] = [nx, ny, txy, angle, majorP, minorP, tmax, ovm]

    def get_stats(self):
        msg = self.get_data_code()
        if self.nonlinear_factor is not None:  # transient
            ntimes = len(self.nx)
            times0 = get_key0(self.nx)
            nelements = len(self. nx[times0])
            msg.append('  type=%s ntimes=%s nelements=%s\n'
                       % (self.__class__.__name__, ntimes, nelements))
        else:
            nelements = len(self. nx)
            msg.append('  type=%s nelements=%s\n' % (self.__class__.__name__,
                                                     nelements))
        msg.append('  nx, ny, txy, angle, majorP, minorP, tmax, ovm\n')
        return msg

class GridPointStresses(ScalarObject):

    def __init__(self, data_code, is_sort1, isubcase, dt):
        ScalarObject.__init__(self, data_code, isubcase)
        self.nx = {}
        self.ny = {}
        self.txy = {}
        self.angle = {}
        self.majorP = {}
        self.minorP = {}
        self.tmax = {}
        self.ovm = {}

        self.elemName = {}
        self.eids = {}

        self.dt = dt
        if is_sort1:
            if dt is not None:
                self.add = self.add_sort1
        else:
            assert dt is not None
            self.add = self.addSort2

    def get_stats(self):
        msg = self.get_data_code()
        if self.nonlinear_factor is not None:  # transient
            ntimes = len(self.nx)
            times0 = get_key0(self.nx)
            nelements = len(self. nx[times0])
            msg.append('  type=%s ntimes=%s nelements=%s\n'
                       % (self.__class__.__name__, ntimes, nelements))
        else:
            nelements = len(self. nx)
            msg.append('  type=%s nelements=%s\n' % (self.__class__.__name__,
                                                     nelements))
        msg.append('  nx, ny, txy, angle, majorP, minorP, tmax, ovm\n')
        return msg

    def add_new_transient(self, dt):  # eKey
        """initializes the transient variables"""
        self.nx[dt] = {}
        self.ny[dt] = {}
        self.txy[dt] = {}
        self.angle[dt] = {}
        self.majorP[dt] = {}
        self.minorP[dt] = {}
        self.tmax[dt] = {}
        self.ovm[dt] = {}

        self.elemName = {}
        self.eids = {}

    def add(self, dt, eKey, eid, elemName, nx, ny, txy, angle, majorP, minorP, tmax, ovm):
        if eKey not in self.nx:
            self.eids[eKey] = []
            self.elemName[eKey] = []
            self.nx[eKey] = []
            self.ny[eKey] = []
            self.txy[eKey] = []
            self.angle[eKey] = []
            self.majorP[eKey] = []
            self.minorP[eKey] = []
            self.tmax[eKey] = []
            self.ovm[eKey] = []
        self.nx[eKey].append(nx)
        self.ny[eKey].append(ny)
        self.txy[eKey].append(txy)
        self.angle[eKey].append(angle)
        self.majorP[eKey].append(majorP)
        self.minorP[eKey].append(minorP)
        self.tmax[eKey].append(tmax)
        self.ovm[eKey].append(ovm)

        self.elemName[eKey].append(elemName)
        self.eids[eKey].append(eid)

    def add_sort1(self, dt, eKey, eid, elemName, nx, ny, txy, angle, majorP, minorP, tmax, ovm):
        if dt not in self.nx:
            self.add_new_transient(dt)

        #print "%s=%s eKey=%s eid=%s elemName=%s f1=%s" %(self.data_code['name'],dt,eKey,eid,elemName,f1)
        if eKey not in self.nx[dt]:
            self.eids[eKey] = []
            self.elemName[eKey] = []
            self.nx[dt][eKey] = []
            self.ny[dt][eKey] = []
            self.txy[dt][eKey] = []
            self.angle[dt][eKey] = []
            self.majorP[dt][eKey] = []
            self.minorP[dt][eKey] = []
            self.tmax[dt][eKey] = []
            self.ovm[dt][eKey] = []
        self.eids[eKey].append(eid)
        self.elemName[eKey].append(elemName)

        self.nx[dt][eKey].append(nx)
        self.ny[dt][eKey].append(ny)
        self.txy[dt][eKey].append(txy)
        self.angle[dt][eKey].append(angle)
        self.majorP[dt][eKey].append(majorP)
        self.minorP[dt][eKey].append(minorP)
        self.tmax[dt][eKey].append(tmax)
        self.ovm[dt][eKey].append(ovm)

    def delete_transient(self, dt):
        del self.nx[dt]
        del self.ny[dt]
        del self.txy[dt]
        del self.angle[dt]
        del self.majorP[dt]
        del self.minorP[dt]
        del self.tmax[dt]
        del self.ovm[dt]

    def get_transients(self):
        k = self.nx.keys()
        k.sort()
        return k

    #def cleanupObj(self):
        #k = self.elemName.keys()
        #self.elemName = self.elemName[k[0]]
        #self.eids = self.eids[k[0]]

    def write_f06(self, header, page_stamp, page_num=1, f=None, is_mag_phase=False):
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, page_stamp, page_num, f)

        msg = header + ['                                  S T R E S S E S   A T   G R I D   P O I N T S   - -     S U R F A C E       5\n',
                        '0                       SURFACE X-AXIS X  NORMAL(Z-AXIS)  Z         REFERENCE COORDINATE SYSTEM FOR SURFACE DEFINITION CID        0\n',
                        '     GRID      ELEMENT            STRESSES IN SURFACE SYSTEM           PRINCIPAL STRESSES            MAX             \n',
                        '     ID          ID    FIBRE   NORMAL-X   NORMAL-Y   SHEAR-XY     ANGLE      MAJOR      MINOR      SHEAR     VON MISES\n']
              #'0     13683          3736    TRIAX6         4.996584E+00   0.0            1.203093E+02   0.0            0.0            0.0'
              #'      13683          3737    TRIAX6        -4.996584E+00   0.0           -1.203093E+02   0.0            0.0            0.0'
              #'      13683                  *TOTALS*       6.366463E-12   0.0           -1.364242E-12   0.0            0.0            0.0'
        for eKey, nxs in sorted(iteritems(self.nx)):
            eKey2 = eKey
            zero = '0'
            for iLoad, nx in enumerate(nxs):
                ny = self.ny[eKey][iLoad]
                txy = self.txy[eKey][iLoad]
                angle = self.angle[eKey][iLoad]
                majorP = self.majorP[eKey][iLoad]
                minorP = self.minorP[eKey][iLoad]
                tmax = self.tmax[eKey][iLoad]
                ovm = self.ovm[eKey][iLoad]

                (elemName) = self.elemName[eKey][iLoad]
                eid = self.eids[eKey][iLoad]
                vals = [nx, ny, txy, majorP, minorP, tmax, ovm]
                (vals2, is_all_zeros) = writeFloats10E(vals)
                [nx, ny, txy, majorP, minorP, tmax, ovm] = vals2
                if eid == 0:
                    eid = zero
                angle, isAllZero = writeFloats8p4F([angle])
                anglei = angle[0]
                msg.append('%s%8s  %8s   %4s    %s %s %s   %8s %10s %10s %10s  %s\n' % (zero, eKey2, eid, elemName, nx, ny, txy, anglei, majorP, minorP, tmax, ovm))
                zero = ' '
                eKey2 = ' '
        msg.append(page_stamp % page_num)
        f.write(''.join(msg))
        return page_num

    def _write_f06_transient(self, header, page_stamp, page_num=1, f=None, is_mag_phase=False):
        f.write('GridPointStressesObject write_f06 is not implemented...\n')
        return page_num
        #raise NotImplementedError()
        msg = header + ['                                  S T R E S S E S   A T   G R I D   P O I N T S   - -     S U R F A C E       5\n',
                        '0                       SURFACE X-AXIS X  NORMAL(Z-AXIS)  Z         REFERENCE COORDINATE SYSTEM FOR SURFACE DEFINITION CID        0\n',
                        '     GRID      ELEMENT            STRESSES IN SURFACE SYSTEM           PRINCIPAL STRESSES            MAX             \n',
                        '     ID          ID    FIBRE   NORMAL-X   NORMAL-Y   SHEAR-XY     ANGLE      MAJOR      MINOR      SHEAR     VON MISES\n']
              #'0     13683          3736    TRIAX6         4.996584E+00   0.0            1.203093E+02   0.0            0.0            0.0'
              #'      13683          3737    TRIAX6        -4.996584E+00   0.0           -1.203093E+02   0.0            0.0            0.0'
              #'      13683                  *TOTALS*       6.366463E-12   0.0           -1.364242E-12   0.0            0.0            0.0'
        for dt, Forces in sorted(iteritems(self.forces)):
            for eKey, force in sorted(iteritems(Forces)):
                zero = '0'
                for iLoad, f in enumerate(force):
                    (f1, f2, f3) = f
                    (m1, m2, m3) = self.moments[dt][eKey][iLoad]
                    (elemName) = self.elemName[eKey][iLoad]
                    eid = self.eids[eKey][iLoad]

                    vals = [f1, f2, f3, m1, m2, m3]
                    (vals2, is_all_zeros) = writeFloats13E(vals)
                    [f1, f2, f3, m1, m2, m3] = vals2
                    if eid == 0:
                        eid = ''
                    msg.append('%s  %8s    %10s    %8s      %10s  %10s  %10s  %10s  %10s  %s\n' % (zero, eKey, eid, elemName, f1, f2, f3, m1, m2, m3))
                    zero = ' '

            msg.append(page_stamp % page_num)
            f.write(''.join(msg))
            msg = ['']
            page_num += 1
        return page_num - 1


class GridPointStressesVolume(ScalarObject):
    def __init__(self, data_code, is_sort1, isubcase, dt):
        ScalarObject.__init__(self, data_code, isubcase)
        self.nx = {}
        self.ny = {}
        self.nz = {}
        self.txy = {}
        self.tyz = {}
        self.txz = {}
        self.pressure = {}
        self.ovm = {}

        self.elemName = {}
        self.eids = {}

        self.dt = dt
        if is_sort1:
            if dt is not None:
                self.add = self.add_sort1
        else:
            assert dt is not None
            self.add = self.addSort2

    def get_stats(self):
        msg = self.get_data_code()
        if self.nonlinear_factor is not None:  # transient
            ntimes = len(self.nx)
            times0 = get_key0(self.nx)
            nelements = len(self. nx[times0])
            msg.append('  type=%s ntimes=%s nelements=%s\n'
                       % (self.__class__.__name__, ntimes, nelements))
        else:
            nelements = len(self. nx)
            msg.append('  type=%s nelements=%s\n' % (self.__class__.__name__,
                                                     nelements))
        msg.append('  nx, ny, nz, txy, tyz, txz, pressure, ovm\n')
        return msg

    def add_new_transient(self, dt):  # eKey
        """initializes the transient variables"""
        self.nx[dt] = {}
        self.ny[dt] = {}
        self.nz[dt] = {}
        self.txy[dt] = {}
        self.tyz[dt] = {}
        self.txz[dt] = {}
        self.pressure[dt] = {}
        self.ovm[dt] = {}

        self.elemName = {}
        self.eids = {}

    def add(self, dt, eKey, nx, ny, nz, txy, tyz, txz, pressure, ovm):
        if eKey not in self.nx:
            #self.eids[eKey] = []
            #self.elemName[eKey] = []
            self.nx[eKey] = []
            self.ny[eKey] = []
            self.nz[eKey] = []
            self.txy[eKey] = []
            self.tyz[eKey] = []
            self.txz[eKey] = []
            self.pressure[eKey] = []
            self.ovm[eKey] = []
        self.nx[eKey].append(nx)
        self.ny[eKey].append(ny)
        self.nz[eKey].append(nz)
        self.txy[eKey].append(txy)
        self.tyz[eKey].append(tyz)
        self.txz[eKey].append(txz)
        self.pressure[eKey].append(pressure)
        self.ovm[eKey].append(ovm)

        #self.elemName[eKey].append(elemName)
        #self.eids[eKey].append(eid)

    def add_sort1(self, dt, eKey, nx, ny, nz, txy, tyz, txz, pressure, ovm):
        if dt not in self.nx:
            self.add_new_transient(dt)

        #print "%s=%s eKey=%s eid=%s elemName=%s f1=%s" %(self.data_code['name'],dt,eKey,eid,elemName,f1)
        if eKey not in self.nx[dt]:
            #self.eids[eKey] = []
            #self.elemName[eKey] = []
            self.nx[dt][eKey] = []
            self.ny[dt][eKey] = []
            self.nz[dt][eKey] = []
            self.txy[dt][eKey] = []
            self.tyz[dt][eKey] = []
            self.txz[dt][eKey] = []
            self.pressure[eKey] = []
            self.ovm[dt][eKey] = []
        self.eids[eKey].append(eid)
        #self.elemName[eKey].append(elemName)

        self.nx[dt][eKey].append(nx)
        self.ny[dt][eKey].append(ny)
        self.nz[dt][eKey].append(nz)
        self.txy[dt][eKey].append(txy)
        self.tyz[dt][eKey].append(tyz)
        self.txz[dt][eKey].append(txz)
        self.pressure[dt][eKey].append(pressure)
        self.ovm[dt][eKey].append(ovm)

    def delete_transient(self, dt):
        del self.nx[dt]
        del self.ny[dt]
        del self.nz[dt]
        del self.txy[dt]
        del self.tyz[dt]
        del self.txz[dt]
        del self.pressure[dt]
        del self.ovm[dt]

    def get_transients(self):
        k = self.nx.keys()
        k.sort()
        return k

    #def cleanupObj(self):
        #k = self.elemName.keys()
        #self.elemName = self.elemName[k[0]]
        #self.eids = self.eids[k[0]]

    def write_f06(self, header, page_stamp, page_num=1, f=None, is_mag_phase=False):
        f.write('GridPointStressesVolumeObject write_f06 is not implemented...\n')
        return page_num

        #raise NotImplementedError()
        if self.nonlinear_factor is not None:
            return self._write_f06_transient(header, page_stamp, page_num, f)

        msg = header + ['                                  S T R E S S E S   A T   G R I D   P O I N T S   - -     S U R F A C E       5\n',
                        '0                       SURFACE X-AXIS X  NORMAL(Z-AXIS)  Z         REFERENCE COORDINATE SYSTEM FOR SURFACE DEFINITION CID        0\n',
                        '     GRID      ELEMENT            STRESSES IN SURFACE SYSTEM           PRINCIPAL STRESSES            MAX             \n',
                        '     ID          ID    FIBRE   NORMAL-X   NORMAL-Y   SHEAR-XY     ANGLE      MAJOR      MINOR      SHEAR     VON MISES\n']
              #'0     13683          3736    TRIAX6         4.996584E+00   0.0            1.203093E+02   0.0            0.0            0.0'
              #'      13683          3737    TRIAX6        -4.996584E+00   0.0           -1.203093E+02   0.0            0.0            0.0'
              #'      13683                  *TOTALS*       6.366463E-12   0.0           -1.364242E-12   0.0            0.0            0.0'
        for eKey, nxs in sorted(iteritems(self.nx)):
            eKey2 = eKey
            zero = '0'
            for iLoad, nx in enumerate(nxs):
                ny = self.ny[eKey][iLoad]
                nz = self.nz[eKey][iLoad]
                txy = self.txy[eKey][iLoad]
                tyz = self.tyz[eKey][iLoad]
                txz = self.txz[eKey][iLoad]
                pressure = self.pressure[eKey][iLoad]
                ovm = self.ovm[eKey][iLoad]

                #(elemName) = self.elemName[eKey][iLoad]
                #eid = self.eids[eKey][iLoad]
                vals = [nx, ny, nz, txy, tyz, txz, pressure, ovm]
                (vals2, is_all_zeros) = writeFloats10E(vals)
                [nx, ny, nz, txy, tyz, txz, pressure, ovm] = vals2
                msg.append('%s%8s  %s %s %s   %s %s %s %s  %-s\n' % (zero, eKey, nx, ny, nz, txy, tyz, txz, pressure, ovm.rstrip()))
                zero = ' '
                eKey2 = ' '

        msg.append(page_stamp % page_num)
        f.write(''.join(msg))
        return page_num

    def _write_f06_transient(self, header, page_stamp, page_num=1, f=None, is_mag_phase=False):
        f.write('GridPointStressesVolume _write_f06_transient is not implemented...\n')
        return page_num
        #raise NotImplementedError()
        msg = header + ['                                  S T R E S S E S   A T   G R I D   P O I N T S   - -     S U R F A C E       5\n',
                        '0                       SURFACE X-AXIS X  NORMAL(Z-AXIS)  Z         REFERENCE COORDINATE SYSTEM FOR SURFACE DEFINITION CID        0\n',
                        '     GRID      ELEMENT            STRESSES IN SURFACE SYSTEM           PRINCIPAL STRESSES            MAX             \n',
                        '     ID          ID    FIBRE   NORMAL-X   NORMAL-Y   SHEAR-XY     ANGLE      MAJOR      MINOR      SHEAR     VON MISES\n']
              #'0     13683          3736    TRIAX6         4.996584E+00   0.0            1.203093E+02   0.0            0.0            0.0'
              #'      13683          3737    TRIAX6        -4.996584E+00   0.0           -1.203093E+02   0.0            0.0            0.0'
              #'      13683                  *TOTALS*       6.366463E-12   0.0           -1.364242E-12   0.0            0.0            0.0'
        for dt, Forces in sorted(iteritems(self.forces)):
            for eKey, force in sorted(iteritems(Forces)):
                zero = '0'
                for iLoad, f in enumerate(force):
                    (f1, f2, f3) = f
                    (m1, m2, m3) = self.moments[dt][eKey][iLoad]
                    (elemName) = self.elemName[eKey][iLoad]
                    eid = self.eids[eKey][iLoad]

                    vals = [f1, f2, f3, m1, m2, m3]
                    (vals2, is_all_zeros) = writeFloats13E(vals)
                    [f1, f2, f3, m1, m2, m3] = vals2
                    if eid == 0:
                        eid = ''

                    msg.append('%s  %8s    %10s    %8s      %s  %s  %s  %s  %s  %-s\n' % (zero, eKey, eid, elemName, f1, f2, f3, m1, m2, m3))
                    zero = ' '

            msg.append(page_stamp % page_num)
            f.write(''.join(msg))
            msg = ['']
            page_num += 1
        return page_num - 1
