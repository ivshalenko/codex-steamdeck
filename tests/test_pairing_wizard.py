import importlib.util,tempfile,unittest
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'scripts/connect-deck.py';s=importlib.util.spec_from_file_location('pairing_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class PairingTests(unittest.TestCase):
 def test_existing_other_host_survives_and_repeat_pairing_is_idempotent(self):
  with tempfile.TemporaryDirectory() as directory:
   home=Path(directory);ssh=home/'.ssh';ssh.mkdir();config=ssh/'config';original='Host work\n    HostName work.example\n';config.write_text(original)
   key=ssh/'id_ed25519_deck_ai';key.write_text('existing private fixture');key.with_suffix('.pub').write_text('ssh-ed25519 PUBLIC_FIXTURE')
   self.assertEqual(m.configure('192.0.2.15',home),'ssh-ed25519 PUBLIC_FIXTURE');self.assertTrue(config.read_text().startswith(original))
   once=config.read_text();m.configure('192.0.2.15',home);self.assertEqual(config.read_text(),once)
   with self.assertRaises(ValueError):m.configure('192.0.2.16',home)
   self.assertEqual(config.read_text(),once)
 def test_command_instead_of_address_is_rejected_before_writing(self):
  with tempfile.TemporaryDirectory() as directory:
   home=Path(directory)
   with self.assertRaises(ValueError):m.configure('deck; touch unexpected',home)
   self.assertFalse((home/'.ssh').exists())
