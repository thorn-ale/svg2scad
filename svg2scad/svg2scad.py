from pathlib import Path
from re import split
import sys
import xml
from svgpathtools import svg2paths, wsvg


class Label:
    """[summary]

    Raises:
        NotImplementedError: [description]

    Returns:
        [type]: [description]
    """
    LINEAR_EXTRUDE_TEMPLATE = 'module {module_name}(height={extrusion_param}){{\n\t{plane_rotation}linear_extrude(height=height){{\n\t\timport("{svg_path}");\n\t}}\n}}\n//{module_name}();\n'
    PLANES = {
        'XY': '',
        'XZ': 'translate([0,height,0])rotate([90,0,0])',
        'YZ': 'rotate([90,0,90])',
        'default': ''
    }

    def __init__(self, label_str: str) -> None:
        """[summary]

        Args:
            label_str (str): [description]
        """
        self._label_str = label_str
        pairs = label_str.split(';')
        rawdata = {}
        for p in pairs:
            key, value = p.split(':')
            rawdata[key.lower()] = value.lower()

        self.name = rawdata['name']
        self.extrusion_method = rawdata['extrude']
        self.extrusion_param = None
        self.plane = 'default'
        if self.extrusion_method == 'linear':
            self.extrusion_param = float(rawdata['height'])
        elif self.extrusion_method == 'revolution':
            self.extrusion_param == float(rawdata['angle'])
        if 'plane' in rawdata.keys():
            self.plane = rawdata['plane'].upper()
        
    def codegen(self, module_name: str, svg_path: Path) -> str:
        """[summary]

        Args:
            module_name (str): [description]
            svg_path (Path): [description]

        Raises:
            NotImplementedError: [description]

        Returns:
            str: [description]
        """
        svg_path = './'+str(svg_path).replace('\\','/')
        if self.extrusion_method == 'linear':
            return Label.LINEAR_EXTRUDE_TEMPLATE.format(module_name=module_name, plane_rotation=Label.PLANES.get(self.plane, ''), extrusion_param=self.extrusion_param, svg_path=svg_path)
        elif self.extrusion_method == 'revolution':
            raise NotImplementedError


class OpenScadCode:
    """[summary]
    """
    def __init__(self) -> None:
        """[summary]
        """
        self.modules = []

    def add(self, module: str) -> None:
        """[summary]

        Args:
            module (str): [description]
        """
        self.modules.append(module)

    def write_code(self, output_file: Path) -> None:
        """[summary]

        Args:
            output_file (Path): [description]
        """
        with open(output_file, 'w', encoding='utf-8') as r:
            r.write('\n'.join(self.modules))

def parse_style(style_string: str) -> dict:
    """[summary]

    Args:
        style_string (str): [description]

    Returns:
        dict: [description]
    """
    return {kv.split(':')[0]:int(kv.split(':')[1]) if kv.split(':')[1].isdigit() else kv.split(':')[1] for kv in style_string.split(';')}

def split_path(svg_file: Path, out_dir: Path) -> OpenScadCode:
    """[summary]

    Args:
        svg_file (Path): [description]
        out_dir (Path): [description]

    Returns:
        OpenScadCode: [description]
    """
    paths, attrs = svg2paths(str(svg_file))
    code = OpenScadCode()
    for path, attr in zip(paths, attrs):
        if 'inkscape:label' not in attr.keys():
            continue
        metadata = Label(attr['inkscape:label'])
        filename = out_dir.joinpath(metadata.name+'.svg')
        code.add(metadata.codegen(metadata.name, filename))
        xmin, xmax, ymin, ymax = path.bbox()
        stroke_width = parse_style(attr['style'])['stroke-width']
        width, height = xmax-xmin+stroke_width, ymax-ymin+stroke_width
        z0 = complex(xmin, ymin)
        #translate path to (0,0)
        path = path.translated(-z0)

        try:
            wsvg([path], attributes=[attr], filename=str(filename), dimensions=(width, height), viewbox=(0, 0, width, height))
        except xml.parsers.expat.ExpatError as e:
            print(f'{e} error exporting {filename}')
            continue
    return code


def main(svg_file: Path):
    out_dir = svg_file.parent.joinpath('split')
    out_dir.mkdir(exist_ok=True)
    code = split_path(svg_file, out_dir)
    code.write_code(out_dir.parent.joinpath('main.scad'))

if __name__ == '__main__':
    main(Path(sys.argv[1]))
