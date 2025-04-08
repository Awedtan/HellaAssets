import os
import sys
import UnityPy

srcDir = sys.argv[1] if len(sys.argv) > 1 else '.'
expDir = sys.argv[2] if len(sys.argv) > 2 else 'exported'
batDir = f'{expDir}/battle'
buiDir = f'{expDir}/build'


def read_from_path_id(parent, list):
    try:
        return next(obj for obj in list if obj.read().path_id == parent['m_PathID']).read()
    except:
        return None


def process_spine(charATree, direction=None):
    skelA = read_from_path_id(charATree[direction]['skeleton'], monobehaviours) if direction else read_from_path_id(
        charATree['_skeleton'], monobehaviours)
    skelDA = read_from_path_id(skelA.read_typetree()['skeletonDataAsset'], monobehaviours)
    skelFile = read_from_path_id(skelDA.read_typetree()['skeletonJSON'], textassets)
    atlasA = read_from_path_id(skelDA.read_typetree()['atlasAssets'][0], monobehaviours)
    atlasFile = read_from_path_id(atlasA.read_typetree()['atlasFile'], textassets)
    mats = read_from_path_id(atlasA.read_typetree()['materials'][0], materials)
    alphaTex, mainTex = None, None
    for tex in mats.read_typetree()['m_SavedProperties']['m_TexEnvs']:
        if tex[0] == '_AlphaTex':
            alphaTex = read_from_path_id(tex[1]['m_Texture'], texture2ds)
        elif tex[0] == '_MainTex':
            mainTex = read_from_path_id(tex[1]['m_Texture'], texture2ds)
    return skelFile, atlasFile, alphaTex, mainTex


def save_assets(skelFile, atlasFile, alphaTex, mainTex, dirPath):
    os.makedirs(dirPath, exist_ok=True)
    open(f'{dirPath}/{skelFile.name}', 'wb').write(skelFile.script)
    open(f'{dirPath}/{atlasFile.name}', 'wb').write(atlasFile.script)
    if alphaTex is not None:
        alphaTex.image.save(f'{dirPath}/{alphaTex.name}.png')
    mainTex.image.save(f'{dirPath}/{mainTex.name}.png')


for file in os.listdir(srcDir):
    try:
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
            charA = mono.read()
            charATree = charA.read_typetree()

            # Battle spine
            if all(value in charATree.keys() for value in ['_animations', '_spineScale']):
                count += 1
                # Single spine (front only)
                if charATree.get('_skeleton'):
                    skelFile, atlasFile, alphaTex, mainTex = process_spine(charATree)
                    save_assets(skelFile, atlasFile, alphaTex, mainTex, f'{batDir}/{mainTex.name}/front')
                # Multiple spines (front + back + down)
                else:
                    for direction in ['_front', '_back', '_down']:
                        if charATree.get(direction):
                            skelFile, atlasFile, alphaTex, mainTex = process_spine(charATree, direction)
                            save_assets(skelFile, atlasFile, alphaTex, mainTex,
                                        f'{batDir}/{mainTex.name}/{direction.strip("_")}')
            # Build spine
            elif all(value in charATree.keys() for value in ['_centerTransform', '_shadowTransform']):
                skelFile, atlasFile, alphaTex, mainTex = process_spine(charATree)
                save_assets(skelFile, atlasFile, alphaTex, mainTex, f'{buiDir}/{mainTex.name}')

        if count == 0:
            print(f'Nothing was found for {file}')
    except Exception as e:
        print(f'Error for {file}: {e}')


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
