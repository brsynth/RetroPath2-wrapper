from yaml   import safe_load as yaml_safe_load
from yaml   import YAMLError
from os     import path      as os_path
from shutil import copyfile

current_folder = os_path.dirname(os_path.realpath(__file__))

# input files
channels_file = current_folder+'/../../recipe/conda_channels.txt'
recipe_file   = current_folder+'/../../recipe/meta.yaml'
bld_cfg_file  = current_folder+'/../../recipe/conda_build_config.yaml'
# output files
env_file      = current_folder+'/test-environment.yml'
test_file     = current_folder+'/test.sh'

def parse_meta(filename):

    recipe = ''
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            # filter all non-YAML elements
            if not line.startswith('{%') and '{{' not in line:
                recipe += line
            line = f.readline()

    requirements = []
    tests = {}
    try:
        try: requirements += yaml_safe_load(recipe)['requirements']['host']
        except TypeError: pass
        try: requirements += yaml_safe_load(recipe)['requirements']['run']
        except TypeError: pass
        try: requirements += yaml_safe_load(recipe)['test']['requires']
        except TypeError: pass
        tests['commands']     = yaml_safe_load(recipe)['test']['commands']
        tests['source_files'] = yaml_safe_load(recipe)['test']['source_files']
    except YAMLError as exc:
        print(exc)

    return requirements, tests

def parse_build_config(filename):
    with open(filename, 'r') as f:
        f_configs = f.read()
        try: configs = yaml_safe_load(f_configs)
        except TypeError: pass
    return configs


def write_dependencies(filename, requirements):

    channels = open(channels_file, 'r').read().split()

    with open(filename, 'w') as f:
        f.write('channels:\n')
        for c in channels:
            f.write('  - '+c+'\n')
        f.write('dependencies:\n')
        for req in requirements:
            f.write('  - '+req+'\n')

def write_tests(filename, tests):
    with open(filename, 'w') as f:
        f.write('cd .. ; ')
        f.write(tests['commands'][0]+' ')
        for source_files in tests['source_files']:
            f.write(source_files)


requirements, tests = parse_meta(recipe_file)
write_dependencies(env_file, requirements)
write_tests(test_file, tests)

bld_cfgs = parse_build_config(bld_cfg_file)
for pkg in bld_cfgs:
    for ver in bld_cfgs[pkg]:
        env_file_cfg = env_file+'.'+pkg+str(ver)
        dep = pkg+' '+str(ver)
        print(dep)
