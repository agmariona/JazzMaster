import constants
import os
import zipfile

in_path = os.fsencode(constants.PROJ_PATH + '/library/compressed_scores')
out_path = constants.PROJ_PATH + '/library/decompressed_scores'

for f in os.listdir(in_path):
    fname = os.fsdecode(f)
    if fname.split('.')[-1] != 'mxl':
        continue
    f_path = constants.PROJ_PATH + f'/library/scores/{fname}'
    with zipfile.ZipFile(f_path, 'r') as zf:
        rename = fname.split('.')[0] + '.xml'
        zf.extract('musicXML.xml', out_path)
        os.rename(out_path + '/musicXML.xml', out_path + f'/{rename}')
