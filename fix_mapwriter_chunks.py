import argparse
import nbt


# TODO:
# - read a directory of region files
# - read every region file, copy chunks to new region file and make them readable
# - write new 'result' region directory

def fix_mapwriter_chunks(world_path, from_x, from_z, to_x, to_z):
    if from_x >= to_x or from_z >= to_z:
        raise Exception("Invalid range.")

    world = nbt.world.AnvilWorldFolder(world_path)

    for x in range(from_x, to_x + 1):
        for z in range(from_z, to_z + 1):
            rx, cx = divmod(x, 32)
            rz, cz = divmod(z, 32)

            if (rx, rz) not in world.regions and (rx, rz) not in world.regionfiles:
                continue

            region = world.get_region(rx, rz)

            try:
                chunk = region.get_nbt(cx, cz)
            except nbt.region.InconceivedChunk:
                continue

            chunk['Level']['TerrainPopulated'] = nbt.nbt.TAG_Byte()
            chunk['Level']['TerrainPopulated'].value = 1

            chunk['Level']['LightPopulated'] = nbt.nbt.TAG_Byte()
            chunk['Level']['LightPopulated'].value = 0

            chunk['Level']['HeightMap'] = nbt.nbt.TAG_Int_Array()
            chunk['Level']['HeightMap'].value = [0 for _ in range(256)]

            # chunk['Level']['Entities'] = nbt.nbt.TAG_List()
            # chunk['Level']['Entities'].value = []

            # chunk['Level']['TileEntities'] = nbt.nbt.TAG_List()
            # chunk['Level']['TileEntities'].value = []

            for section in chunk['Level']['Sections']:
                if 'Blocks' not in section:
                    section['Blocks'] = nbt.nbt.TAG_Byte_Array()
                    section['Blocks'].value = bytearray(4096)
                if 'Data' not in section:
                    section['Data'] = nbt.nbt.TAG_Byte_Array()
                    section['Data'].value = bytearray(2048)
                if 'Add' not in section:
                    section['Add'] = nbt.nbt.TAG_Byte_Array()
                    section['Add'].value = bytearray(2048)
                if 'BlockLight' not in section:
                    section['BlockLight'] = nbt.nbt.TAG_Byte_Array()
                    section['BlockLight'].value = bytearray(2048)
                if 'SkyLight' not in section:
                    section['SkyLight'] = nbt.nbt.TAG_Byte_Array()
                    section['SkyLight'].value = bytearray(2048)

            region.write_chunk(cx, cz, chunk)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("world_path", type=str, help="path to the world directory")
    parser.add_argument("from_x", type=int, help="from X chunk coordinate")
    parser.add_argument("from_z", type=int, help="from Z chunk coordinate")
    parser.add_argument("to_x", type=int, help="to X chunk coordinate")
    parser.add_argument("to_z", type=int, help="to Z chunk coordinate")

    args = parser.parse_args()

    fix_mapwriter_chunks(args.world_path, args.from_x, args.from_z, args.to_x, args.to_z)
