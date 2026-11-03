"""Official CLI owns auth choices and credentials; Deck AI must not filter them."""
import json, os, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import providers

AUTH_ENV={'ANTHROPIC_API_KEY':'fixture-api','ANTHROPIC_AUTH_TOKEN':'fixture-gateway',
          'CLAUDE_CODE_OAUTH_TOKEN':'fixture-oauth','CLAUDE_CODE_USE_BEDROCK':'1',
          'AWS_PROFILE':'fixture-profile','CLAUDE_CODE_USE_VERTEX':'1',
          'ANTHROPIC_VERTEX_PROJECT_ID':'fixture-project','CLAUDE_CODE_USE_FOUNDRY':'1'}

class ClaudeAuthTests(unittest.TestCase):
 def test_official_auth_methods_are_accepted_without_subscription_whitelist(self):
  for method in ('claude.ai','oauth_token','api_key','api_key_helper','third_party','future_native_method'):
   with self.subTest(method=method):
    payload=SimpleNamespace(returncode=0,stdout=json.dumps({'loggedIn':True,'authMethod':method,'email':'do-not-copy@example.invalid'}))
    with patch.object(providers.subprocess,'run',return_value=payload) as run:
     status=providers.claude_auth_status('/native/claude')
    self.assertEqual(status,{'loggedIn':True,'method':method})
    self.assertEqual(run.call_args.args[0],['/native/claude','auth','status'])

 def test_failure_and_invalid_status_never_look_ready(self):
  for code,payload in [(1,{'loggedIn':False,'authMethod':'none'}),(0,{'loggedIn':False}),(0,[]),(0,None)]:
   with self.subTest(payload=payload):
    with patch.object(providers.subprocess,'run',return_value=SimpleNamespace(returncode=code,stdout=json.dumps(payload))):
     self.assertFalse(providers.claude_auth_status('/native/claude')['loggedIn'])

 def test_auth_probe_and_request_keep_all_native_auth_environment(self):
  responses=[SimpleNamespace(returncode=0,stdout='{"loggedIn":true,"authMethod":"api_key"}'),
             SimpleNamespace(returncode=0,stdout='{"result":"answer"}',stderr='')]
  with patch.dict(os.environ,AUTH_ENV),patch.object(providers,'claude_code_available',return_value='/native/claude'),patch.object(providers.subprocess,'run',side_effect=responses) as run:
   self.assertEqual(providers.claude_code_reply('sonnet','chat','hello'),'answer')
  for call in run.call_args_list:
   for key,value in AUTH_ENV.items():self.assertEqual(call.kwargs['env'][key],value)
   self.assertFalse(any(value in str(call.args[0]) for value in AUTH_ENV.values()))

 def test_login_uses_unmodified_native_ui_and_preserves_credentials(self):
  for console in (False,True):
   with self.subTest(console=console),patch.dict(os.environ,AUTH_ENV),patch.object(providers,'claude_code_available',return_value='/native/claude'),patch.object(providers.shutil,'which',return_value='/usr/bin/konsole'),patch.object(providers.subprocess,'Popen') as spawn:
    providers.launch_claude_setup(console=console)
   expected=['/usr/bin/konsole','-e','/native/claude']+(['auth','login','--console'] if console else [])
   self.assertEqual(spawn.call_args.args[0],expected)
   for key,value in AUTH_ENV.items():self.assertEqual(spawn.call_args.kwargs['env'][key],value)

 def test_native_install_is_found_when_desktop_path_omits_local_bin(self):
  with tempfile.TemporaryDirectory() as directory:
   home=Path(directory);binary=home/'.local/bin/claude';binary.parent.mkdir(parents=True);binary.write_text('#!/bin/sh\nexit 0\n');binary.chmod(0o700)
   with patch.object(providers.shutil,'which',return_value=None),patch.object(providers.Path,'home',return_value=home):
    self.assertEqual(providers.claude_code_available(),str(binary))

 def test_cli_failure_does_not_publish_raw_credentials(self):
  for code,stdout in ((1,'failed'),(0,'{"is_error":true,"result":"fixture-api"}'),(0,'not JSON')):
   result=SimpleNamespace(returncode=code,stdout=stdout,stderr='fixture-api fixture-gateway fixture-oauth')
   with patch.object(providers,'claude_code_available',return_value='/native/claude'),patch.object(providers,'claude_auth_status',return_value={'loggedIn':True}),patch.object(providers.subprocess,'run',return_value=result):
    with self.assertRaises(providers.ProviderError) as caught:providers.claude_code_reply('sonnet','chat','hello')
   for secret in ('fixture-api','fixture-gateway','fixture-oauth'):self.assertNotIn(secret,str(caught.exception))

 def test_missing_terminal_does_not_claim_login_started(self):
  with patch.object(providers,'claude_code_available',return_value='/native/claude'),patch.object(providers.shutil,'which',return_value=None),patch.object(providers.subprocess,'Popen') as spawn:
   with self.assertRaisesRegex(providers.ProviderError,'--console'):providers.launch_claude_setup(console=True)
   spawn.assert_not_called()
