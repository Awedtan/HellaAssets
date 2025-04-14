import os
import sys
import UnityPy
from UnityPy.enums.BundleFile import CompressionFlags
from UnityPy.helpers import CompressionHelper
from lz4ak.Block import decompress_lz4ak

CompressionHelper.DECOMPRESSION_MAP[CompressionFlags.LZHAM] = decompress_lz4ak

srcDir = sys.argv[1] if len(sys.argv) > 1 else '.'
expDir = sys.argv[2] if len(sys.argv) > 2 else 'exported'
batDir = f'{expDir}/battle'
buiDir = f'{expDir}/build'

debug = False


def debug_print(str):
    if debug:
        print(str)


def read_from_path_id(parent, list):
    debug_print(f'Finding {parent["m_PathID"]} in {list[0]}')
    try:
        obj = next(obj for obj in list if obj.path_id and obj.path_id == parent['m_PathID'])

        debug_print(obj)
        debug_print(obj.read())
        debug_print(obj.read_typetree())

        return obj
    except:
        debug_print(f'Failed to find {parent["m_PathID"]} in {list[0]}')
        return None


def process_spine(charATree, direction=None):
    skelA = (read_from_path_id(charATree[direction]['skeleton'], monobehaviours) if direction else read_from_path_id(
        charATree['_skeleton'], monobehaviours)).read_typetree()
    skelDA = read_from_path_id(skelA['skeletonDataAsset'], monobehaviours).read_typetree()
    skelFile = read_from_path_id(skelDA['skeletonJSON'], textassets).read_typetree()
    atlasA = read_from_path_id(skelDA['atlasAssets'][0], monobehaviours).read_typetree()
    atlasFile = read_from_path_id(atlasA['atlasFile'], textassets).read_typetree()
    mats = read_from_path_id(atlasA['materials'][0], materials).read_typetree()
    alphaTex, mainTex = None, None
    for tex in mats['m_SavedProperties']['m_TexEnvs']:
        if tex[0] == '_AlphaTex':
            alphaTex = read_from_path_id(tex[1]['m_Texture'], texture2ds)
            alphaTex = alphaTex.read() if alphaTex else None
        elif tex[0] == '_MainTex':
            mainTex = read_from_path_id(tex[1]['m_Texture'], texture2ds).read()
    return skelFile, atlasFile, alphaTex, mainTex


def save_assets(skelFile, atlasFile, alphaTex, mainTex, dirPath):
    os.makedirs(dirPath, exist_ok=True)
    open(f'{dirPath}/{skelFile["m_Name"]}', 'wb').write(skelFile['m_Script'].encode('utf-16', 'surrogatepass'))
    open(f'{dirPath}/{atlasFile["m_Name"]}', 'wb').write(atlasFile['m_Script'].encode('utf-16', 'surrogatepass'))
    if alphaTex is not None:
        alphaTex.image.save(f'{dirPath}/{alphaTex.m_Name}.png')
    mainTex.image.save(f'{dirPath}/{mainTex.m_Name}.png')


for file in os.listdir(srcDir):
    try:
        print(file)
        if not file.endswith('.ab'):
            continue

        env = UnityPy.load(os.path.join(srcDir, file))
        materials = []
        monobehaviours = []
        textassets = []
        texture2ds = []

        for obj in env.objects:
            match obj.type.name:
                case 'Material':
                    materials.append(obj)
                case 'MonoBehaviour':
                    monobehaviours.append(obj)
                case 'TextAsset':
                    textassets.append(obj)
                case 'Texture2D':
                    texture2ds.append(obj)

        count = 0
        for mono in monobehaviours:
            charATree = mono.read_typetree()

            # Battle spine
            if all(value in charATree.keys() for value in ['_animations', '_spineScale']):
                count += 1
                # Single spine (front only)
                if charATree.get('_skeleton'):
                    skelFile, atlasFile, alphaTex, mainTex = process_spine(charATree)
                    save_assets(skelFile, atlasFile, alphaTex, mainTex, f'{batDir}/{mainTex.m_Name}/front')
                # Multiple spines (front + back + down)
                else:
                    for direction in ['_front', '_back', '_down']:
                        if charATree.get(direction):
                            skelFile, atlasFile, alphaTex, mainTex = process_spine(charATree, direction)
                            save_assets(skelFile, atlasFile, alphaTex, mainTex,
                                        f'{batDir}/{mainTex.m_Name}/{direction.strip("_")}')
            # Build spine
            elif all(value in charATree.keys() for value in ['_centerTransform', '_shadowTransform']):
                skelFile, atlasFile, alphaTex, mainTex = process_spine(charATree)
                save_assets(skelFile, atlasFile, alphaTex, mainTex, f'{buiDir}/{mainTex.m_Name}')

        if count == 0:
            print(f'Nothing was found for {file}')
    except Exception as e:
        print(f'Error for {file}: {e}')
        break


# Front only spine assets tree
#
#                                               SingleSpineAnimator
#                                                       |
#                                                       |
#                                               SkeletonAnimation
#                                                       |
#                                                       |
#                                               SkeletonDataAsset
#                                                 |           |
#                                                 |           |
#                                         AtlasAssets       SkeletonFile
#                                         |       |
#                                         |       |
#                                     AtlasFile   Materials
#                                                 |       |
#                                                 |       |
#                                             AlphaTex  MainTex

# Front + back spine assets tree
#
#                                               CharacterAnimator
#                                                |              |
#                                                |              |
#                           SkeletonAnimation (front)         SkeletonAnimation (back)
#                                       |                               |
#                                       |                               |
#                           SkeletonDataAsset (front)         SkeletonDataAsset (back)
#                           |               |                       |               |
#                           |               |                       |               |
#                   AtlasAssets       SkeletonFile              AtlasAssets       SkeletonFile
#                   |       |                                   |       |
#                   |       |                                   |       |
#               AtlasFile   Materials                       AtlasFile   Materials
#                           |       |                                   |       |
#                           |       |                                   |       |
#                       AlphaTex  MainTex                           AlphaTex    MainTex

# Front + back + down spine assets tree
#
#                                                               ThreeFaceAnimator
#                                        _______________________________|_______________________________
#                                       |                               |                               |
#                           SkeletonAnimation (front)         SkeletonAnimation (back)         SkeletonAnimation (down)
#                                       |                               |                               |
#                                       |                               |                               |
#                           SkeletonDataAsset (front)                  ...                             ...
#                           |               |
#                           |               |
#                   AtlasAssets       SkeletonFile
#                   |       |
#                   |       |
#               AtlasFile   Materials
#                           |       |
#                           |       |
#                       AlphaTex  MainTex
