import contextlib,hashlib,importlib.util,io,json,os,ssl,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
p=Path(__file__).resolve().parents[1]/'scripts/install-codex.py'
s=importlib.util.spec_from_file_location('codex_install_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Response(io.BytesIO):
 def geturl(self):return 'https://release-assets.githubusercontent.com/verified'

class InstallerTests(unittest.TestCase):
 def test_tampered_official_installer_is_rejected_before_execution(self):
  with tempfile.TemporaryDirectory() as d:
   source=Path(d)/'install.sh';source.write_bytes(b'changed installer')
   with patch.object(m,'VENDORED_INSTALLER',source),patch.object(m.subprocess,'run') as execute,patch.object(m.urllib.request,'urlopen') as network:
    with self.assertRaisesRegex(ValueError,'checksum'):m.install()
    execute.assert_not_called();network.assert_not_called()
 def test_vendored_official_installer_matches_reviewed_checksum_without_network(self):
  with tempfile.TemporaryDirectory() as d,patch.object(m.urllib.request,'urlopen',side_effect=urllib.error.HTTPError('https://api.github.com',500,'forced failure',None,None)) as network:
   target=Path(d)/'install.sh';m.download(target);self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),m.SHA256);network.assert_not_called()
 def test_official_metadata_request_uses_pins_even_when_api_returns_500_or_504(self):
  for status in (500,504):
   with self.subTest(status=status),patch.object(m.subprocess,'call',side_effect=AssertionError('No system curl request allowed')) as system,patch.object(m.urllib.request,'urlopen',side_effect=urllib.error.HTTPError(m.API,status,'forced failure',None,None)) as network,contextlib.redirect_stdout(io.StringIO()) as output:
    self.assertEqual(m.curl_proxy(['-fsSL',m.API+'/releases/tags/rust-v'+m.VERSION],'/usr/bin/curl'),0)
    data=json.loads(output.getvalue());self.assertEqual(data['tag_name'],'rust-v'+m.VERSION);self.assertTrue(any(a['name']=='codex-package_SHA256SUMS' for a in data['assets']));system.assert_not_called();network.assert_not_called()
 def test_unrelated_curl_requests_use_the_system_binary(self):
  arguments=['-fsSL','https://example.org']
  with patch.object(m.subprocess,'call',return_value=7) as system:self.assertEqual(m.curl_proxy(arguments,'/usr/bin/curl'),7)
  system.assert_called_once_with(['/usr/bin/curl',*arguments])
 def test_original_verified_installer_is_executed_with_temporary_adapter(self):
  def execute(command,**kwargs):
   self.assertEqual(command[0],'sh');self.assertEqual(command[-2:],['--release',m.VERSION]);self.assertEqual(hashlib.sha256(Path(command[1]).read_bytes()).hexdigest(),m.SHA256)
   adapter=Path(kwargs['env']['PATH'].split(':')[0])/'curl';self.assertTrue(adapter.stat().st_mode&0o100);self.assertIn('--curl',adapter.read_text())
  with patch.object(m.shutil,'which',return_value='/usr/bin/curl'),patch.object(m.subprocess,'run',side_effect=execute):m.install()

class CodexDownloadTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name);self.path=self.root/'package.tar.gz'
  self.data=b'official pinned package';self.name='codex-package-x86_64-unknown-linux-musl.tar.gz';self.url=m.PREFIX+self.name
  pins={self.name:(123,len(self.data),hashlib.sha256(self.data).hexdigest())};manager=patch.object(m,'PINS',pins);manager.start();self.addCleanup(manager.stop)
  manager=patch.dict(os.environ,{});manager.start();self.addCleanup(manager.stop);os.environ.pop('DECK_AI_CODEX_BUNDLE_DIR',None)
  self.requests=[];self.status=504
 def network(self,request,*args,**kwargs):
  self.requests.append(request);url=request.full_url
  if url==self.url:raise urllib.error.HTTPError(url,self.status,'forced failure',None,None)
  if url==m.API+'/releases/assets/123':return Response(self.data)
  raise AssertionError('No metadata API request expected: '+url)
 def test_500_and_504_recover_pinned_asset_without_a_metadata_query(self):
  for status in (500,504):
   self.status=status;self.requests=[]
   with self.subTest(status=status),patch.object(m.urllib.request,'urlopen',side_effect=self.network):m.download_asset(self.url,self.path)
   self.assertEqual(self.path.read_bytes(),self.data);self.assertEqual(len(self.requests),2);self.assertEqual(self.requests[-1].get_header('Accept'),'application/octet-stream');self.assertTrue(all(r.get_header('Authorization') is None for r in self.requests))
 def test_bad_payload_preserves_existing_file_and_cleans_temporary_files(self):
  for payload in (b'wrong size',b'X'*len(self.data),self.data+b'overflow'):
   with self.subTest(payload=payload):
    self.path.write_bytes(b'existing');original=self.data;self.data=payload
    with patch.object(m.urllib.request,'urlopen',side_effect=self.network),self.assertRaises(ValueError):m.download_asset(self.url,self.path)
    self.data=original;self.assertEqual(self.path.read_bytes(),b'existing');self.assertEqual(list(self.path.parent.iterdir()),[self.path])
 def test_foreign_repository_version_or_unexpected_asset_never_contacts_network(self):
  for url in ('https://other.example/file',self.url.replace('0.166.0','0.167.0'),m.PREFIX+'unexpected.sh'):
   with self.subTest(url=url),patch.object(m.urllib.request,'urlopen') as network,self.assertRaises(ValueError):m.download_asset(url,self.path)
   network.assert_not_called()
 def test_certificate_and_nontransient_http_errors_do_not_use_asset_api(self):
  for error in (urllib.error.URLError(ssl.SSLCertVerificationError('certificate')),urllib.error.HTTPError(self.url,403,'denied',None,None)):
   with self.subTest(error=error),patch.object(m.urllib.request,'urlopen',side_effect=error) as network,self.assertRaises(urllib.error.URLError):m.download_asset(self.url,self.path)
   self.assertEqual(network.call_count,1)
 def test_bundle_is_verified_and_used_without_any_network_request(self):
  folder=self.root/'bundle';folder.mkdir();(folder/self.name).write_bytes(self.data)
  with patch.dict(os.environ,{'DECK_AI_CODEX_BUNDLE_DIR':str(folder)}),patch.object(m.urllib.request,'urlopen',side_effect=AssertionError('Network blocked')) as network:m.download_asset(self.url,self.path)
  self.assertEqual(self.path.read_bytes(),self.data);network.assert_not_called()
 def test_missing_or_changed_bundled_files_never_fall_back_to_the_network(self):
  folder=self.root/'bundle';folder.mkdir()
  for content in (None,b'changed'):
   if content is not None:(folder/self.name).write_bytes(content)
   self.path.write_bytes(b'existing')
   with self.subTest(content=content),patch.dict(os.environ,{'DECK_AI_CODEX_BUNDLE_DIR':str(folder)}),patch.object(m.urllib.request,'urlopen') as network,self.assertRaises(ValueError):m.download_asset(self.url,self.path)
   network.assert_not_called();self.assertEqual(self.path.read_bytes(),b'existing')
