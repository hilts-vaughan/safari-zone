"""Supported flat landing areas on visual branches; native tree perches stay disabled."""
def add(g, name, x, z, scale, cherry=False, parent="CenterArrival", base_y=0):
    # The landing rectangles fit entirely inside their branch tops. Visual-only
    # supports avoid introducing overhead player collision around the Center.
    material = 'arrivaldark' if parent == 'CenterArrival' else 'walkgrain'
    if parent == 'ForestGarden':
        # A compact branch tip keeps the dense canopy from reading as scaffolding.
        y = 2.3 * scale + .04 + base_y
        g['box'](name+'Branch0', (x+.45*scale,y-.025*scale,z),
                 (1.1*scale,.05*scale,.16*scale), 'arrivaldark', solid=False, parent=parent)
        g['prefab'](name+'Landing0', 'FunctionalObjects/RockHangout',
                    (x+.7*scale,y+.01,z), (.45*scale,1,.12*scale))
        return
    for index, (sign, height) in enumerate([(1, 2.0), (-1, 2.55)]):
        y = height * scale + (0 if cherry else .04)
        length, depth, thickness = 1.55 * scale, .30 * scale, .065 * scale
        center = x + sign * .65 * scale
        g['box'](name+'Branch'+str(index), (center,y-thickness/2,z),
                 (length,thickness,depth), material, solid=False, parent=parent)
        # Exclude the trunk end and keep a margin inside all branch edges.
        g['prefab'](name+'Landing'+str(index), 'FunctionalObjects/RockHangout',
                    (x+sign*.98*scale,y+.01,z), (.72*scale,1,.24*scale))
