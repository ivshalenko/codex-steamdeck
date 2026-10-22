import json
import io
import unittest
from unittest.mock import patch

import providers


class ProviderTests(unittest.TestCase):
    def test_deepseek_catalog_keeps_ids_and_costs(self):
        with patch.object(providers.urllib.request, 'urlopen') as open_url:
            open_url.return_value = io.BytesIO(json.dumps({'data':[
                {'id':'deepseek/deepseek-chat','name':'DeepSeek Chat','pricing':{'prompt':'0.0000002','completion':'0.0000008'}},
                {'id':'deepseek/free','name':'DeepSeek Free','pricing':{'prompt':'0','completion':'0'}},
            ]}).encode())
            models=providers.list_deepseek_models()
        self.assertEqual([m['id'] for m in models],['deepseek/deepseek-chat','deepseek/free'])
        self.assertAlmostEqual(models[0]['inputPrice'],0.0000002)
        self.assertEqual(models[1]['outputPrice'],0)

    def test_openrouter_error_does_not_echo_response_body(self):
        key='test-secret-placeholder'
        error=providers.urllib.error.HTTPError(providers.OPENROUTER_CHAT,401,'Unauthorized',{},None)
        with patch.object(providers,'read_openrouter_key',return_value=key), patch.object(providers.urllib.request,'urlopen',side_effect=error):
            with self.assertRaises(providers.ProviderError) as raised:
                providers.openrouter_reply('deepseek/test',[],'hello')
        self.assertNotIn(key,str(raised.exception))

    def test_openrouter_sends_selected_model_and_prior_chat(self):
        response=io.BytesIO(json.dumps({'choices':[{'message':{'content':'DeepSeek reply'}}]}).encode())
        with patch.object(providers,'read_openrouter_key',return_value='test-secret-placeholder'), patch.object(providers.urllib.request,'urlopen',return_value=response) as open_url:
            answer=providers.openrouter_reply('deepseek/example',[{'role':'user','content':'older prompt'}],'new prompt')
        request=open_url.call_args.args[0]
        payload=json.loads(request.data)
        self.assertEqual(answer,'DeepSeek reply')
        self.assertEqual(payload['model'],'deepseek/example')
        self.assertEqual(payload['messages'],[{'role':'user','content':'older prompt'},{'role':'user','content':'new prompt'}])
        self.assertEqual(request.get_header('Authorization'),'Bearer test-secret-placeholder')

    def test_claude_calls_cli_with_subscription_auth_and_safe_permission_mode(self):
        payload={'result':'answer'}
        result=type('Completed',(),{'returncode':0,'stdout':json.dumps(payload),'stderr':''})()
        with patch.object(providers,'claude_code_available',return_value='/opt/claude'), patch.object(providers,'claude_subscription_status',return_value={'loggedIn':True,'method':'claude.ai'}), patch.object(providers.subprocess,'run',return_value=result) as run:
            self.assertEqual(providers.claude_code_reply('sonnet','session-id','hello'), 'answer')
        args=run.call_args.args[0]
        self.assertIn('--resume',args)
        self.assertIn('--permission-prompts',args)
        self.assertIn('none',args)
        self.assertEqual(run.call_args.kwargs['env']['ANTHROPIC_API_KEY'],'')

    def test_openrouter_key_is_sent_to_secret_store_stdin_not_arguments(self):
        secret='test-secret-placeholder'
        result=type('Completed',(),{'returncode':0,'stdout':'','stderr':''})()
        with patch.object(providers.shutil,'which',return_value='/usr/bin/secret-tool'), patch.object(providers.subprocess,'run',return_value=result) as run:
            providers.save_openrouter_key(secret)
        self.assertNotIn(secret,run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs['input'],secret)

    def test_tokenharbor_key_is_stored_under_its_own_secret_account(self):
        secret='tokenharbor-test-placeholder'
        result=type('Completed',(),{'returncode':0,'stdout':'','stderr':''})()
        with patch.object(providers.shutil,'which',return_value='/usr/bin/secret-tool'), patch.object(providers.subprocess,'run',return_value=result) as run:
            providers.save_tokenharbor_key(secret)
        self.assertNotIn(secret,run.call_args.args[0])
        self.assertEqual(run.call_args.kwargs['input'],secret)
        self.assertEqual(run.call_args.args[0][-2:],['account','tokenharbor'])

    def test_tokenharbor_uses_the_free_model_endpoint(self):
        response=io.BytesIO(json.dumps({'choices':[{'message':{'content':'TokenHarbor reply'}}]}).encode())
        secret='tokenharbor-test-placeholder'
        with patch.object(providers,'read_tokenharbor_key',return_value=secret), patch.object(providers.urllib.request,'urlopen',return_value=response) as open_url:
            answer=providers.tokenharbor_reply(providers.TOKENHARBOR_MODEL,[{'role':'user','content':'older prompt'}],'new prompt')
        request=open_url.call_args.args[0]
        payload=json.loads(request.data)
        self.assertEqual(answer,'TokenHarbor reply')
        self.assertEqual(request.full_url,providers.TOKENHARBOR_CHAT)
        self.assertEqual(request.get_header('Authorization'),'Bearer '+secret)
        self.assertEqual(payload['model'],'deepseek-v4.1-flash:free')
        self.assertEqual(payload['messages'],[{'role':'user','content':'older prompt'},{'role':'user','content':'new prompt'}])

    def test_claude_console_api_auth_is_not_used_for_subscription_mode(self):
        with patch.object(providers,'claude_code_available',return_value='/opt/claude'), patch.object(providers,'claude_subscription_status',return_value={'loggedIn':False,'method':'api_key'}):
            with self.assertRaisesRegex(providers.ProviderError,'Pro/Max'):
                providers.claude_code_reply('sonnet','session-id','hello')


if __name__=='__main__':
    unittest.main()
