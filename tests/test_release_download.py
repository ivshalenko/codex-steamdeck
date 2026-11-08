import base64,hashlib,importlib.util,io,json,ssl,tempfile,unittest,urllib.error
from pathlib import Path
from unittest.mock import patch
import updates

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
bootstrap=load('fallback_bootstrap','scripts/bootstrap.py')
builder=load('fallback_builder','scripts/build-release.py')
API=updates.API;VERSION='1.0.0-rc.21';NAME='asset.zip';URL=updates.WEB+'/releases/download/v'+VERSION+'/'+NAME
class Response(io.BytesIO):
 def __init__(self,data,url):super().__init__(data);self.headers={'Content-Length':str(len(data))};self.url=url
 def geturl(self):return self.url

class ReleaseDownloadTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.path=Path(self.temp.name)/NAME;self.data=b'verified release asset'
  self.asset={'id':123,'name':NAME,'size':len(self.data),'state':'uploaded','digest':'sha256:'+hashlib.sha256(self.data).hexdigest(),'url':API+'/releases/assets/123','browser_download_url':URL}
  self.release={'tag_name':'v'+VERSION,'draft':False,'published_at':'2026-11-08T00:00:00Z','assets':[self.asset]}
  self.requests=[]
 def network(self,request,*args,**kwargs):
  url=request.full_url;self.requests.append(request)
  if url==URL:raise urllib.error.HTTPError(url,504,'gateway timeout',None,None)
  if url==API+'/releases/tags/v'+VERSION:return Response(json.dumps(self.release).encode(),url)
  if url==self.asset['url']:return Response(self.data,url)
  raise AssertionError('Unexpected network request: '+url)
 def test_bootstrap_recovers_from_504_through_the_same_published_asset(self):
  with patch.object(bootstrap,'BASE',updates.WEB+'/releases/download/v'+VERSION+'/'),patch.object(updates.urllib.request,'urlopen',side_effect=self.network):
   bootstrap.download(NAME,self.path,1000)
  self.assertEqual(self.path.read_bytes(),self.data)
  self.assertEqual(len(self.requests),3)
  self.assertEqual(self.requests[-1].get_header('Accept'),'application/octet-stream')
  self.assertTrue(all(r.get_header('Authorization') is None for r in self.requests))
 def test_updater_recovers_with_its_original_checksum_guard(self):
  with patch.object(updates.urllib.request,'urlopen',side_effect=self.network):updates.download(URL,self.path,1000,hashlib.sha256(self.data).hexdigest())
  self.assertEqual(self.path.read_bytes(),self.data)
 def test_tampered_api_payload_cannot_replace_a_previous_file(self):
  self.path.write_bytes(b'previous');self.data=b'tampered payload'
  with patch.object(updates.urllib.request,'urlopen',side_effect=self.network),self.assertRaisesRegex(ValueError,'checksum'):
   updates.download(URL,self.path,1000)
  self.assertEqual(self.path.read_bytes(),b'previous')
  self.assertFalse(self.path.with_name(NAME+'.part').exists())
 def test_foreign_asset_endpoint_is_not_contacted(self):
  self.asset['url']='https://other.example/private'
  with patch.object(updates.urllib.request,'urlopen',side_effect=self.network),self.assertRaisesRegex(ValueError,'origin'):
   updates.download(URL,self.path,1000)
  self.assertEqual(len(self.requests),2);self.assertFalse(self.path.exists())
 def test_wrong_tag_draft_or_missing_digest_is_rejected(self):
  for kind in ('wrong-tag','draft','digest'):
   with self.subTest(kind=kind):
    self.release['tag_name']='v'+VERSION;self.release['draft']=False;self.asset['digest']='sha256:'+hashlib.sha256(self.data).hexdigest()
    if kind=='wrong-tag':self.release['tag_name']='v0.0.1'
    if kind=='draft':self.release['draft']=True
    if kind=='digest':self.asset.pop('digest')
    with patch.object(updates.urllib.request,'urlopen',side_effect=self.network),self.assertRaises(ValueError):updates.download(URL,self.path,1000)
    self.assertFalse(self.path.exists())
 def test_invalid_source_is_rejected_before_network_io(self):
  with patch.object(updates.urllib.request,'urlopen') as network,self.assertRaises(ValueError):updates.release_response('https://other.example/file')
  network.assert_not_called()
 def test_tls_verification_failure_does_not_take_another_route(self):
  error=urllib.error.URLError(ssl.SSLCertVerificationError('certificate rejected'))
  with patch.object(updates.urllib.request,'urlopen',side_effect=error) as network,self.assertRaises(urllib.error.URLError):updates.release_response(URL)
  self.assertEqual(network.call_count,1)
 def test_installer_embeds_downloader_without_needing_updates_module(self):
  text=builder.launcher_text(VERSION);encoded=text.split("base64.b64decode('",1)[1].split("')",1)[0]
  code=base64.b64decode(encoded).decode()
  self.assertIn('def release_response(',code);self.assertNotIn('from updates import release_response',code)
  scope={'__name__':'standalone_installer_test'};exec(compile(code,'standalone-installer','exec'),scope)
  self.assertEqual(scope['VERSION'],VERSION)
