import xml.dom.minidom as md
import re
import pathlib
import json

import click


#: Atomic KML geometry types supported.
#: MultiGeometry is handled separately.
GEOTYPES = [
  'Polygon',
  'LineString',
  'Point',
  'Track',
  'gx:Track',
  ]

#: Supported style types
STYLE_TYPES = [
  'svg',
  'leaflet',
  ]

SPACE = re.compile(r'\s+')

# ----------------
# Helper functions
# ----------------
def get(node, name):
    """
    Given a KML Document Object Model (DOM) node, return a list
    of its sub-nodes that have the given tag name.
    """
    return node.getElementsByTagName(name)

def get1(node, name):
    """
    Return the first element of ``get(node, name)``, if it exists.
    Otherwise return ``None``.
    """
    s = get(node, name)
    if s:
        return s[0]
    else:
        return None

def attr(node, name):
    """
    Return as a string the value of the given DOM node's attribute named
    by ``name``, if it exists.
    Otherwise, return an empty string.
    """
    return node.getAttribute(name)

def val(node):
    """
    Normalize the given DOM node and return the value
    of its first child (the string content of the node).
    """
    try:
        node.normalize()
        return node.firstChild.wholeText  # Handles CDATASection too
    except AttributeError:
        return ''

def valf(node):
    """
    Cast ``val(node)`` as a float.
    Return ``None`` if that does not work.
    """
    try:
        return float(val(node))
    except ValueError:
        return None

def numarray(a):
    """
    Cast the given list into a list of floats.
    """
    return [float(aa) for aa in a]

def coords1(s):
    """
    Convert the given KML string containing one coordinate tuple into a list
    of floats.

    EXAMPLE::

        >>> coords1(' -112.2,36.0,2357 ')
        [-112.2, 36.0, 2357.0]

    """
    return numarray(re.sub(SPACE, '', s).split(','))

def coords(s):
    """
    Convert the given KML string containing multiple coordinate tuples into
    a list of lists of floats.

    EXAMPLE::

        >>> coords('''
        ... -112.0,36.1,0
        ... -113.0,36.0,0
        ... ''')
        [[-112.0, 36.1, 0.0], [-113.0, 36.0, 0.0]]

    """
    s = s.split() #sub(TRIM_SPACE, '', v).split()
    return [coords1(ss) for ss in s]

def gx_coords1(s):
    """
    Convert the given KML string containing one gx coordinate tuple
    into a list of floats.

    EXAMPLE::

        >>> gx_coords1('-113.0 36.0 0')
        [-113.0, 36.0, 0.0]

    """
    return numarray(s.split(' '))

def gx_coords(node):
    """
    Given a KML DOM node, grab its <gx:coord> and <gx:timestamp><when>
    subnodes, and convert them into a dictionary with the keys and values

    - ``'coordinates'``: list of lists of float coordinates
    - ``'times'``: list of timestamps corresponding to the coordinates

    """
    els = get(node, 'gx:coord')
    coordinates = []
    times = []
    coordinates = [gx_coords1(val(el)) for el in els]
    time_els = get(node, 'when')
    times = [val(t) for t in time_els]
    return {
      'coordinates': coordinates,
      'times': times,
      }

def disambiguate(names, mark='1'):
    """
    Given a list of strings ``names``, return a new list of names
    where repeated names have been disambiguated by repeatedly
    appending the given mark.

    EXAMPLE::

        >>> disambiguate(['sing', 'song', 'sing', 'sing'])
        ['sing', 'song', 'sing1', 'sing11']

    """
    names_seen = set()
    new_names = []
    for name in names:
        new_name = name
        while new_name in names_seen:
            new_name += mark
        new_names.append(new_name)
        names_seen.add(new_name)

    return new_names

def to_filename(s):
    """
    Based on `django/conversiontools/text.py <https://github.com/django/django/blob/master/django/conversiontools/text.py>`_.
    Return the given string converted to a string that can be used for a clean
    filename.
    Specifically, leading and trailing spaces are removed; other
    spaces are converted to underscores; and anything that is not a unicode
    alphanumeric, dash, underscore, or dot, is removed.

    EXAMPLE::

    """
    s = re.sub(r'(?u)[^-\w. ]', '', s)
    s = s.strip().replace(' ', '_')
    return s

# ---------------
# Main functions
# ---------------
def build_rgb_and_opacity(s):
    """
    Given a KML color string, return an equivalent
    RGB hex color string and an opacity float
    rounded to 2 decimal places.

    EXAMPLE::

        >>> build_rgb_and_opacity('ee001122')
        ('#221100', 0.93)

    """
    # Set defaults
    color = '000000'
    opacity = 1

    if s.startswith('#'):
        s = s[1:]
    if len(s) == 8:
        color = s[6:8] + s[4:6] + s[2:4]
        opacity = round(int(s[0:2], 16)/256, 2)
    elif len(s) == 6:
        color = s[4:6] + s[2:4] + s[0:2]
    elif len(s) == 3:
        color = s[::-1]

    return '#' + color, opacity

def build_svg_style(node):
    """
    Given a DOM node, grab its top-level Style nodes, convert
    every one into a SVG style dictionary, put them in
    a master dictionary of the form

        #style ID -> SVG style dictionary,

    and return the result.

    The possible keys and values of each SVG style dictionary,
    the style options, are

    - ``iconUrl``: URL of icon
    - ``stroke``: stroke color; RGB hex string
    - ``stroke-opacity``: stroke opacity
    - ``stroke-width``:  stroke width in pixels
    - ``fill``: fill color; RGB hex string
    - ``fill-opacity``: fill opacity
    """
    d = {}
    for item in get(node, 'Style'):
        style_id = '#' + attr(item, 'id')
        # Create style properties
        props = {}
        for x in get(item, 'PolyStyle'):
            color = val(get1(x, 'color'))
            if color:
                rgb, opacity = build_rgb_and_opacity(color)
                props['fill'] = rgb
                props['fill-opacity'] = opacity
                # Set default border style
                props['stroke'] = rgb
                props['stroke-opacity'] = opacity
                props['stroke-width'] = 1
            fill = valf(get1(x, 'fill'))
            if fill == 0:
                props['fill-opacity'] = fill
            elif fill == 1 and 'fill-opacity' not in props:
                props['fill-opacity'] = fill
            outline = valf(get1(x, 'outline'))
            if outline == 0:
                props['stroke-opacity'] = outline
            elif outline == 1 and 'stroke-opacity' not in props:
                props['stroke-opacity'] = outline
        for x in get(item, 'LineStyle'):
            color = val(get1(x, 'color'))
            if color:
                rgb, opacity = build_rgb_and_opacity(color)
                props['stroke'] = rgb
                props['stroke-opacity'] = opacity
            width = valf(get1(x, 'width'))
            if width is not None:
                props['stroke-width'] = width
        for x in get(item, 'IconStyle'):
            icon = get1(x, 'Icon')
            if not icon:
                continue
            # Clear previous style properties
            props = {}
            props['iconUrl'] = val(get1(icon, 'href'))

        d[style_id] = props

    return d

def build_leaflet_style(node):
    """
    Given a DOM node, grab its top-level Style nodes, convert
    every one into a Leaflet style dictionary, put them in
    a master dictionary of the form

        #style ID -> Leaflet style dictionary,

    and return the result.

    The the possible keys and values of each Leaflet style dictionary,
    the style options, are

    - ``iconUrl``: URL of icon
    - ``color``: stroke color; RGB hex string
    - ``opacity``: stroke opacity
    - ``weight``:  stroke width in pixels
    - ``fillColor``: fill color; RGB hex string
    - ``fillOpacity``: fill opacity
    """
    d = {}
    for item in get(node, 'Style'):
        style_id = '#' + attr(item, 'id')
        # Create style properties
        props = {}
        for x in get(item, 'PolyStyle'):
            color = val(get1(x, 'color'))
            if color:
                rgb, opacity = build_rgb_and_opacity(color)
                props['fillColor'] = rgb
                props['fillOpacity'] = opacity
                # Set default border style
                props['color'] = rgb
                props['opacity'] = opacity
                props['weight'] = 1
            fill = valf(get1(x, 'fill'))
            if fill == 0:
                props['fillOpacity'] = fill
            elif fill == 1 and 'fillOpacity' not in props:
                props['fillOpacity'] = fill
            outline = valf(get1(x, 'outline'))
            if outline == 0:
                props['opacity'] = outline
            elif outline == 1 and 'opacity' not in props:
                props['opacity'] = outline
        for x in get(item, 'LineStyle'):
            color = val(get1(x, 'color'))
            if color:
                rgb, opacity = build_rgb_and_opacity(color)
                props['color'] = rgb
                props['opacity'] = opacity
            width = valf(get1(x, 'width'))
            if width is not None:
                props['weight'] = width
        for x in get(item, 'IconStyle'):
            icon = get1(x, 'Icon')
            if not icon:
                continue
            # Clear previous style properties
            props = {}
            props['iconUrl'] = val(get1(icon, 'href'))

        d[style_id] = props

    return d

def build_geometry(node):
    """
    Return a (decoded) GeoJSON geometry dictionary corresponding
    to the given KML node.
    """
    geoms = []
    times = []
    if get1(node, 'MultiGeometry'):
        return build_geometry(get1(node, 'MultiGeometry'))
    if get1(node, 'MultiTrack'):
        return build_geometry(get1(node, 'MultiTrack'))
    if get1(node, 'gx:MultiTrack'):
        return build_geometry(get1(node, 'gx:MultiTrack'))
    for geotype in GEOTYPES:
        geonodes = get(node, geotype)
        if not geonodes:
            continue
        for geonode in geonodes:
            if geotype == 'Point':
                geoms.append({
                  'type': 'Point',
                  'coordinates': coords1(val(get1(
                    geonode, 'coordinates')))
                  })
            elif geotype == 'LineString':
                geoms.append({
                  'type': 'LineString',
                  'coordinates': coords(val(get1(
                    geonode, 'coordinates')))
                  })
            elif geotype == 'Polygon':
                rings = get(geonode, 'LinearRing')
                coordinates = [coords(val(get1(ring, 'coordinates')))
                  for ring in rings]
                geoms.append({
                  'type': 'Polygon',
                  'coordinates': coordinates,
                  })
            elif geotype in ['Track', 'gx:Track']:
                track = gx_coords(geonode)
                geoms.append({
                  'type': 'LineString',
                  'coordinates': track['coordinates'],
                  })
                if track['times']:
                    times.append(track['times'])

    return {'geoms': geoms, 'times': times}

def build_feature(node):
    """
    Build and return a (decoded) GeoJSON Feature corresponding to
    this KML node (typically a KML Placemark).
    Return ``None`` if no Feature can be built.
    """
    geoms_and_times = build_geometry(node)
    if not geoms_and_times['geoms']:
        return None

    props = {}
    for x in get(node, 'name')[:1]:
        props['name'] = val(x)
    for x in get(node, 'description')[:1]:
        description = val(x)
        if description:
            props['description'] = description
    for x in get(node, 'styleUrl')[:1]:
        style_url = val(x)
        if style_url[0] != '#':
            style_url = '#' + style_url
        props['styleUrl'] = style_url
    for x in get(node, 'PolyStyle')[:1]:
        color = val(get1(x, 'color'))
        if color:
            rgb, opacity = build_rgb_and_opacity(color)
            props['fill'] = rgb
            props['fill-opacity'] = opacity
            # Set default border style
            props['stroke'] = rgb
            props['stroke-opacity'] = opacity
            props['stroke-width'] = 1
        fill = valf(get1(x, 'fill'))
        if fill == 0:
            props['fill-opacity'] = fill
        elif fill == 1 and 'fill-opacity' not in props:
            props['fill-opacity'] = fill
        outline = valf(get1(x, 'outline'))
        if outline == 0:
            props['stroke-opacity'] = outline
        elif outline == 1 and 'stroke-opacity' not in props:
            props['stroke-opacity'] = outline
    for x in get(node, 'LineStyle')[:1]:
        color = val(get1(x, 'color'))
        if color:
            rgb, opacity = build_rgb_and_opacity(color)
            props['stroke'] = rgb
            props['stroke-opacity'] = opacity
        width = valf(get1(x, 'width'))
        if width:
            props['stroke-width'] = width
    for x in get(node, 'ExtendedData')[:1]:
        datas = get(x, 'Data')
        for data in datas:
            props[attr(data, 'name')] = val(get1(
              data, 'value'))
        simple_datas = get(x, 'SimpleData')
        for simple_data in simple_datas:
            props[attr(simple_data, 'name')] = val(simple_data)
    for x in get(node, 'TimeSpan')[:1]:
        begin = val(get1(x, 'begin'))
        end = val(get1(x, 'end'))
        props['timeSpan'] = {'begin': begin, 'end': end}
    if geoms_and_times['times']:
        times = geoms_and_times['times']
        if len(times) == 1:
            props['times'] = times[0]
        else:
            props['times'] = times

    feature = {
      'type': 'Feature',
      'properties': props,
      }

    geoms = geoms_and_times['geoms']
    if len(geoms) == 1:
        feature['geometry'] = geoms[0]
    else:
        feature['geometry'] = {
          'type': 'GeometryCollection',
          'geometries': geoms,
          }

    if attr(node, 'id'):
        feature['id'] = attr(node, 'id')

    return feature

def build_feature_collection(node, name=None):
    """
    Build and return a (decoded) GeoJSON FeatureCollection
    corresponding to this KML DOM node (typically a KML Folder).
    Set the name of the FeatureCollection to the given name
    if it is not ``None``
    """
    # Initialize
    geojson = {
      'type': 'FeatureCollection',
      'features': [],
      }

    # Build features
    for placemark in get(node, 'Placemark'):
        feature = build_feature(placemark)
        if feature is not None:
            geojson['features'].append(feature)

    # Name the collection if requested
    if name is not None:
        geojson['properties']  = {'name': name}

    return geojson

def build_layers(node, disambiguate_names=True):
    """
    Return a list of GeoJSON FeatureCollections,
    one for each folder in the given KML DOM node that contains geodata.
    Name each FeatureCollection (setting its ``properties`` -> ``name`` value)
    according to its corresponding KML folder name.

    If ``disambiguate_names == True``, then disambiguate repeated layer names
    via :func:`disambiguate`.

    Warning: this can produce layers with the same geodata in case
    the KML node has nested folders with geodata.
    """
    layers = []
    names = []
    for i, folder in enumerate(get(node, 'Folder')):
        geojson = build_feature_collection(folder)
        if not geojson['features']:
            continue
        layers.append(geojson)
        name = val(get1(folder, 'name'))
        names.append(name)

    if not layers:
        # No folders, so use the root node
        geojson = build_feature_collection(node)
        if geojson['features']:
            layers.append(geojson)
        name = val(get1(node, 'name'))
        names.append(name)

    if disambiguate_names:
        new_names = disambiguate(names)
        new_layers = []
        for i, layer in enumerate(layers):
            layer['properties'] = {'name': new_names[i]}
            new_layers.append(layer)
        layers = new_layers

    return layers

@click.command()
@click.option('-f', '--separate-folders', is_flag=True,
  default=False)
@click.option('-st', '--style-type', type=click.Choice(STYLE_TYPES),
  default=None)
@click.option('-sf', '--style-filename',
  default='style.json')
@click.argument('kml_path')
@click.argument('output_dir')
def main(kml_path, output_dir, separate_folders=False,
  style_type=None, style_filename='style.json'):
    """
    Given a path to a KML file, convert it to one or several GeoJSON
    FeatureCollection files and save the result(s) to the given
    output directory.

    If ``separate_folders == False`` (the default), then create one
    GeoJSON file.
    If ``separate_folders == True``, then create several GeoJSON
    files, one for each folder in the KML file
    that contains geodata or that has a descendant node that contains geodata.
    Warning: this can produce GeoJSON files with the same geodata in case
    the KML file has nested folders with geodata.

    If a ``style_type`` is given (default is ``None``),
    then also build a JSON style
    file of the given style type and save it to the output directory
    under the name given by ``style_filename``
    (which defaults to 'style.json')
    """
    # Create absolute paths
    kml_path = pathlib.Path(kml_path).resolve()
    if output_dir is None:
        output_dir = kml_path.parent
    else:
        output_dir = pathlib.Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir()
    output_dir = output_dir.resolve()

    # Parse KML
    with kml_path.open('r') as src:
        kml_str = src.read()
    root = md.parseString(kml_str)

    # Build GeoJSON layers
    if separate_folders:
        layers = build_layers(root)
    else:
        name = kml_path.name.replace('.kml', '')
        layers = [build_feature_collection(root, name=name)]

    # Create filenames for layers
    filenames = disambiguate(
      [to_filename(layer['properties']['name'])
      for layer in layers])
    filenames = [name + '.geojson' for name in filenames]

    # Write layers to files
    for i in range(len(layers)):
        path = pathlib.Path(output_dir, filenames[i])
        with path.open('w') as tgt:
            json.dump(layers[i], tgt)

    # Build and export style file if desired
    if style_type in STYLE_TYPES:
        builder_name = 'build_{!s}_style'.format(style_type)
        style_dict = globals()[builder_name](root)
        path = pathlib.Path(output_dir, style_filename)
        with path.open('w') as tgt:
            json.dump(style_dict, tgt)

if __name__ == '__main__':
    main()