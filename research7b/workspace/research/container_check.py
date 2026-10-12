"""Run exact assessed resource flags and inspect effective cgroup/read-only limits."""
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evaluate import docker_command
image='sequential-research:1.0';command=docker_command(image)
idx=command.index(image);command[idx:idx]=['--entrypoint','python']
code='''import json, pathlib, os
out={}
for name in ("cpu.max","memory.max","pids.max"):
 p=pathlib.Path("/sys/fs/cgroup")/name
 out[name]=p.read_text().strip() if p.exists() else "unavailable"
try:
 pathlib.Path("/rootfs_probe").write_text("test")
 out["root_write_blocked"]=False
except OSError as e:
 out["root_write_blocked"]=True
 out["root_write_errno"]=e.errno
out["uid"]=os.getuid()
out["network_interfaces"]=[line.split(":")[0].strip() for line in pathlib.Path("/proc/net/dev").read_text().splitlines()[2:]]
out["up_network_interfaces"]=[name for name in out["network_interfaces"] if int((pathlib.Path("/sys/class/net")/name/"flags").read_text().strip(),16)&1]
out["app_files"]=sorted(os.listdir("/app"))
print(json.dumps(out))
'''
command+=['-c',code];p=subprocess.run(command,capture_output=True,text=True,timeout=10)
if p.returncode:raise RuntimeError(p.stderr)
out=json.loads(p.stdout);assert out['memory.max']=='1073741824';assert out['pids.max']=='64';quota,period=map(int,out['cpu.max'].split());assert quota/period==2;assert out['root_write_blocked'];assert out['uid']==65534;assert out['up_network_interfaces']==['lo']
Path('results/research/container_limits.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
