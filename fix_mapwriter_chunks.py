import argparse
import os
from glob import glob
from shutil import copyfile

from nbt import nbt
from nbt.region import RegionFile, RegionFileFormatError


def fix_mapwriter_chunks(input_region_path: str, output_region_path: str):
    input_region_path = os.path.abspath(input_region_path)
    output_region_path = os.path.abspath(output_region_path)

    if not os.path.isdir(input_region_path):
        raise Exception(f"{input_region_path} is not a directory")
    elif len(os.listdir(input_region_path)) == 0:
        raise Exception(f"{input_region_path} is empty")

    if os.path.exists(output_region_path):
        if not os.path.isdir(output_region_path):
            raise Exception(f"{output_region_path} is not a directory")

        if len(os.listdir(output_region_path)) > 0:
            raise Exception(f"{output_region_path} is not empty")
    else:
        os.mkdir(output_region_path)

    input_mca_paths = glob(os.path.join(input_region_path, "*.mca"))
    count = len(input_mca_paths)

    for i, input_mca_path in enumerate(input_mca_paths):
        basename = os.path.basename(input_mca_path)
        print(f"{basename} ({i+1}/{count})")

        output_mca_path = os.path.join(output_region_path, basename)
        if not os.path.exists(output_mca_path):
            copyfile(input_mca_path, output_mca_path)

        input_region = RegionFile(input_mca_path)
        output_region = RegionFile(
            os.path.join(output_region_path, os.path.basename(input_mca_path))
        )

        for m in input_region.get_metadata():
            try:
                chunk = input_region.get_chunk(m.x, m.z)
            except RegionFileFormatError:
                continue

            chunk["Level"]["TerrainPopulated"] = nbt.TAG_Byte()
            chunk["Level"]["TerrainPopulated"].value = 1

            chunk["Level"]["LightPopulated"] = nbt.TAG_Byte()
            chunk["Level"]["LightPopulated"].value = 0

            chunk["Level"]["HeightMap"] = nbt.TAG_Int_Array()
            chunk["Level"]["HeightMap"].value = [0 for _ in range(256)]

            # chunk['Level']['Entities'] = nbt.TAG_List()
            # chunk['Level']['Entities'].value = []

            # chunk['Level']['TileEntities'] = nbt.TAG_List()
            # chunk['Level']['TileEntities'].value = []

            for section in chunk["Level"]["Sections"]:
                if "Blocks" not in section:
                    section["Blocks"] = nbt.TAG_Byte_Array()
                    section["Blocks"].value = bytearray(4096)
                if "Data" not in section:
                    section["Data"] = nbt.TAG_Byte_Array()
                    section["Data"].value = bytearray(2048)
                if "Add" not in section:
                    section["Add"] = nbt.TAG_Byte_Array()
                    section["Add"].value = bytearray(2048)
                if "BlockLight" not in section:
                    section["BlockLight"] = nbt.TAG_Byte_Array()
                    section["BlockLight"].value = bytearray(2048)
                if "SkyLight" not in section:
                    section["SkyLight"] = nbt.TAG_Byte_Array()
                    section["SkyLight"].value = bytearray(2048)

            output_region.write_chunk(m.x, m.z, chunk)

        input_region.close()
        output_region.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_region_path",
        type=str,
        help="path to the region directory to use as input",
    )
    parser.add_argument(
        "output_region_path",
        type=str,
        help="path to the region directory to write output to",
    )

    args = parser.parse_args()

    fix_mapwriter_chunks(args.input_region_path, args.output_region_path)
