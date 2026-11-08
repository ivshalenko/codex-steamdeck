import hashlib,importlib.util,io,json,ssl,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
p=Path(__file__).resolve().parents[1]/'scripts/install-codex.py'
s=importlib.util.spec_from_file_location('codex_install_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class InstallerTests(unittest.TestCase):
 def test_tampered_official_download_is_rejected_before_execution(self):
  with tempfile.TemporaryDirectory() as d,patch.object(m.urllib.request,'urlopen',return_value=io.BytesIO(b'changed installer')),patch.object(m.subprocess,'run') as execute:
   with self.assertRaisesRegex(ValueError,'checksum'):m.install()
   execute.assert_not_called()

class Response(io.BytesIO):
 def geturl(self):return 'https://release-assets.githubusercontent.com/verified'

class CodexDownloadTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)/'package.tar.gz'
  self.data=b'official pinned package';self.name='codex-package-x86_64-unknown-linux-musl.tar.gz';self.url=m.PREFIX+self.name
  self.asset={'id':123,'name':self.name,'size':len(self.data),'state':'uploaded','digest':'sha256:'+hashlib.sha256(self.data).hexdigest(),'url':m.API+'/releases/assets/123','browser_download_url':self.url}
  self.release={'tag_name':'rust-v'+m.VERSION,'draft':False,'published_at':'2026-11-01','assets':[self.asset]};self.requests=[]
 def network(self,request,*args,**kwargs):
  self.requests.append(request);url=request.full_url
  if url==m.API+'/releases/tags/rust-v'+m.VERSION:return Response(json.dumps(self.release).encode())
  if url==self.url:raise urllib.error.HTTPError(url,504,'timeout',None,None)
  if url==self.asset['url']:return Response(self.data)
  raise AssertionError(url)
 def test_504_recovers_same_pinned_asset_without_credentials(self):
  with patch.object(m.urllib.request,'urlopen',side_effect=self.network):m.download_asset(self.url,self.path)
  self.assertEqual(self.path.read_bytes(),self.data);self.assertEqual(len(self.requests),3)
  self.assertEqual(self.requests[-1].get_header('Accept'),'application/octet-stream')
  self.assertTrue(all(r.get_header('Authorization') is None for r in self.requests))
 def test_bad_payload_preserves_existing_file_and_cleans_temporary_files(self):
  for payload in (b'wrong size',b'X'*len(self.data),self.data+b'overflow'):
   with self.subTest(payload=payload):
    self.path.write_bytes(b'existing');original=self.data;self.data=payload
    with patch.object(m.urllib.request,'urlopen',side_effect=self.network),self.assertRaises(ValueError):m.download_asset(self.url,self.path)
    self.data=original;self.assertEqual(self.path.read_bytes(),b'existing');self.assertEqual(list(self.path.parent.iterdir()),[self.path])
 def test_untrusted_asset_metadata_is_rejected_before_payload_request(self):
  for key,value in [('url','https://other.example/asset'),('size',True),('size',500_000_001),('digest',None),('digest',''),('browser_download_url','https://other.example/asset')]:
   with self.subTest(key=key,value=value):
    previous=self.asset.get(key);self.asset[key]=value;self.requests=[]
    with patch.object(m.urllib.request,'urlopen',side_effect=self.network),self.assertRaises(ValueError):m.download_asset(self.url,self.path)
    self.asset[key]=previous;self.assertEqual(len(self.requests),1);self.assertFalse(self.path.exists())
 def test_wrong_tag_draft_or_unpublished_release_is_rejected(self):
  for key,value in [('tag_name','rust-v0.0.1'),('draft',True),('published_at',None)]:
   with self.subTest(key=key):
    previous=self.release[key];self.release[key]=value
    with patch.object(m.urllib.request,'urlopen',side_effect=self.network),self.assertRaises(ValueError):m.download_asset(self.url,self.path)
    self.release[key]=previous;self.assertFalse(self.path.exists())
 def test_foreign_repository_version_or_unexpected_asset_never_contacts_network(self):
  for url in ('https://other.example/file',self.url.replace('0.166.0','0.167.0'),m.PREFIX+'unexpected.sh'):
   with self.subTest(url=url),patch.object(m.urllib.request,'urlopen') as network,self.assertRaises(ValueError):m.download_asset(url,self.path)
   network.assert_not_called()
 def test_certificate_and_nontransient_http_errors_do_not_use_asset_api(self):
  for error in (urllib.error.URLError(ssl.SSLCertVerificationError('certificate')),urllib.error.HTTPError(self.url,403,'denied',None,None)):
   def network(request,*args,**kwargs):
    if request.full_url==self.url:raise error
    return self.network(request,*args,**kwargs)
   self.requests=[]
   with self.subTest(error=error),patch.object(m.urllib.request,'urlopen',side_effect=network),self.assertRaises(urllib.error.URLError):m.download_asset(self.url,self.path)
   self.assertEqual(len(self.requests),1)
 def test_proxy_adapts_only_official_asset_download_invocation(self):
  args=['-fsSL',self.url,'-o',str(self.path)]
  with patch.object(m,'download_asset') as download,patch.object(m.subprocess,'call') as system:
   self.assertEqual(m.curl_proxy(args,'/usr/bin/curl'),0);download.assert_called_once_with(self.url,str(self.path));system.assert_not_called()
  other=['-fsSL',m.API+'/releases/tags/rust-v'+m.VERSION]
  with patch.object(m,'download_asset') as download,patch.object(m.subprocess,'call',return_value=0) as system:
   self.assertEqual(m.curl_proxy(other,'/usr/bin/curl'),0);system.assert_called_once_with(['/usr/bin/curl',*other]);download.assert_not_called()
 def test_original_checksum_pinned_script_is_executed_with_temporary_adapter(self):
  def execute(command,**kwargs):
   self.assertEqual(command[0],'sh');self.assertEqual(command[-2:],['--release',m.VERSION]);self.assertEqual(Path(command[1]).read_bytes(),b'original verified script')
   adapter=Path(kwargs['env']['PATH'].split(':')[0])/'curl';self.assertTrue(adapter.stat().st_mode&0o100);self.assertIn('--curl',adapter.read_text())
  with patch.object(m,'download',side_effect=lambda p:Path(p).write_bytes(b'original verified script')),patch.object(m.shutil,'which',return_value='/usr/bin/curl'),patch.object(m.subprocess,'run',side_effect=execute):m.install()
