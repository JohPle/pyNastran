from __future__ import (nested_scopes, generators, division, absolute_import,
                        print_function, unicode_literals)


class XRefMesh(object):
    def __init__(self):
        pass
    
    def cross_reference(self, xref=True):
        self.grid.build()
        self.coord.build()

        #self.elements_rod.build()
        self.crod.build()
        self.conrod.build()
        #self.elements_bar.build()
        self.elements_shell.build()
        self.elements_solid.build()

        #self.properties_rod.build()
        self.prod.build()
        #self.properties_bar.build()
        self.properties_shell.build()
        self.properties_solid.build()

        self.materials.build()
        
        self._build_loads()

    def _build_loads(self):
        #self.loadcase.build()
        for load_id, loads in self.load.iteritems():
            for load in loads:
                load.build()
        for load_id, loads in self.dload.iteritems():
            for load in loads:
                load.build()

        #self.loadset.build()
        self.force.build()
        #self.force1.build()
        #self.force2.build()
        self.moment.build()
        #self.moment1.build()
        #self.moment2.build()

        from ..cards.loadcase import LoadCase
        self.loadcase = LoadCase()
        self.loadcase.add_reference(self.load)
        self.loadcase.add_reference(self.dload)
        self.loadcase.add(self.force)
        self.loadcase.add(self.moment)
        
        #self.loadcase.add(self.moment)
        
        self.loadcase.resolve(2)
        self.loadcase.resolve(1)