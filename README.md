# Svg to Openscad

This script automate the workflow to export 2d shapes from Inkscape into Openscad extrusion code.

## How it works
As of now this project is only a proof of concept and will evolve over time. The basic idea is that you can set metadata on the paths to extrude in inkscape.

When you want to see the shape(s) in 3D the script will do two things : 
1. Split the svg into multiple svg files (one path per file)
2. Parse the path's metadata to generate an openscad extrusion code

To set the metadata in inkscape open the *Objects...* menu and for each path write the metadata in *Label* input area.

The medata syntax is : 

>\<key1\>:\<value1\>;\<key2\>:\<value2\>

Here are the keys and corresponding expected values currently supported : 


|key|Expected Value|Mandatory|Example|Implementation Status|
|---|--------------|---------|-------|---------------------|
|name|The name of the object (string)|Yes|name:shape_name|done|
|extrude|Either linear or rotation (enum)|Yes|extrude:linear|works for linear, rotation throws a **NotImplementedError**|
|height|The height of linear extrusion in milimeters (float)|yes if extrude:linear|height:12.7|done|
|angle|The angle of rotational extrusion in degrees (float)|yes if extrude:rotation|angle:120|Not yet implemented|
|plane|The plane of the extruded object, either XY (default), XZ or YZ (enum)|no|plane:YZ|done


For example the following metadata string : 


```
name:front_low_brace;extrude:linear;height:12.70
```


will render the following openscad code : 


```scad
module front_low_brace(height=12.7){
	linear_extrude(height=height){
		import("./split/front_low_brace.svg");
	}
}
front_low_brace();
```

## Running the script
```sh
python .\svg2scad\svg2scad.py path/to/file.svg
```

## Todo : 
Right now this project is a proof of concept and the items below are a personnal roadmap. You can do a feature proposal by filling a new Issue.
### project management
- [ ] Proper python packaging
- [ ] Complete docstrings
- [ ] Tests
- [ ] Proper error management

### features
- [ ] Complete CLI
- [ ] Manage rotational extrusions