import bpy
import os
import re
import bmesh

#find path
blend_file_directory = bpy.path.abspath("//")

main_directory_path = os.path.join(blend_file_directory, "data/")

#extract code
def extract_code(name):
    match = re.search(r'\d{4}-\d{4}', name)
    return match.group(0)

index = 0
current_tiles = []

for sub_directory in (os.listdir(main_directory_path)):
    
    sub_directory_path = os.path.join(main_directory_path, sub_directory)
    
    #import terrain    
    terrain_directory = os.path.join(sub_directory_path, "terrain")

    for file_name in sorted(os.listdir(terrain_directory), key=extract_code):
        terrain_file_path = os.path.join(terrain_directory, file_name)
        
        bpy.ops.importgis.georaster(
            filepath = terrain_file_path,
            importMode = "DEM",
            rastCRS = "EPSG:2056",
            demInterpolation = True
        )
        
        #apply modifiers
        imported_obj = bpy.context.object
        for modifier in imported_obj.modifiers:
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        
        #add to current tiles
        current_tiles.append(imported_obj)
    
    #import ortho
    ortho_directory = os.path.join(sub_directory_path, "ortho")

    for file_name in sorted(os.listdir(ortho_directory), key=extract_code):
        ortho_file_path = os.path.join(ortho_directory, file_name)
        
        bpy.ops.importgis.georaster(
            filepath = ortho_file_path,
            importMode = "MESH",
            objectsLst = str(index)
        )
        
        index += 1
        
    #join tiles in one object
    if len(current_tiles) == 4:
        
        imported_obj.name = sub_directory
        
        for obj in current_tiles:
            obj.select_set(True)
        bpy.ops.object.join()
        current_tiles = []
        index -= 3
        
        #edit mode
        bpy.ops.object.editmode_toggle()
        bm = bmesh.from_edit_mesh(imported_obj.data)
        
        #clean mesh
        if bpy.context.object.dimensions.z > 3000:
            
            vertices_to_delete = set()
            
            for vert in bm.verts:
                if vert.co.z < 0:
                    vertices_to_delete.add(vert)
            
            for edge in bm.edges:
                length = (edge.verts[0].co - edge.verts[1].co).length
                if length > 300:
                    if edge.verts[0].co.z < edge.verts[1].co.z:
                        vertices_to_delete.add(edge.verts[0])
                    else:
                        vertices_to_delete.add(edge.verts[1])
            bmesh.ops.delete(bm, geom=list(vertices_to_delete), context='VERTS')
        
        #merge tiles
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=15)
        
        bmesh.update_edit_mesh(imported_obj.data)
        bpy.ops.object.editmode_toggle()
        
        #move object to origin
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        bpy.context.object.location[0] = 0
        bpy.context.object.location[1] = 0
        bpy.context.object.location[2] = 0
        
        #scale
        bpy.context.object.scale *= 0.001
        bpy.ops.object.transform_apply(scale=True)
        
        
        #export to glb
        export_directory = os.path.join(blend_file_directory, "glb export")
        export_path = os.path.join(export_directory, f"{imported_obj.name}.glb")
        
        bpy.ops.export_scene.gltf(
            filepath=export_path,
            export_format='GLB',
            use_selection = True
        )