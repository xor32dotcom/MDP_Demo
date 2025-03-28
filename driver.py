import struct

## CREDIT MPOADMIN2978
## ESPECIAL THANKS TO JAYVEER, SHALASHASKA, SNAKE SWISS
# File paths
mdp_file_path = "gun_camera.mdp"  # Update with correct path
obj_file_path = "gun_camera.obj"

# Face buffer offsets and counts (triangle strips)
face_buffers = [
    (0x000001D0, 0x00000088),
    (0x00000B60, 0x00000004),
    (0x00000BB0, 0x0000007B),
    (0x00001460, 0x00000004),
    (0x000014B0, 0x0000001C),
    (0x000016B0, 0x00000046),
    (0x00001BA0, 0x00000052),
    (0x00002170, 0x0000001C),
    (0x00002370, 0x00000008),
    (0x00002400, 0x00000070),
]

entry_size = 0x12  # 18 bytes per vertex entry

def extract_flipped_triangle_strips(mdp_file_path, obj_file_path, face_buffers, entry_size):
    vertices = []
    normals = []
    faces = []
    vertex_index = 1  # OBJ uses 1-based indexing

    with open(mdp_file_path, "rb") as f:
        for offset, face_count in face_buffers:
            f.seek(offset)  # Jump to the face buffer section
            
            strip_vertices = []  # Stores the strip's vertices
            
            for _ in range(face_count):
                data = f.read(entry_size)
                if len(data) < entry_size:
                    break  # Stop if we reach the end of readable data

                # Extract vertex data (vec3Short at offset 0xC in struct)
                vert_x, vert_y, vert_z = struct.unpack("<hhh", data[12:18])

                # Extract normal data (vec3Short at offset 0x8 in struct)
                norm_x, norm_y, norm_z = struct.unpack("<hhh", data[8:14])

                # Convert short (int16) to float with a scale of 1/4096.0
                scale = 1 / 32768

                ##TODO: research if normals need same coefficient 
                ##3 points to a vertex, clockwise or anticlockwise direction for the culling
                vertices.append((vert_x * scale * 100 , vert_y * scale * 100, vert_z * scale * 100))
                normals.append((norm_x * scale, norm_y * scale, norm_z * scale))

                # Store the vertex in the strip list
                strip_vertices.append(vertex_index)
                
                # Triangle strip handling with alternating face flipping
                if len(strip_vertices) > 2:
                    if len(strip_vertices) % 2 == 0:  # Flip every other face
                        faces.append((strip_vertices[-2], strip_vertices[-3], strip_vertices[-1]))
                    else:
                        faces.append((strip_vertices[-3], strip_vertices[-2], strip_vertices[-1]))

                vertex_index += 1

    # Write to OBJ file
    with open(obj_file_path, "w") as obj_file:
        obj_file.write("# Extracted MDP Model using Correct Triangle Strips with Alternating Flip\n")
        for v in vertices:
            obj_file.write(f"v {v[0]} {v[1]} {v[2]}\n")
        for n in normals:
            obj_file.write(f"vn {n[0]} {n[1]} {n[2]}\n")
        for f in faces:
            obj_file.write(f"f {f[0]} {f[1]} {f[2]}\n")

    print(f"OBJ file saved: {obj_file_path}")

# Run the extraction with alternating face flipping
extract_flipped_triangle_strips(mdp_file_path, obj_file_path, face_buffers, entry_size)
