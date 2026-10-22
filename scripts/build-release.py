#!/usr/bin/env python3
"""Build checked, deterministic release assets without publishing anything."""
import argparse,gzip,hashlib,importlib.util,json,os,subprocess,sys,tarfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
package=module('release_package','check-package.py');manager=module('release_manager','manage-install.py')

def build(output):
    subprocess.run(['bash',str(ROOT/'scripts/check-release.sh')],cwd=ROOT,check=True,env={**os.environ,'DECK_AI_TEST_PYTHON':sys.executable})
    version,source=package.check();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    desktop=output/f'deck-ai-{version}-steamdeck.tar.gz';plugin=output/f'deck-ai-{version}-decky.zip'
    # All archive metadata is fixed, independent of the machine/user building it.
    with desktop.open('wb') as raw,gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=0) as gz,tarfile.open(fileobj=gz,mode='w') as tar:
        for rel in source:
            path=ROOT/rel;info=tar.gettarinfo(str(path),arcname=f'deck-ai-{version}/{rel}');info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
            info.mode=0o755 if os.access(path,os.X_OK) and path.suffix in ('.sh','') else 0o644
            with path.open('rb') as stream:tar.addfile(info,stream)
    runtime=[p for p in manager.source_files(ROOT) if p.parts[0]=='decky']
    with zipfile.ZipFile(plugin,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for rel in runtime:
            inner=Path('Deck AI')/Path(*rel.parts[1:]);info=zipfile.ZipInfo(str(inner),(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16;archive.writestr(info,(ROOT/rel).read_bytes())
    checksums=output/'SHA256SUMS.txt';checksums.write_text(''.join(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\n' for path in (desktop,plugin)))
    report={'version':version,'sourceFiles':len(source),'pluginFiles':len(runtime),'licenseSelected':(ROOT/'LICENSE').is_file(),'published':False,'checks':'compile, shell syntax, TypeScript, frontend logic, Python regression tests, package allowlist','manualChecksRequired':['Second Steam Deck/SteamOS installation','SteamOS suspend/resume during a task','Live optional providers with owner accounts','Human microphone accuracy in a running game']}
    (output/'BUILD-REPORT.json').write_text(json.dumps(report,indent=2)+'\n');return output

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=ROOT/'build/releases');args=parser.parse_args()
    try:print(build(args.output))
    except (OSError,ValueError,subprocess.CalledProcessError) as exc:parser.exit(1,str(exc)+'\n')
